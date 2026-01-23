from mem0 import Memory
import os, requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}

def cut(t, n): 
    return t[:n]

mem = Memory.from_config({
    "llm": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "models/gemini-2.5-flash"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENROUTER_API_KEY,
            "openai_base_url": "https://openrouter.ai/api/v1",
            "model": "text-embedding-3-small"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "memo_1536"
        }
    }
})

USER_ID = "ayushdhakre"
chat_history = []

def extract_facts(text):
    r = requests.post(
        URL,
        headers=HEADERS,
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Extract long-term user facts worth remembering. One fact per line. If none, return NOTHING."
                },
                {"role": "user", "content": text}
            ],
            "max_tokens": 100
        },
        timeout=15
    ).json()

    if "choices" not in r:
        return []

    return [
        line.strip()
        for line in r["choices"][0]["message"]["content"].split("\n")
        if line.strip()
    ]

print("ready")

while True:
    q = input("> ")
    if q in ("exit", "quit"):
        break

    try:
        results = mem.search(user_id=USER_ID, query=q, limit=3)
    except:
        results = []

    ctx = []
    for r in results:
        if isinstance(r, dict) and r.get("memory"):
            ctx.append(r["memory"])

    if ctx:
        print("\nFound Memories:")
        for r in results:
            if isinstance(r, dict) and r.get("memory"):
                print(f"- ID: {r.get('id')}\n  Memory: {r.get('memory')}")

    messages = []

    if ctx:
        messages.append({
            "role": "system",
            "content": "Here is the context about the user:\n" + "\n".join(ctx)
        })

    messages.extend(chat_history[-6:])
    messages.append({"role": "user", "content": cut(q, 400)})

    res = requests.post(
        URL,
        headers=HEADERS,
        json={
            "model": "openai/gpt-4o-mini",
            "messages": messages,
            "max_tokens": 200
        },
        timeout=20
    ).json()

    if "choices" not in res:
        print(res)
        continue

    ans = res["choices"][0]["message"]["content"]
    print("\nAI:", ans)

    chat_history.append({"role": "user", "content": q})
    chat_history.append({"role": "assistant", "content": ans})

    facts = extract_facts(q)

    if facts:
        mem.add(
            user_id=USER_ID,
            messages=[{"role": "assistant", "content": f} for f in facts]
        )
        print("Memory has been saved...")
