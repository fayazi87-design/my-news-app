import os
from flask import Flask, request, jsonify
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)

# تنظیم دقیق Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# استفاده از مدل قوی‌تر و پایدارتر
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/")
def home():
    ticker_symbol = request.args.get("ticker", "META").upper()
    try:
        stock = yf.Ticker(ticker_symbol)
        # استفاده از متد جدیدتر برای گرفتن اخبار
        news_list = stock.news[:3]
        
        if not news_list:
            return jsonify({"status": "No news found"})

        results = []
        for news in news_list:
            title = news.get('title', '')
            link = news.get('link', '')
            
            try:
                # دستور ترجمه بسیار دقیق
                prompt = f"Translate this financial headline to Persian. Keep company names in English. Headline: {title}"
                response = model.generate_content(prompt)
                translated_title = response.text.strip()
            except Exception as e:
                translated_title = f"AI Busy: {str(e)[:20]}"

            results.append({
                "ticker": ticker_symbol,
                "en": title,
                "fa": translated_title,
                "url": link
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()
