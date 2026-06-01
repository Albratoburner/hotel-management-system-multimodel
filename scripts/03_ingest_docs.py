import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/data/documents'))
DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/vectorstore/chroma_db'))

def ingest_docs():
    print(f"Ingesting PDFs from {DOCS_DIR}...")
    
    # Check if docs dir exists
    if not os.path.exists(DOCS_DIR):
        print(f"Directory {DOCS_DIR} not found.")
        return

    documents = []
    # Load all PDFs
    for file_name in os.listdir(DOCS_DIR):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(DOCS_DIR, file_name)
            print(f"Loading {file_name}...")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
    
    if not documents:
        print("No PDF documents found to ingest.")
        return

    print(f"Loaded {len(documents)} document pages.")

    # Split documents with better chunking parameters for accuracy
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Created {len(splits)} text chunks.")

    # Ensure DB_DIR exists
    os.makedirs(DB_DIR, exist_ok=True)

    # Use a local embedding model (sentence-transformers)
    print("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Creating Chroma vectorstore...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print(f"Successfully ingested documents into ChromaDB at {DB_DIR}")

if __name__ == "__main__":
    ingest_docs()
