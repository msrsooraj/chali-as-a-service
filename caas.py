from flask import Flask, jsonify
import random

app = Flask(__name__)

QUOTE_COUNT = sum(1 for _ in open("chali.txt", "r", encoding="utf-8"))


def get_random_quote():
    target = random.randint(0, QUOTE_COUNT - 1)

    with open("chali.txt", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == target:
                return line.strip()

@app.route("/chali", methods=["GET"])
def hello():
    return jsonify(chali=get_random_quote())

if __name__ == '__main__':
   app.run(debug=True)
