from fastapi import FastAPI
from app.routers import auth, user_profile, chat
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
app.include_router(auth.router)
app.include_router(user_profile.router)
app.include_router(chat.router)

# Serve static files from /app/static
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount the static directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Run the application using: uvicorn app.main:app --reload 