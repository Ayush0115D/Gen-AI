from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",  
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
       max_tokens=256, 
    default_headers={
        "HTTP-Referer": "http://localhost",   # required by OpenRouter
        "X-Title": "LangGraph Chatbot"         # required by OpenRouter
    }
)
class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):#chatbot-node
    print("\n\ninside chatbot node",state)
    response = llm.invoke(state["messages"])
    return { "messages": [response] }

def samplenode(state: State):
    print("\n\ninside samplenode node",state)
    return {"messages": ["Sample Message Appended"]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", chatbot)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)
#START->Chatbot->Samplenode->END
graph=graph_builder.compile()

updated_state = graph.invoke(State({"messages": ["Hi, My name is Ayush"]}))
print("\n\nupdated_state", updated_state)
# state = { messages: ["Hey there"] }
# node runs: chatbot(state: ["Hey There"]) -> ["Hi, This is a message from ChatBot Node"]
# state = { "messages": ["Hey there", "Hi, This is a message from ChatBot Node"]