from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

load_dotenv()
# OpenRouter client (CHAT)
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning rag",   
    embedding=embedding_model,
    validate_collection_config=False  #  
)
user_query = input("Ask something: ")

search_results = vector_db.similarity_search(user_query, k=3)


context = "\n\n\n".join(
    [
        f"Pagecontent: {result.page_content}\n"
        f"Page Number: {result.metadata.get('page_number', 'N/A')}\n"
        f"File Location: {result.metadata.get('source', 'Unknown')}"
        for result in search_results
    ]
)
SYSTEM_PROMPT=f"""
You are a helpful AI assistant who answere user queries based on the available context retrieved from the the pdf file along with page number and page_contents
You should only answeer the user based on following context and navigate the user to the page number to know more
{context}
"""

response = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ],
     max_tokens=512
)

print("🤖:", response.choices[0].message.content)
