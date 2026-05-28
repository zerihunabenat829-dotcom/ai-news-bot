import os
import requests
import xml.etree.ElementTree as ET
from groq import Groq

# ኮንፊገሬሽን
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def fetch_fast_news(url, fallback_query, limit=3):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        root = ET.fromstring(response.content)
        items = []
        for item in root.findall('.//item')[:limit]:
            title = item.find('title').text
            if title:
                clean_title = title.split(" - ")[0].strip()
                items.append(clean_title)
        if items:
            return items
    except Exception as e:
        print(f"Fast fetch failed, using alternative for {fallback_query}: {e}")
    
    try:
        alt_url = f"https://news.google.com/rss/search?q={fallback_query}&hl=en-US&gl=US&ceid=US:en"
        res = requests.get(alt_url, headers=headers, timeout=10)
        root = ET.fromstring(res.content)
        return [item.find('title').text.split(" - ")[0].strip() for item in root.findall('.//item')[:limit]]
    except:
        return []

if __name__ == "__main__":
    print("Fetching fresh live data...")
    
    # 1. የዓለም ትኩስ ዜናዎችን ማምጣት
    world_news = fetch_fast_news("https://news.google.com/rss/sections/ certain/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YVNoR0FtdHZZbW9uWkd4U0FpQVAB?hl=en-US&gl=US&ceid=US:en", "breaking+world+news", limit=3)
    
    # 2. ትኩስ የስፖርት ዜናዎችን ማምጣት
    sports_news = fetch_fast_news("https://news.google.com/rss/search?q=football+news+transfers+scores&hl=en-US&gl=US&ceid=US:en", "football+sports+scores", limit=3)
    
    # 3. የሥራ ማስታወቂያዎችን ማምጣት
    job_vacancies = fetch_fast_news("https://news.google.com/rss/search?q=jobs+in+ethiopia+vacancies&hl=en-US&gl=US&ceid=US:en", "ethiopia+jobs", limit=3)
    
    # መረጃዎቹን ማጣመር
    combined_updates = ""
    if world_news:
        combined_updates += "🔴 BREAKING WORLD NEWS:\n" + "\n".join([f"- {n}" for n in world_news]) + "\n\n"
    if sports_news:
        combined_updates += "⚽ LIVE SPORTS & TRANSFERS:\n" + "\n".join([f"- {n}" for n in sports_news]) + "\n\n"
    if job_vacancies:
        combined_updates += "💼 LATEST JOB VACANCIES:\n" + "\n".join([f"- {j}" for j in job_vacancies])

    if not combined_updates:
        combined_updates = "🔄 Updating live feeds... Check back in a moment for fresh news!"

    # በ Groq AI አማካኝነት ዜናውን እጅግ ማራኪ ማድረግ
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system", 
                "content": "You are an elite, real-time breaking news bot. Format the provided headlines into an ultra-modern, clean, and highly professional Telegram channel post in English. Use bold headers, clean bullet points, and dynamic emojis for World News, Sports News, and Job Vacancies. Keep the headlines sharp and instant. Do not use Amharic."
            },
            {"role": "user", "content": combined_updates}
        ]
    )
    
    live_message = completion.choices[0].message.content
    
    # ወደ ቴሌግราม መላክ
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": live_message, "parse_mode": "Markdown"}
    requests.post(telegram_url, json=payload)
    print("Ultra-fast live update successfully posted to Telegram!")
