import os
from flask import Flask, request, jsonify
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)

# تنظیم دقیق جمینای
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def home():
    ticker_symbol = request.args.get("ticker", "AAPL").upper()
    try:
        stock = yf.Ticker(ticker_symbol)
        # متد جایگزین برای گرفتن خبر در صورت خالی بودن news
        news_list = stock.news[:3]
        
        if not news_list:
            return jsonify([{"fa": "خبری یافت نشد. تیکر را چک کنید."}])

        # استفاده از مدل با نام کوتاه و مستقیم
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        results = []
        for news in news_list:
            title = news.get('title', 'No Title')
            link = news.get('link', '#')
            
            try:
                prompt = f"ترجمه تخصصی بازار سرمایه به فارسی (نام شرکت ها انگلیسی بماند): {title}"
                response = model.generate_content(prompt)
                fa_title = response.text.strip()
            except:
                fa_title = "خطا در ترجمه هوش مصنوعی"

            results.append({
                "ticker": ticker_symbol,
                "en": title,
                "fa": fa_title,
                "url": link
            })
        return jsonify(results)
    except Exception as e:
        return jsonify([{"error": str(e)}])

if __name__ == "__main__":
    app.run()
