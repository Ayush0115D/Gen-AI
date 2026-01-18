from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

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
    "get_weather": get_weather
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

Available tool:
get_weather(city: string)
Example interaction:
User: What is the weather in Delhi?

Assistant:
{
  "step": "START",
  "content": "The user is asking for the current weather in Delhi."
}

Assistant:
{
  "step": "PLAN",
  "content": "I should call the weather tool to get the weather information."
}

Assistant:
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

Assistant:
{
  "step": "OUTPUT",
  "content": "The weather in Delhi is 🌫 with a temperature of 18°C."
}
"""

while True:
    message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    user_query = input("--> ")
    message_history.append({"role": "user", "content": user_query})

    for _ in range(10):
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            response_format={"type": "json_object"},
            messages=message_history,
            max_tokens=512
        )

        raw = response.choices[0].message.content
        parsed = json.loads(raw)
        message_history.append({"role": "assistant", "content": raw})

        step = parsed.get("step")

        if step == "START":
            print(parsed.get("content", ""))
            continue

        if step == "PLAN":
            print(parsed.get("content", ""))
            continue

        if step == "TOOL":
            tool = parsed.get("tool")
            inp = parsed.get("input")
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
            print(result)
            continue

        if step == "OUTPUT":
            print(parsed.get("content", ""))
            break
