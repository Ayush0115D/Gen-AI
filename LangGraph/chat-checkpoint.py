from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
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
        "X-Title": "LangGraph Chatbot"        
    }
)
class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):#chatbot-node
    print("\n\ninside chatbot node",state)
    response = llm.invoke(state["messages"])
    return { "messages": [response] }


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot",END)

#START->Chatbot->END
graph=graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

DB_URI = "mongodb://localhost:27017"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)
    
    config = {
        "configurable": {
            "thread_id": "Ayush"
        }
    }
    
    for chunk in graph_with_checkpointer.stream(
        State({"messages": ["what i am learning"]}),
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()

# state = { messages: ["Hey there"] }
# node runs: chatbot(state: ["Hey There"]) -> ["Hi, This is a message from ChatBot Node"]
# state = { "messages": ["Hey there", "Hi, This is a message from ChatBot Node"]
#checkpointer(ayush)-Hey,my name is ayush dhakre