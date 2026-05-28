import os
import requests
from groq import Groq

# ኮንፊገሬሽን
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_crypto_news():
    test_url = "https://api.spaceflightnewsapi.net/v4/articles/?limit=1"
    try:
        response = requests.get(test_url).json()
        if response and 'results' in response:
            article = response['results'][0]
            return f"Title: {article['title']}\nSummary: {article['summary']}"
    except:
        return "No new international news found at this moment."

def translate_and_summarize(text):
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[
            {"role": "system", "content": "You are a professional news translator. Translate the given news into Amharic and make it short and engaging for Telegram."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    raw_news = get_crypto_news()
    if raw_news and "No new" not in raw_news:
        amharic_news = translate_and_summarize(raw_news)
        send_to_telegram(amharic_news)
        print("News sent successfully!")
    else:
        print("No new news found to process.")
