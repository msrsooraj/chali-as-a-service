from flask import Flask, render_template
import random
import os

app = Flask(__name__)

QUOTE_FILE = "chali.txt"
IMAGE_FOLDER = os.path.join("static", "images")
FEEDBACK_IMAGE_FOLDER = os.path.join("static", "images", "feedback")


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

    return f"/{folder}/{random.choice(images)}"


@app.route("/chali")
def chali():
    return render_template(
        "chali.html",
        quote=random_line(QUOTE_FILE),
        image_url=random_image(IMAGE_FOLDER),
        feedback_image=random_image(FEEDBACK_IMAGE_FOLDER)
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000, debug=True)
