import os
from flask import Flask, request, render_template_string
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# قالب گرافیکی صفحه
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اخبار هوشمند بورس</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #f0f2f5; padding: 20px; color: #333; }
        .container { max-width: 700px; margin: auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
        .news-item { border-bottom: 1px solid #eee; padding: 15px 0; transition: 0.3s; }
        .news-item:hover { background-color: #fdfdfd; }
        .en-title { color: #888; font-size: 0.85em; margin-bottom: 5px; font-style: italic; }
        .fa-title { color: #222; font-weight: bold; font-size: 1.1em; line-height: 1.6; }
        .link-btn { display: inline-block; margin-top: 8px; font-size: 0.8em; color: #1a73e8; text-decoration: none; border: 1px solid #1a73e8; padding: 2px 8px; border-radius: 5px; }
        .link-btn:hover { background: #1a73e8; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h2>آخرین اخبار: {{ ticker }}</h2>
        {% for item in news %}
        <div class="news-item">
            <div class="en-title">{{ item.en }}</div>
            <div class="fa-title">{{ item.fa }}</div>
            <a class="link-btn" href="{{ item.url }}" target="_blank">مطالعه منبع اصلی</a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    ticker = request.args.get("ticker", "NVDA").upper()
    try:
        stock = yf.Ticker(ticker)
        news_list = stock.news[:5]
        results = []
        for n in news_list:
            title = n.get('title', '')
            try:
                # دستور ترجمه اختصاصی
                res = model.generate_content(f"Translate this financial headline to Persian. Keep company names in English: {title}")
                fa = res.text.strip()
            except: fa = "خطا در ترجمه هوش مصنوعی"
            results.append({"en": title, "fa": fa, "url": n.get('link', '#')})
        return render_template_string(HTML_TEMPLATE, ticker=ticker, news=results)
    except Exception as e:
        return f"خطایی رخ داد: {str(e)}"

if __name__ == "__main__":
    app.run()
