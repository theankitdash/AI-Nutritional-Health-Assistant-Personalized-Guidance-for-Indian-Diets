import faiss
import json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import numpy as np


class SentenceTransformerEmbeddings(Embeddings):
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()


# Initialize embedding model once
embedding_model = None

# In-memory caches (loaded once at startup, never re-read from disk)
food_metadata: List[dict] = []
food_texts_cache: List[str] = []


def get_embedding_model():
    """Get or initialize the embedding model."""
    global embedding_model
    if embedding_model is None:
        embedding_model = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
    return embedding_model


def load_faiss_index():
    """Load FAISS index for food data with metadata."""
    global food_metadata, food_texts_cache
    try:
        # Load FAISS index
        food_index = faiss.read_index("app/food_dataset/index.faiss")
        
        # Load texts from JSON — cached in memory for the lifetime of the process
        with open("app/food_dataset/index.json", encoding="utf-8") as f:
            food_texts_cache = json.load(f)
        
        # Load metadata
        try:
            with open("app/food_dataset/metadata.json", encoding="utf-8") as f:
                food_metadata = json.load(f)
        except FileNotFoundError:
            food_metadata = [{} for _ in food_texts_cache]
            print("Warning: metadata.json not found, using empty metadata.")
        
        # Convert to LangChain Documents with metadata
        food_docs = []
        for i, text in enumerate(food_texts_cache):
            meta = food_metadata[i] if i < len(food_metadata) else {}
            food_docs.append(Document(page_content=text, metadata=meta))

        # Build docstore
        food_store = InMemoryDocstore({f"food_{i}": d for i, d in enumerate(food_docs)})

        # Index-to-ID mapping
        food_map = {i: f"food_{i}" for i in range(len(food_docs))}

        # Get LangChain-compatible embedding model
        embeddings = get_embedding_model()

        return FAISS(embeddings, food_index, food_store, food_map)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None


def get_food_texts() -> List[str]:
    """Return the cached text list (loaded once at startup, never re-reads disk)."""
    return food_texts_cache


def get_food_metadata() -> List[dict]:
    """Return the metadata list."""
    return food_metadata


# Global variable to store food FAISS index (loaded once at startup)
food_faiss = None


def initialize_faiss_indexes():
    """Initialize food FAISS index at startup."""
    global food_faiss
    food_faiss = load_faiss_index()
    if food_faiss:
        print(f"FAISS food index loaded successfully! ({len(food_texts_cache)} documents cached in memory)")
    else:
        print("Failed to load FAISS food index!")


def get_food_faiss():
    """Get food FAISS index."""
    return food_faiss


def faiss_search_with_indices(query: str, k: int = 20) -> List[Tuple[int, Document]]:
    
    if food_faiss is None:
        return []
    
    try:
        embeddings = get_embedding_model()
        query_embedding = embeddings.embed_query(query)
        
        query_vec = np.array([query_embedding], dtype="float32")
        
        # Search the raw FAISS index directly
        raw_index = food_faiss.index
        distances, indices = raw_index.search(query_vec, k)
        
        results = []
        # Use cached lists — no disk I/O
        texts = food_texts_cache
        meta_list = food_metadata
        
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            idx = int(idx)
            meta = meta_list[idx] if idx < len(meta_list) else {}
            text = texts[idx] if idx < len(texts) else ""
            doc = Document(page_content=text, metadata=meta)
            results.append((idx, doc))
        
        return results
    except Exception as e:
        print(f"Error in faiss_search_with_indices: {e}")
        return []