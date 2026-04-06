from flask import Flask, jsonify, render_template, request, send_file, url_for
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/chali/static"
)

app.json.ensure_ascii = False

QUOTE_FILE = os.path.join(BASE_DIR, "chali.txt")
CONTACT_EMAIL = "msrsooraj@protonmail.com"  # TODO: Replace with your actual email address

IMAGE_FOLDER = os.path.join(app.static_folder, "images")
FEEDBACK_IMAGE_FOLDER = os.path.join(app.static_folder, "images", "feedback")


def random_line(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        jokes = f.read().split("\n---\n")
        return random.choice(jokes).strip()


def random_image(folder):
    valid_ext = (".jpg", ".jpeg", ".png", ".webp", ".gif")

    images = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith(valid_ext)
    ]

    filename = random.choice(images)

    # Convert filesystem path → URL
    relative_path = os.path.relpath(
        os.path.join(folder, filename),
        app.static_folder
    )

    return url_for("static", filename=relative_path)


@app.route("/")
def chali():
    return render_template(
        "chali.html",
        quote=random_line(QUOTE_FILE),
        image_url=random_image(IMAGE_FOLDER),
        feedback_image=random_image(FEEDBACK_IMAGE_FOLDER)
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/contact")
def contact():
    return render_template("contact.html", contact_email=CONTACT_EMAIL)


@app.route("/sw.js")
def sw_js():
    return send_file(os.path.join(BASE_DIR, "sw.js"), mimetype="application/javascript")


@app.route("/robots.txt")
def robots_txt():
    sitemap_url = request.url_root.rstrip("/") + "/sitemap.xml"
    content = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
    return content, 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    pages = ["", "about", "privacy", "terms", "contact"]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for page in pages:
        xml.append(f"  <url><loc>{base}/{page}</loc></url>")
    xml.append("</urlset>")
    return "\n".join(xml), 200, {"Content-Type": "application/xml"}


@app.route("/api")
def api():
    return jsonify({"chali": random_line(QUOTE_FILE)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
