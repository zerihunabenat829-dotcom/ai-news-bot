
import os
import requests
import xml.etree.ElementTree as ET
from groq import Groq

# ኮንፊገሬሽን
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_news_from_feed(url, limit=4):
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        items = []
        for item in root.findall('.//item')[:limit]:
            title = item.find('title').text
            items.append(title)
        return items
    except Exception as e:
        print(f"Error fetching feed: {e}")
        return []

if __name__ == "__main__":
    # 1. የአጠቃላይ የዓለም ዜናዎችን ማምጣት
    world_url = "https://news.google.com/rss/search?q=world+news&hl=en-US&gl=US&ceid=US:en"
    world_news = get_news_from_feed(world_url, limit=3)
    
    # 2. የዋና ዋና ስፖርት ዜናዎችን እና ውጤቶችን ማምጣት
    sports_url = "https://news.google.com/rss/search?q=sports+news+live+scores&hl=en-US&gl=US&ceid=US:en"
    sports_news = get_news_from_feed(sports_url, limit=4)
    
    # መረጃዎቹን ማጣመር
    combined_text = "WORLD NEWS:\n" + " | ".join(world_news) + "\n\nSPORTS NEWS & SCORES:\n" + " | ".join(sports_news)
    
    # በ Groq AI አማካኝነት ዜናውን ማስዋብ
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional news and sports anchor. Take the given world news and sports headlines/scores and format them into a clean, highly engaging daily news update in English. Use separate sections for World News and Sports News. Use clear bullet points, soccer/sports emojis, and bold text for team names or key scores. Do not use Amharic."},
            {"role": "user", "content": combined_text}
        ]
    )
    
    final_message = completion.choices[0].message.content
    
    # ወደ ቴሌግራም መላክ
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": final_message, "parse_mode": "Markdown"}
    requests.post(telegram_url, json=payload)
    print("Combined World and Sports news sent successfully!")
