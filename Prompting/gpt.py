from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    # default_headers={
    #     "HTTP-Referer": "http://localhost",
    #     "X-Title": "GenAI Learning"
    # } 
)

response = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    max_tokens=512,   # ✅ REQUIRED
    messages=[
        {"role": "system", "content": "You are a expert in maths and ans only and only maths related questions."},
        {"role": "user", "content": "Hey, I am Piyush Garg! Nice to meet you"}
    ]
)

print(response.choices[0].message.content)
