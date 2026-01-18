from dotenv import load_dotenv
from openai import OpenAI
import os
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=3"
    headers = {"User-Agent": "curl"}  # IMPORTANT
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException:
        return "Weather service unreachable"
    return "Something went wrong"

def main():
    user_query = input("> ").strip()
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{"role": "user", "content": user_query}],
    )
    print(f"🤖: {response.choices[0].message.content}")

print(get_weather("New Delhi"))
