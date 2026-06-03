import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class TruthLensRAG:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print(f"[RAG] Initializing with model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vector_store = None

    def index_text(self, text, metadata=None):
        """
        Chunks the text, embeds it, and adds it to the FAISS vector store.
        """
        if not text or len(text.strip()) < 10:
            return False
            
        print(f"[RAG] Indexing {len(text)} characters...")
        chunks = self.text_splitter.split_text(text)
        docs = [Document(page_content=chunk, metadata=metadata or {}) for chunk in chunks]
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(docs, self.embeddings)
        else:
            self.vector_store.add_documents(docs)
            
        print(f"[RAG] Added {len(docs)} chunks to index.")
        return True

    def query(self, query_text, k=4):
        """
        Retrieves the most relevant chunks for a given query.
        """
        if self.vector_store is None:
            return ""
            
        print(f"[RAG] Querying for: {query_text[:50]}...")
        results = self.vector_store.similarity_search_with_relevance_scores(query_text, k=k)
        
        # Filter by relevance score if possible (FAISS scores can be L2 distance or inner product)
        # Similarity search with relevance scores usually returns (doc, score)
        context_parts = []
        for doc, score in results:
            print(f"[RAG] Match found (score: {score:.4f}): {doc.page_content[:50]}...")
            context_parts.append(doc.page_content)
            
        return "\n\n".join(context_parts)

    def query_detailed(self, query_text, k=4):
        """
        Retrieves the most relevant chunks for a given query, returning raw chunks with score metadata.
        """
        if self.vector_store is None:
            return []
            
        print(f"[RAG] Detailed querying for: {query_text[:50]}...")
        # similarity_search_with_score returns (doc, L2_distance)
        results = self.vector_store.similarity_search_with_score(query_text, k=k)
        
        chunks = []
        for doc, score in results:
            # Map FAISS distance score to an intuitive similarity percentage
            # Cosine or L2 distance is typically around 0.5 to 1.5 in this embedding space.
            relevance_pct = max(0.0, min(100.0, (1.2 - score) * 100.0))
            if relevance_pct < 10.0 and score < 1.8:
                relevance_pct = max(10.0, (2.0 - score) * 30.0)
                
            chunks.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata or {},
                "score": round(relevance_pct, 1),
                "raw_score": float(score)
            })
            
        return chunks

    def reset(self):
        """
        Clears the vector store.
        """
        self.vector_store = None
        print("[RAG] Index reset.")
