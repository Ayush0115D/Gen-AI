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

#Few-shot prompting:Providing a few examples to the model before asking the actual question.
#it increases accuracy of the model.
SYSTEM_PROMPT = """You are a expert in coding and only answer coding related questions.Your name is alexa.if user asks non coding related questions,you will politely refuse to answer.
Rule-Strictly follow output in json format.
output Format:
{{
"code:"string or none,
iscorrect:"boolean"
}}
Examples:Can u explain a+b whole square?
A:SORRY, I can only answer coding related questions.
Q:How to reverse a linked list in python?
A:To reverse a linked list in python, you can use the following code:"""
response = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    max_tokens=512, 
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "how to tell a joke?"}
    ]
)

print(response.choices[0].message.content)
