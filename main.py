import os
from flask import Flask, request, render_template_string
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <title>اخبار بورس</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f4f9; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .news-item { border-bottom: 1px solid #eee; padding: 15px 0; }
        .news-item:last-child { border: none; }
        .en-title { color: #666; font-size: 0.9em; margin-bottom: 5px; }
        .fa-title { color: #333; font-weight: bold; font-size: 1.1em; }
        a { color: #007bff; text-decoration: none; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="container">
        <h2>آخرین اخبار برای {{ ticker }}</h2>
        {% for item in news %}
        <div class="news-item">
            <div class="en-title">{{ item.en }}</div>
            <div class="fa-title">{{ item.fa }}</div>
            <a href="{{ item.url }}" target="_blank">مشاهده منبع خبر</a>
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
                res = model.generate_content(f"Translate to Persian: {title}")
                fa = res.text.strip()
            except: fa = "خطا در ترجمه"
            results.append({"en": title, "fa": fa, "url": n.get('link', '#')})
        return render_template_string(HTML_TEMPLATE, ticker=ticker, news=results)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run()
