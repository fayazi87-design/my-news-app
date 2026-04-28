import os
from flask import Flask, request, jsonify
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)

# تنظیم ایمن جمینای
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@app.route("/")
def home():
    ticker_symbol = request.args.get("ticker", "META").upper()
    
    if not model:
        return "Error: GEMINI_API_KEY is not set in Render settings."

    try:
        # گرفتن اطلاعات تیکر
        stock = yf.Ticker(ticker_symbol)
        news_list = stock.news
        
        if not news_list:
            return f"No news found for ticker: {ticker_symbol}"

        results = []
        # فقط ۳ خبر اول رو برای سرعت بیشتر می‌گیریم
        for news in news_list[:3]:
            title = news.get('title', 'No Title')
            
            try:
                # ترجمه با رعایت احتیاط
                prompt = f"Translate this financial headline to Persian (keep company names in English): {title}"
                response = model.generate_content(prompt)
                translated_title = response.text.strip()
            except:
                translated_title = "Translation Error"

            results.append({
                "ticker": ticker_symbol,
                "original": title,
                "persian": translated_title,
                "link": news.get('link', '#')
            })
            
        return jsonify(results)
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app.run()
