import faiss, json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings

# Build FAISS vectorstore manually — no pickle, no deserialization flag needed
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_faiss_index():
    
    # Load FAISS index
    food_index = faiss.read_index("app/food_dataset/index.faiss")
    user_index = faiss.read_index("app/user_embeddings/index.faiss")
    
    # Load texts from JSON
    with open("app/food_dataset/index.json", encoding="utf-8") as f:
        food_texts = json.load(f)

    with open("app/user_embeddings/index.json", encoding="utf-8") as f:
        user_texts = json.load(f)
    
    # Convert to LangChain Documents
    food_docs = [Document(page_content=t) for t in food_texts]
    user_docs = [Document(page_content=t) for t in user_texts]

     # Build individual docstores
    food_store = InMemoryDocstore({f"food_{i}": d for i, d in enumerate(food_docs)})
    user_store = InMemoryDocstore({f"user_{i}": d for i, d in enumerate(user_docs)})

    # Index-to-ID mapping
    food_map = {i: f"food_{i}" for i in range(len(food_docs))}
    user_map = {i: f"user_{i}" for i in range(len(user_docs))}

    return (
        FAISS(embedding, food_index, food_store, food_map),
        FAISS(embedding, user_index, user_store, user_map),
    )

# Global variables to store FAISS indexes (loaded once at startup)
food_faiss = None
user_faiss = None

def initialize_faiss_indexes():
    global food_faiss, user_faiss
    food_faiss, user_faiss = load_faiss_index()

def get_food_faiss():
    """Get food FAISS index."""
    return food_faiss

def get_user_faiss():
    """Get user FAISS index."""
    return user_faiss    