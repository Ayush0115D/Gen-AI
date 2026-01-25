import speech_recognition as sr
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ✅ OpenRouter API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ✅ OpenRouter Client (Gemini Model)
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    
)


def main():
    # ✅ System Prompt (Same Voice Agent Prompt)
    SYSTEM_PROMPT = """
    You're an expert voice agent.
    You are given the transcript of what user has said using voice.
    You need to output as if you are a voice agent and whatever you speak
    will be converted back to audio using AI and played back to user.
    """

    # ✅ Speech Recognizer
    r = sr.Recognizer()

    # ✅ Mic Input
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2

        print("Speak Something...")
        audio = r.listen(source)

        print("Processing Audio... (STT)")
        stt = r.recognize_google(audio)

        print("You Said:", stt)

    # ✅ Send Transcript to Gemini (via OpenRouter)
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
          max_tokens=200, 
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": stt}
        ]
    )

    # ✅ AI Reply Output
    reply = response.choices[0].message.content
    print("\nGemini Voice Agent Reply:\n", reply)


# ✅ Run Main
main()
