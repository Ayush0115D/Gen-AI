from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
     base_url="https://openrouter.ai/api/v1"
    # default_headers={
    #     "HTTP-Referer": "http://localhost",
    #     "X-Title": "GenAI Learning"
    # } 
)

#zero-shot  prompting:Directly giving the instruction to the model without prior examples.
SYSTEM_PROMPT = "You are a expert in coding and only answer coding related questions.Your name is alexa.if user asks non coding related questions,you will politely refuse to answer."
response = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    max_tokens=512, 
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "how to tell a joke?"}
    ]
)

print(response.choices[0].message.content)
