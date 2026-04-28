import os
from flask import Flask, request, render_template_string
import requests
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <title>اخبار فوری بورس</title>
    <style>
        body { font-family: Tahoma; background: #f4f7f6; padding: 20px; }
        .card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 600px; margin: 15px auto; text-align: right; border-right: 5px solid #1a73e8; }
        .en { color: #888; font-size: 0.8em; display: block; margin-bottom: 5px; }
        .fa { color: #2c3e50; font-weight: bold; font-size: 1.1em; }
        .link { color: #1a73e8; text-decoration: none; font-size: 0.8em; margin-top: 10px; display: inline-block; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">نتایج برای: {{ ticker }}</h2>
    {% for item in news %}
    <div class="card">
        <span class="en">{{ item.title }}</span>
        <span class="fa">{{ item.translated }}</span><br>
        <a class="link" href="{{ item.link }}" target="_blank">🔗 منبع خبر</a>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route("/")
def home():
    ticker = request.args.get("ticker", "NVDA").upper()
    try:
        # متد مستقیم برای گرفتن اخبار بدون کتابخانه yfinance
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
        data = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        raw_news = data.get('news', [])[:5]
        
        results = []
        for n in raw_news:
            title = n.get('title', '')
            try:
                # ترجمه Gemini
                res = model.generate_content(f"ترجمه فارسی کوتاه: {title}")
                translated = res.text.strip()
            except: translated = "خطا در ترجمه"
            results.append({"title": title, "translated": translated, "link": n.get('link', '#')})
        return render_template_string(HTML_TEMPLATE, ticker=ticker, news=results)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run()
