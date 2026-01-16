from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, user_profile, chat
from app.services.faiss_service import initialize_faiss_indexes

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

# Load FAISS indexes once at startup for better performance
@app.on_event("startup")
async def startup_event():
    """Load FAISS indexes at startup to avoid loading on every request"""
    print("Loading FAISS indexes...")
    initialize_faiss_indexes()
    print("FAISS indexes loaded successfully!")

app.include_router(auth.router)
app.include_router(user_profile.router)
app.include_router(chat.router)

# Run the application using: uvicorn app.main:app --reload 
#Frontend: cd frontend && npm run dev