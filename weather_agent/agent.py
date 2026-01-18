from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
import time
from pydantic import BaseModel,Field
from typing import Optional
import subprocess
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

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
run_command(cmd: string):Takes a system linux command as string and executes command on user system and returns the output from that command.
example:
You are a general-purpose agent.
Tools may return weather info OR system command output.
Your OUTPUT must summarize the actual task result, not weather by default.
If writing files on Windows, use PowerShell here-strings with Out-File.
Never use echo for multiline content

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
class MyOutputFormat(BaseModel):
 step: str = Field(..., description="THE id of START, PLAN, TOOL, OBSERVE, OUTPUT etc")
 content:Optional[str] = Field(None, description="The Optional string content for the step")
 tool:Optional[str] = Field(None, description="The id of tool to call")
 input:Optional[str] = Field(None, description="The input params for the tool")

while True:
     message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
     user_query = input("--> ")
     message_history.append({"role": "user", "content": user_query})

     for _ in range(10):
        response = client.chat.completions.parse(
            model="google/gemini-2.5-flash",
            response_format=MyOutputFormat,
            messages=message_history,
            max_tokens=2048
        )

        raw = response.choices[0].message.content
       
        message_history.append({"role": "assistant", "content": raw})
        parsed_result = response.choices[0].message.parsed
        

        if parsed_result.step == "START":
            print ("🔥",parsed_result.content)
            continue

        if parsed_result.step == "PLAN":
            print("🛠️",parsed_result.content)
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
           
            break
