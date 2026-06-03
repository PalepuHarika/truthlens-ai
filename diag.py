import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Python Path: {sys.path}")

try:
    import fastapi
    print("FastAPI: SUCCESS")
except ImportError:
    print("FastAPI: FAILED")

try:
    import sentence_transformers
    print("SentenceTransformers: SUCCESS")
except ImportError:
    print("SentenceTransformers: FAILED")

try:
    from langchain_core.documents import Document
    print("LangChain Core: SUCCESS")
except ImportError:
    print("LangChain Core: FAILED")

try:
    import faiss
    print("FAISS: SUCCESS")
except ImportError:
    print("FAISS: FAILED")
