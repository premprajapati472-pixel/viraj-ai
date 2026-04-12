from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AIzaSyA17VrxwlYGHnHvFpGfknnbxXw0Xt_-Uxo")

model = genai.GenerativeModel("gemini-pro")

@app.route("/")
def home():
    return "Viraj AI Running 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data["message"]

    response = model.generate_content(user_msg)

    return jsonify({"reply": response.text})

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))