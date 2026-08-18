from flask import Flask, jsonify, render_template, request, send_file, url_for, abort
import random
import os
import io
import base64
import binascii
import json
import secrets
import string
import qrcode
from qrcode.constants import ERROR_CORRECT_H

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


def all_jokes(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [j.strip() for j in f.read().split("\n---\n") if j.strip()]


def random_line(file_path):
    return random.choice(all_jokes(file_path))


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


@app.route("/jokes")
def jokes():
    return render_template("jokes.html", jokes=all_jokes(QUOTE_FILE))


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


@app.route("/tools")
def tools():
    return render_template("tools.html")


@app.route("/qr")
def qr():
    return render_template("qr.html")


@app.route("/password-generator")
def password_generator():
    return render_template("password_generator.html")


@app.route("/base64")
def base64_tool():
    return render_template("base64_tool.html")


@app.route("/json-formatter")
def json_formatter():
    return render_template("json_formatter.html")


@app.route("/qr/generate")
def qr_generate():
    data = request.args.get("data", "").strip()
    if not data:
        abort(400, "Missing 'data' parameter.")
    if len(data) > 2000:
        abort(400, "Data too long (max 2000 characters).")

    qr_code = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr_code.add_data(data)
    qr_code.make(fit=True)
    img = qr_code.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    as_attachment = request.args.get("dl") == "1"
    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=as_attachment,
        download_name="qr-code.png" if as_attachment else None,
    )


@app.errorhandler(400)
def handle_bad_request(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": e.description}), 400
    return e


@app.route("/api/password")
def api_password():
    try:
        length = int(request.args.get("length", 16))
    except ValueError:
        abort(400, "'length' must be an integer.")
    if not 4 <= length <= 128:
        abort(400, "'length' must be between 4 and 128.")

    def flag(name, default=True):
        val = request.args.get(name)
        return default if val is None else val.lower() not in ("false", "0", "")

    charset = ""
    if flag("uppercase"):
        charset += string.ascii_uppercase
    if flag("lowercase"):
        charset += string.ascii_lowercase
    if flag("numbers"):
        charset += string.digits
    if flag("symbols"):
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not charset:
        abort(400, "At least one character set must be enabled.")

    password = "".join(secrets.choice(charset) for _ in range(length))
    return jsonify({"password": password, "length": length})


@app.route("/api/base64/encode")
def api_base64_encode():
    text = request.args.get("text", "")
    if not text:
        abort(400, "Missing 'text' parameter.")
    if len(text) > 8000:
        abort(400, "Text too long (max 8000 characters). Use the browser tool for larger payloads.")
    result = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return jsonify({"result": result})


@app.route("/api/base64/decode")
def api_base64_decode():
    text = request.args.get("text", "")
    if not text:
        abort(400, "Missing 'text' parameter.")
    if len(text) > 8000:
        abort(400, "Text too long (max 8000 characters). Use the browser tool for larger payloads.")
    try:
        result = base64.b64decode(text, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        abort(400, "Invalid Base64 input.")
    return jsonify({"result": result})


def _validate_json_text(text):
    if not text:
        abort(400, "Missing 'json' parameter.")
    if len(text) > 8000:
        abort(400, "Input too long (max 8000 characters). Use the browser tool for larger payloads.")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        abort(400, f"Invalid JSON: {e}")


@app.route("/api/json/format")
def api_json_format():
    parsed = _validate_json_text(request.args.get("json", ""))
    return jsonify({"result": json.dumps(parsed, indent=2), "valid": True})


@app.route("/api/json/minify")
def api_json_minify():
    parsed = _validate_json_text(request.args.get("json", ""))
    return jsonify({"result": json.dumps(parsed, separators=(",", ":")), "valid": True})


@app.route("/sw.js")
def sw_js():
    return send_file(os.path.join(BASE_DIR, "sw.js"), mimetype="application/javascript")


@app.route("/ads.txt")
def ads_txt():
    content = "google.com, pub-7148483459385293, DIRECT, f08c47fec0942fa0\n"
    return content, 200, {"Content-Type": "text/plain"}


@app.route("/robots.txt")
def robots_txt():
    sitemap_url = request.url_root.rstrip("/") + "/sitemap.xml"
    content = f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n"
    return content, 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    pages = [
        "", "jokes", "about", "privacy", "terms", "contact", "tools",
        "qr", "password-generator", "base64", "json-formatter",
    ]
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
