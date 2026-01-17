import faiss, json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings

# Build FAISS vectorstore manually — no pickle, no deserialization flag needed
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_faiss_index():
    
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

    return FAISS(embedding, food_index, food_store, food_map)

# Global variable to store food FAISS index (loaded once at startup)
food_faiss = None

def initialize_faiss_indexes():
    """Initialize food FAISS index at startup."""
    global food_faiss
    food_faiss = load_faiss_index()

def get_food_faiss():
    """Get food FAISS index."""
    return food_faiss