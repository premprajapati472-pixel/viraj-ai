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

def get_market_data(symbol):
    try:
        # 1. Pichle 3 mahine ka data (Candlestick ke liye 3 mahina clear dikhta hai)
        df = yf.download(symbol, period="3mo", interval="1d")
        if df.empty: return None
        
        # 2. Indicators Calculate karna
        df['EMA10'] = ta.ema(df['Close'], length=10)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # 3. Candlestick Chart Banana (Red/Green candles)
        buf = io.BytesIO()
        # mav=(10, 21) matlab do moving average lines dikhayega
        mpf.plot(df, type='candle', style='charles', 
                 mav=(10, 21), volume=True, 
                 title=f"\n{symbol} Analysis",
                 savefig=buf)
        
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return {"df": df.iloc[-1], "chart": img_base64}
    except Exception as e:
        print(f"Error in data: {e}")
        return None

@app.route('/ask', methods=['POST'])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").upper()
        
        # Normal chat handle karna
        if ".NS" not in msg and "^" not in msg:
            res = model.generate_content(msg)
            return jsonify({"reply": res.text, "chart": None})

        # Trading analysis handle karna
        info = get_market_data(msg)
        if not info:
            return jsonify({"reply": "Stock data nahi mila. Symbol check karein (e.g. SBIN.NS)", "chart": None})
            
        last = info['df']
        # AI ko indicators ka data dena
        prompt = f"""Tum ek expert trader ho. Stock: {msg} ka data ye hai:
        Price: {last['Close']:.2f}, RSI: {last['RSI']:.2f}, EMA10: {last['EMA10']:.2f}.
        Batao ki Buy karna hai ya Sell? Entry aur Stoploss bhi batao."""
        
        res = model.generate_content(prompt)
        return jsonify({"reply": res.text, "chart": info['chart']})
    except Exception as e:
        return jsonify({"reply": f"Server Error: {str(e)}", "chart": None}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)