#persona prompting means to make the model act like a specific person or character 
# by providing it with a detailed description of that person in the system prompt.
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

# Load environment variables
load_dotenv()

# OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = """you are ai persona  assistant name ayush 
                  you are acting on behalf of ayush,a tech enthusiast in mern stack and learning gen ai these days
                  example:
                  Question:HEY There?
                    Answer:Hello,whats up!
                    (100-150 examples)
"""
response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
          max_tokens=512,        
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "who are you"}
        ]
    )

print("Response:", response.choices[0].message.content)