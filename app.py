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

# Gemini Setup
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return "Viraj AI is Online and Ready!"

def get_market_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d")
        if df.empty: return None
        
        df['EMA10'] = ta.ema(df['Close'], length=10)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        buf = io.BytesIO()
        mpf.plot(df, type='candle', style='charles', 
                 mav=(10, 21), volume=True, 
                 title=f"\n{symbol} Analysis",
                 savefig=buf)
        
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return {"df": df.iloc[-1], "chart": img_base64}
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/ask', methods=['POST'])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").upper()
        
        if ".NS" not in msg and "^" not in msg:
            res = model.generate_content(msg)
            return jsonify({"reply": res.text, "chart": None})

        info = get_market_data(msg)
        if not info:
            return jsonify({"reply": "Stock data nahi mila. Symbol check karein (e.g. SBIN.NS)", "chart": None})
            
        last = info['df']
        prompt = f"Stock: {msg}, Price: {last['Close']:.2f}, RSI: {last['RSI']:.2f}. Give buy/sell advice."
        res = model.generate_content(prompt)
        return jsonify({"reply": res.text, "chart": info['chart']})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}", "chart": None}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)