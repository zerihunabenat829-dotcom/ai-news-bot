
import os
import requests
import xml.etree.ElementTree as ET
from groq import Groq

# ኮንፊገሬሽን
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_daily_world_news():
    # በየ24 ሰዓቱ የሚታደሰውን የጉግል ዜና (Google News RSS Feed) በቀጥታ መጠቀም
    rss_url = "https://news.google.com/rss/search?q=world+news&hl=en-US&gl=US&ceid=US:en"
    try:
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        
        # የመጀመሪያዎቹን 2 ወይም 3 ዋና ዋና ዜናዎች ሰብስቦ ለማምጣት
        news_items = []
        for item in root.findall('.//item')[:2]:
            title = item.find('title').text
            news_items.append(title)
            
        if news_items:
            return " | ".join(news_items)
    except Exception as e:
        print(f"Error fetching Google News: {e}")
    return None

def translate_and_summarize(text):
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional news anchor. Take the given world news headlines, summarize them clearly into a single daily update in Amharic, and format it beautifully for a Telegram channel using emojis."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    daily_news = get_daily_world_news()
    if daily_news:
        amharic_summary = translate_and_summarize(daily_news)
        send_to_telegram(amharic_summary)
        print("Daily news update sent successfully!")
    else:
        print("No news found for the last 24 hours.")
