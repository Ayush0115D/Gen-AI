from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
import time
import subprocess
import speech_recognition as sr
import pyttsx3
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Initialize text-to-speech engine
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
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError:
            print("❌ Microphone/Speech service error")
            return None

def run_command(cmd: str):
    completed = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return completed.stdout.strip() or completed.stderr.strip()

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=3"
    headers = {"User-Agent": "curl"}
    for _ in range(2):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200 and r.text.strip():
                return r.text.strip()
        except requests.exceptions.RequestException:
            time.sleep(1)
    return "Weather service unreachable"

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}

SYSTEM_PROMPT = """
You are an AI agent that reasons step by step and uses tools when required.

You must ALWAYS respond in JSON.
You must return EXACTLY ONE JSON object per response.
Do not add any extra text outside JSON.

Allowed steps:
START
PLAN
TOOL
OBSERVE
OUTPUT

Rules:
- Use START to understand the user query
- Use PLAN to decide next action
- Use TOOL only when calling a tool
- After TOOL, wait for OBSERVE
- Use OUTPUT for the final answer
- Do not skip steps

JSON format:
{
  "step": "START | PLAN | TOOL | OBSERVE | OUTPUT",
  "content": "string",
  "tool": "string",
  "input": "string",
  "output": "string"
}

Available tools:
get_weather(city: string)
run_command(cmd: string): Takes a system linux command as string and executes command on user system and returns the output from that command.

Example:
You are a general-purpose agent.
Tools may return weather info OR system command output.
Your OUTPUT must summarize the actual task result, not weather by default.
If writing files on Windows, use PowerShell here-strings with Out-File.
Never use echo for multiline content

A:
{
  "step": "START",
  "content": "The user is asking for the current weather in Delhi."
}

A:
{
  "step": "PLAN",
  "content": "I should call the weather tool to get the weather information."
}

A:
{
  "step": "TOOL",
  "tool": "get_weather",
  "input": "Delhi"
}

Tool response:
{
  "step": "OBSERVE",
  "tool": "get_weather",
  "output": "Delhi: 🌫 +18°C"
}

A:
{
  "step": "OUTPUT",
  "content": "The weather in Delhi is cloudy with a temperature of 18 degrees Celsius."
}
"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="THE id of START, PLAN, TOOL, OBSERVE, OUTPUT etc")
    content: Optional[str] = Field(None, description="The Optional string content for the step")
    tool: Optional[str] = Field(None, description="The id of tool to call")
    input: Optional[str] = Field(None, description="The input params for the tool")

def process_query(user_query, use_voice=False):
    """Process a single query through the agent"""
    message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    message_history.append({"role": "user", "content": user_query})

    for _ in range(10):
        response = client.chat.completions.parse(
            model="google/gemini-2.5-flash",
            response_format=MyOutputFormat,
            messages=message_history,
            max_tokens=178
        )

        raw = response.choices[0].message.content
        message_history.append({"role": "assistant", "content": raw})
        parsed_result = response.choices[0].message.parsed

        if parsed_result.step == "START":
            print("🔥", parsed_result.content)
            if use_voice:
                tts(parsed_result.content)
            continue

        if parsed_result.step == "PLAN":
            print("🛠️", parsed_result.content)
            if use_voice:
                tts(parsed_result.content)
            continue

        if parsed_result.step == "TOOL":
            tool = parsed_result.tool
            inp = parsed_result.input
            print(f"{tool}({inp})")

            result = available_tools[tool](inp)
            observe = {
                "step": "OBSERVE",
                "tool": tool,
                "output": result
            }
            message_history.append({
                "role": "developer",
                "content": json.dumps(observe)
            })
            message_history.append({
                "role": "system",
                "content": "You now have all observations. Produce the final OUTPUT."
            })
            print(result)
            continue

        if parsed_result.step == "OUTPUT":
            print("✅ Final Result:")
            print(parsed_result.content)
            if use_voice:
                tts(parsed_result.content)
            return parsed_result.content

def main():
    print("🚀 Voice-Enabled Weather Agent\n")
    print("Options:")
    print("1. Text mode (type queries)")
    print("2. Voice mode (speak queries)")
    
    mode = input("Select mode (1/2): ").strip()
    use_voice = mode == "2"

    if use_voice:
        print("\n🎙️ Voice Mode Activated")
        tts("Voice mode activated. Say your query.")
    
    while True:
        if use_voice:
            user_query = stt()
            if not user_query:
                continue
        else:
            user_query = input("--> ")
        
        if user_query.lower() in ["exit", "quit", "bye"]:
            if use_voice:
                tts("Goodbye!")
            print("Exiting...")
            break

        process_query(user_query, use_voice=use_voice)
        print()

if __name__ == "__main__":
    main()