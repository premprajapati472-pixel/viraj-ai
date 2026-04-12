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

app.run()