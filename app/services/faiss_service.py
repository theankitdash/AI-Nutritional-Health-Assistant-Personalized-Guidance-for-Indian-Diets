import faiss
import json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List


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


def get_embedding_model():
    """Get or initialize the embedding model."""
    global embedding_model
    if embedding_model is None:
        embedding_model = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
    return embedding_model


def load_faiss_index():
    """Load FAISS index for food data."""
    try:
        # Load FAISS index for food data
        food_index = faiss.read_index("app/food_dataset/index.faiss")
        
        # Load texts from JSON
        with open("app/food_dataset/index.json", encoding="utf-8") as f:
            food_texts = json.load(f)
        
        # Convert to LangChain Documents
        food_docs = [Document(page_content=t) for t in food_texts]

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


# Global variable to store food FAISS index (loaded once at startup)
food_faiss = None


def initialize_faiss_indexes():
    """Initialize food FAISS index at startup."""
    global food_faiss
    food_faiss = load_faiss_index()
    if food_faiss:
        print("FAISS food index loaded successfully!")
    else:
        print("Failed to load FAISS food index!")


def get_food_faiss():
    """Get food FAISS index."""
    return food_faiss