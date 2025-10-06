import os, glob
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

RAG_INDEX_PATH = os.getenv("RAG_INDEX_PATH", "rag_index")

def _load_index():
    if not os.path.isdir(RAG_INDEX_PATH):
        return None
    try:
        embeddings = OpenAIEmbeddings()  # requiere OPENAI_API_KEY
        return FAISS.load_local(RAG_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return None

def rag_answer(query: str) -> str:
    """
    Si existe índice FAISS y OPENAI_API_KEY, retorna fragmentos relevantes.
    Esta función sólo concatena contextos; la orquestación LLM se hace en openai_service.
    """
    vs = _load_index()
    if vs is None:
        return ""
    docs: List[Document] = vs.similarity_search(query, k=3)
    parts = [d.page_content.strip() for d in docs if d.page_content]
    if not parts:
        return ""
    return "\n---\n".join(parts[:3])
