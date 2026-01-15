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

# STRICT SYSTEM PROMPT (JSON ONLY)
SYSTEM_PROMPT = """
You are a STRICT JSON-only agent.

You MUST respond ONLY in valid JSON.
NO plain text.
NO explanations outside JSON.
NO markdown.

You work in steps: START, PLAN, OUTPUT.
Return ONLY ONE step per response.

JSON format (MANDATORY):
{
  "step": "START" | "PLAN" | "OUTPUT",
  "content": "string"
}

If you violate the JSON format, the program will fail.
"""

print("\n\n")

# Message history
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# User input
user_query = input("--> ")
message_history.append({"role": "user", "content": user_query})

# Safety limit to avoid infinite loops
MAX_STEPS = 6

for _ in range(MAX_STEPS):
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        response_format={"type": "json_object"},
        max_tokens=512,          # 🔑 CRITICAL FIX
        messages=message_history,
    )

    raw_result = response.choices[0].message.content

    # 🔒 SAFETY: Protect JSON parsing
    try:
        parsed_result = json.loads(raw_result)
    except json.JSONDecodeError:
        print("❌ Invalid JSON received from model:")
        print(raw_result)
        break

    # Save assistant response
    message_history.append({"role": "assistant", "content": raw_result})

    step = parsed_result.get("step")
    content = parsed_result.get("content")

    if step == "START":
        print("Processing your request:", content)

    elif step == "PLAN":
        print("Planning:", content)

    elif step == "OUTPUT":
        print("Final Output:\n", content)
        break

else:
    print("⚠️ Stopped: maximum steps reached")

# response = client.chat.completions.create(
#     model="google/gemini-2.5-flash",
#     response_format={"type": "json_object"},
#     max_tokens=512, 
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": "write a code to add n numbers in js"},
#     {
#             "role": "assistant",
#             "content": json.dumps({
#                 "step": "START",
#                 "content": "You want a JavaScript code to add 'n' numbers."
#             })
#         },
#         {
#             "role": "assistant",
#             "content": json.dumps({
#                 "step": "PLAN",
#                 "content": "I need to provide a JavaScript function that can add any number of arguments or elements in an array. I will use the rest parameter syntax (...) to accept multiple numbers and then use the reduce method to sum them up."
#             })
#         },
#         {
#             "role": "assistant",
#             "content": json.dumps({
#                 "step": "PLAN",
#                 "content": "I will define a JavaScript function that accepts an arbitrary number of arguments using the rest parameter. Inside the function, I will use the reduce array method to iterate over these arguments and calculate their sum. Finally, I will return the sum."
#             })
#         }
#     ]
# )

# print(response.choices[0].message.content)
# print(response.choices[0].message.content)