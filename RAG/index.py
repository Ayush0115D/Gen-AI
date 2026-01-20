from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

pdf_path=Path(__file__).parent/"nodejs.pdf"
#  Load this file in py program and extract text
loader=PyPDFLoader(file_path=pdf_path)
docs=loader.load()
print(docs[10].page_content)
# Split the docs into smaller chunks
text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=400)
chunks=text_splitter.split_documents(docs)
print(len(chunks))               
#vector embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1"
)
# Create Qdrant vector store
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning rag"
)
print("indexing of documents is completed")
