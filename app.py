from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Viraj AI Running 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data["message"]

    reply = "Viraj AI: " + msg

    return jsonify({"reply": reply})

import os

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))