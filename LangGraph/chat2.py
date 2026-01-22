from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):
    print("chatbot node:", state)
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=256,
        messages=[
            {"role": "user", "content": state["user_query"]}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state

JUDGE_PROMPT = """
You are a strict evaluator.
User Question:
{question}
Chatbot Answer:
{answer}
Is the answer correct, complete, and helpful?
Reply with ONLY one word:
END or RETRY
"""

def judge_llm_answer(question: str, answer: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=17,
        messages=[
            {"role": "user", "content": JUDGE_PROMPT.format(
                question=question,
                answer=answer
            )}
        ]
    )
    return response.choices[0].message.content.strip().upper()

def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    print("\n \n evaluate_response node:", state)
    decision = judge_llm_answer(
        state["user_query"],
        state["llm_output"]
    )
    if decision == "END":
        return "endnode"
    return "chatbot_gemini"

def chatbot_gemini(state: State):
    print("\n chatbot_gemini:", state)
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        max_tokens=120,
        messages=[
            {"role": "user", "content": state["user_query"]}
        ]
    )
    state["llm_output"] = response.choices[0].message.content
    return state

def endnode(state: State):
    print("\n end node:", state)
    return state

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response)
graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

updated_state = graph.invoke(
    State({"user_query": "Hey, What is recursion in java?"})
)
print(updated_state)
