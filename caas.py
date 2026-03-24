from flask import Flask, jsonify, render_template, url_for
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

IMAGE_FOLDER = os.path.join(app.static_folder, "images")
FEEDBACK_IMAGE_FOLDER = os.path.join(app.static_folder, "images", "feedback")


def random_line(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return random.choice(f.readlines()).strip()


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


@app.route("/api")
def api():
    return jsonify({"chali": random_line(QUOTE_FILE)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
