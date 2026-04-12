import os
import yfinance as yf
import pandas_ta as ta
import mplfinance as mpf
import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Gemini API Key yahan set hai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Ye rasta check karne ke liye hai ki server zinda hai ya nahi
@app.route('/')
def index():
    return "Viraj AI Server is LIVE!"

@app.route('/ask', methods=['POST'])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").upper()
        
        # Agar stock symbol nahi hai toh normal chat
        if ".NS" not in msg and "^" not in msg:
            res = model.generate_content(msg)
            return jsonify({"reply": res.text, "chart": None})

        # Stock data logic
        df = yf.download(msg, period="3mo", interval="1d")
        if df.empty:
            return jsonify({"reply": "Symbol galat hai!", "chart": None})
            
        # Chart banana
        buf = io.BytesIO()
        mpf.plot(df, type='candle', style='charles', volume=True, savefig=buf)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        prompt = f"Stock: {msg}, Last Price: {df['Close'].iloc[-1]:.2f}. Advice?"
        res = model.generate_content(prompt)
        
        return jsonify({"reply": res.text, "chart": img_base64})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}", "chart": None}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)