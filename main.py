import os
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

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

# ترجمه ساده (Rule-based)
def simple_translate(text):
    text = text.lower()

    replacements = {
        "stock": "سهام",
        "stocks": "سهام",
        "market": "بازار",
        "ai": "هوش مصنوعی",
        "earnings": "سود",
        "revenue": "درآمد",
        "growth": "رشد",
        "buy": "خرید",
        "sell": "فروش",
        "analyst": "تحلیلگر",
        "wall street": "وال استریت",
        "nvidia": "انویدیا",
        "intel": "اینتل",
    }

    for en, fa in replacements.items():
        text = text.replace(en, fa)

    return text

@app.route("/")
def home():
    ticker = request.args.get("ticker", "NVDA").upper()

    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={ticker}"
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )

        data = response.json()
        raw_news = data.get('news', [])[:5]

        results = []

        for n in raw_news:
            title = n.get('title', '')
            translated = simple_translate(title)

            results.append({
                "title": title,
                "translated": translated,
                "link": n.get('link', '#')
            })

        return render_template_string(HTML_TEMPLATE, ticker=ticker, news=results)

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
