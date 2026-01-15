from dotenv import load_dotenv
from openai import OpenAI
import os
import json
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
     base_url="https://openrouter.ai/api/v1"
   
)
#Chain-of-Thought prompting: Encouraging the model to reason through the problem step-by-step before providing an answer.
SYSTEM_PROMPT = """You're an expert AI Assistant in resolving user queries using chain of thought.
You work on START, PLAN and OUTPUT steps.
You need to first PLAN what needs to be done. The PLAN can be multiple steps.
Once you think enough PLAN has been done, finally you can give an OUTPUT.
RULES:
- Strictly follow the given JSON output format
- Only run one step at a time.
- The sequence of steps is START (where user gives an input),
  PLAN (that can be multiple times), and finally OUTPUT
  (which is going to be displayed to the user).

Output JSON Format:
{
  "step": "START" | "PLAN" | "OUTPUT",
  "content": "string"
}

Example:
START: Hey, Can you solve 2 + 3 * 5 / 10
PLAN:{"step": "PLAN", "content": "First, I'll perform the multiplication (3 * 5 = 15). Then, I'll perform the division (15 / 10 = 1.5). Finally, I'll add the result to 2 (2 + 1.5 = 3.5)."}
"""
response = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    response_format={"type": "json_object"},
    max_tokens=512, 
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "write a code to add n numbers in js"},
    {
            "role": "assistant",
            "content": json.dumps({
                "step": "START",
                "content": "You want a JavaScript code to add 'n' numbers."
            })
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "step": "PLAN",
                "content": "I need to provide a JavaScript function that can add any number of arguments or elements in an array. I will use the rest parameter syntax (...) to accept multiple numbers and then use the reduce method to sum them up."
            })
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "step": "PLAN",
                "content": "I will define a JavaScript function that accepts an arbitrary number of arguments using the rest parameter. Inside the function, I will use the reduce array method to iterate over these arguments and calculate their sum. Finally, I will return the sum."
            })
        }
    ]
)

print(response.choices[0].message.content)
print(response.choices[0].message.content)