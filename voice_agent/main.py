import asyncio
import speech_recognition as sr
from openai import OpenAI
import os
from dotenv import load_dotenv
import pyttsx3

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

engine = pyttsx3.init()
engine.setProperty('rate', 150)

def tts(text):
    """Convert text to speech using pyttsx3"""
    engine.say(text)
    engine.runAndWait()

def stt():
    """Convert speech to text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2
        print("🎤 Listening...")
        try:
            audio = r.listen(source, timeout=10)
            stt_text = r.recognize_google(audio)
            print(f"✅ You: {stt_text}")
            return stt_text
        except:
            print("❌ Could not understand")
            return None

def get_response(user_input):
    """Get response from Gemini via OpenRouter"""
    SYSTEM_PROMPT = """You're a friendly voice agent. Keep responses short (1-2 sentences)."""
    
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        max_tokens=100,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

def main():
    print("🚀 Gemini Voice Agent\n")
    while True:
        user_text = stt()
        if not user_text:
            continue
        
        print("💭 Thinking...")
        reply = get_response(user_text)
        print(f"🤖 Agent: {reply}\n")
        tts(reply)
        
        if input("Continue? (yes/no): ").lower() != 'yes':
            break

if __name__ == "__main__":
    main()