from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
pdf_path=Path(__file__).parent/"nodejs.pdf"
#  Load this file in py program and extract text
loader=PyPDFLoader(file_path=pdf_path)
docs=loader.load()
print(docs[10].page_content)