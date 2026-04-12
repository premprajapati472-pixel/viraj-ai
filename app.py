import os
import yfinance as yf
import pandas_ta as ta
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Gemini Setup
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_market_analysis(symbol):
    try:
        # 1. Pichle 6 mahine ka data lena (Daily candles)
        df = yf.download(symbol, period="6mo", interval="1d")
        if df.empty: return None

        # 2. Indicators Calculate karna
        df['EMA10'] = ta.ema(df['Close'], length=10)
        df['EMA21'] = ta.ema(df['Close'], length=21)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        st_data = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
        df['ST'] = st_data['SUPERT_10_3.0']

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # 3. Buy/Sell Logic based on your rules
        close_price = float(last['Close'])
        ema10 = float(last['EMA10'])
        rsi_val = float(last['RSI'])
        st_val = float(last['ST'])

        # Signal Logic
        analysis = f"Current Price: {close_price:.2f}. "
        if close_price > ema10 and rsi_val > 60 and close_price > st_val:
            signal = "BUY SIGNAL (Strong Bullish)"
        elif close_price < ema10 and rsi_val < 40 and close_price < st_val:
            signal = "SELL SIGNAL (Strong Bearish)"
        else:
            signal = "WAIT/NEUTRAL (Conditions not fully met)"

        return {
            "price": close_price,
            "rsi": rsi_val,
            "ema10": ema10,
            "signal": signal,
            "raw_data": f"Price is {close_price}, EMA10 is {ema10}, RSI is {rsi_val}, Supertrend is {st_val}."
        }
    except Exception as e:
        return str(e)

@app.route('/ask', methods=['POST'])
def chat():
    try:
        data = request.json
        user_msg = data.get("message").upper() # Example: "RELIANCE.NS"

        # Market data nikalna
        market_info = get_market_analysis(user_msg)
        
        if not market_info or isinstance(market_info, str):
            # Agar stock symbol nahi mila toh normal AI talk
            response = model.generate_content(user_msg)
            return jsonify({"reply": response.text})

        # Gemini ko market data ke sath prompt bhejna
        prompt = f"""
        Tum ek expert Trading Assistant ho jiska naam Viraj AI hai. 
        User ne {user_msg} ka analysis manga hai. 
        Data: {market_info['raw_data']}. 
        Mera Signal: {market_info['signal']}.
        
        Is data ke basis par user ko short mein entry, exit aur target points suggest karo. 
        Candle sticks aur indicators ka logic samjhao.
        """
        
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)