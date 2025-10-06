"""
Crea un índice FAISS desde PDFs/TXT/MD en backend/docs
Requiere: OPENAI_API_KEY
"""
import os, glob
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
INDEX_DIR = Path(__file__).resolve().parent.parent / os.getenv("RAG_INDEX_PATH", "rag_index")

def load_docs():
    docs = []
    for p in DOCS_DIR.glob("**/*.txt"):
        docs.append(TextLoader(str(p), encoding="utf-8").load())
    for p in DOCS_DIR.glob("**/*.md"):
        docs.append(TextLoader(str(p), encoding="utf-8").load())
    for p in DOCS_DIR.glob("**/*.pdf"):
        loader = PyPDFLoader(str(p))
        docs.append(loader.load())
    # Flatten
    merged = []
    for d in docs:
        merged.extend(d)
    return merged

def main():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    raw_docs = load_docs()
    if not raw_docs:
        print(f"No se encontraron documentos en {DOCS_DIR}")
        return
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    splits = splitter.split_documents(raw_docs)
    embeddings = OpenAIEmbeddings()
    vs = FAISS.from_documents(splits, embeddings)
    vs.save_local(str(INDEX_DIR))
    print(f"Índice FAISS guardado en {INDEX_DIR}")

if __name__ == "__main__":
    main()
