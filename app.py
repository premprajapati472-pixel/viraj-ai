import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. Environment Variable se API Key lena
# Render ki settings mein 'GEMINI_API_KEY' naam se key zaroor save karein
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. Gemini Model Setup
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return "Viraj AI is Online and Ready!"

@app.route('/ask', methods=['POST'])
def chat():
    try:
        # User ka message lena
        data = request.json
        user_input = data.get("message")
        
        if not user_input:
            return jsonify({"error": "Empty message"}), 400

        # AI se jawab mangna
        response = model.generate_content(user_input)
        
        return jsonify({
            "status": "success",
            "reply": response.text
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render ke liye port aur host setup
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)