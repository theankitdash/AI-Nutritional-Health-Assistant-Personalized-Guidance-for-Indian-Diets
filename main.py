from fastapi import FastAPI
from routers import auth, user_profile, chat
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(auth.router)
app.include_router(user_profile.router)
app.include_router(chat.router)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("static/index.html")

# Run the application using: uvicorn main:app --reload 