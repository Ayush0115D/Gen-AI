from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

#VectorEmbedding
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "rag-queue-worker",
    },
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",   
    embedding=embedding_model,
)
def process_query(user_query: str):
    print("Searching chunks", user_query)

    search_results = vector_db.similarity_search(user_query)

    context = "\n\n".join(
        [
            f"Pagecontent: {result.page_content}\n"
            f"Page Number: {result.metadata['page_number']}\n"
            f"File Location: {result.metadata['source']}"
            for result in search_results
        ]
    )

    SYSTEM_PROMPT = (
        "You are a helpful AI assistant who answers user queries based on the available context "
        "retrieved from the pdf file along with page number. "
        "You should only answeer the user based on following context and navigate the user to the page number to know more\n\n"
        f"{context}"
    )

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]
    )

    print("🤖:", response.choices[0].message.content)
    return response.choices[0].message.content
