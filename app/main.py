from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, user_profile, chat
from app.db_connect import init_db
from app.services.faiss_service import initialize_faiss_indexes
from app.services.bm25_service import initialize_bm25
from app.services.hybrid_retriever import initialize_reranker

app = FastAPI()

# CORS middleware configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # Allow cookies to be sent
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load all indexes and models once at startup
@app.on_event("startup")
async def startup_event():
    """Initialize DB pool, FAISS index, BM25 index, and reranker at startup."""
    print("Initializing database connection pool...")
    await init_db()

    print("Loading FAISS food index...")
    initialize_faiss_indexes()
    
    print("Loading BM25 index...")
    initialize_bm25()
    
    print("Loading Cross-Encoder reranker...")
    initialize_reranker()
    
    print("All indexes and models loaded successfully!")

app.include_router(auth.router)
app.include_router(user_profile.router)
app.include_router(chat.router)

# Run the application using: uvicorn app.main:app --reload 
#Frontend: cd frontend && npm run dev 