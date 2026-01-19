from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
pdf_path=Path(__file__).parent/"nodejs.pdf"
#  Load this file in py program and extract text
loader=PyPDFLoader(file_path=pdf_path)
docs=loader.load()
print(docs[10].page_content)
# Split the docs into smaller chunks
text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=400)
chunks=text_splitter.split_documents(docs)
print(len(chunks))               