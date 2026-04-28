import os
from flask import Flask, request, jsonify
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)

# تنظیم دقیق و کامل مدل
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# استفاده از نام کامل مدل برای جلوگیری از خطای 404
model = genai.GenerativeModel('models/gemini-1.5-flash')

@app.route("/")
def home():
    ticker_symbol = request.args.get("ticker", "AAPL").upper()
    try:
        # گرفتن اخبار
        stock = yf.Ticker(ticker_symbol)
        news_list = stock.news
        
        if not news_list or len(news_list) == 0:
            return jsonify([{"ticker": ticker_symbol, "en": "No news found right now", "fa": "در حال حاضر خبری یافت نشد", "url": ""}])

        results = []
        for news in news_list[:3]:
            title = news.get('title', 'No title')
            link = news.get('link', '#')
            
            try:
                # ترجمه
                prompt = f"Translate this financial news title to Persian: {title}"
                response = model.generate_content(prompt)
                # گرفتن متن خالص از پاسخ هوش مصنوعی
                translated_title = response.text.strip()
            except Exception as ai_err:
                translated_title = f"Translation pending... ({str(ai_err)[:10]})"

            results.append({
                "ticker": ticker_symbol,
                "en": title,
                "fa": translated_title,
                "url": link
            })
        return jsonify(results)
    except Exception as e:
        return jsonify([{"error": str(e)}])

if __name__ == "__main__":
    app.run()
