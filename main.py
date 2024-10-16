from fastapi import FastAPI, HTTPException, Cookie
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import aioredis
import bcrypt
from itsdangerous import URLSafeTimedSerializer

# Initialize FastAPI app
app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redis Database Connection
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
}

# Initialize Redis connection
redis_client = None
serializer = URLSafeTimedSerializer("your_secret_key")  # Replace with your secret key

# Pydantic models for personal details and user credentials
class PersonalDetails(BaseModel):
    name: str
    date_of_birth: str
    gender: str
    height: float
    weight: float

class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = await aioredis.from_url(f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}")

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("static/index.html")

@app.get("/account-settings", response_class=FileResponse)
async def read_account_settings():
    return FileResponse("static/account-settings.html")

@app.post("/register/")
async def register_user(credentials: UserCredentials):
    if len(credentials.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        await redis_client.hset(f"user:{credentials.email}", mapping={
            "password": hashed_password
        })
    except aioredis.RedisError as e:
        raise HTTPException(status_code=500, detail="Internal Redis error.")
    
    return {"message": "User registered successfully."}

@app.post("/login/")
async def login_user(credentials: UserCredentials):
    user_data = await redis_client.hgetall(f"user:{credentials.email}")

    if user_data and bcrypt.checkpw(credentials.password.encode('utf-8'), user_data[b'password']):
        session_id = serializer.dumps(credentials.email)  # Create a session ID
        await redis_client.set(f"session:{session_id}", credentials.email)
        response = JSONResponse(content={"message": "User logged in successfully."})
        response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True)  # Set the cookie
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

@app.post("/logout/")
async def logout_user(session_id: str = Cookie(None)):
    if session_id:
        await redis_client.delete(f"session:{session_id}")
    response = JSONResponse(content={"message": "User logged out successfully."})
    response.delete_cookie("session_id")  # Delete the cookie
    return response

@app.post("/personal-details/")
async def add_personal_details(details: PersonalDetails, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = serializer.loads(session_id)  # Get email from session ID
    await redis_client.hset(f"personal_details:{email}", mapping={
        "name": details.name,
        "date_of_birth": details.date_of_birth,
        "gender": details.gender,
        "height": details.height,
        "weight": details.weight,
    })
    return {"message": "Personal details added successfully."}

@app.get("/personal-details/")
async def get_personal_details(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = serializer.loads(session_id)  # Get email from session ID
    result = await redis_client.hgetall(f"personal_details:{email}")
    if result:
        return {
            "email": email,
            "name": result[b'name'].decode('utf-8'),
            "date_of_birth": result[b'date_of_birth'].decode('utf-8'),
            "gender": result[b'gender'].decode('utf-8'),
            "height": float(result[b'height']),
            "weight": float(result[b'weight']),
        }
    else:
        raise HTTPException(status_code=404, detail="User not found.")

@app.put("/personal-details/")
async def update_personal_details(details: PersonalDetails, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = serializer.loads(session_id)  # Get email from session ID
    await redis_client.hset(f"personal_details:{email}", mapping={
        "name": details.name,
        "date_of_birth": details.date_of_birth,
        "gender": details.gender,
        "height": details.height,
        "weight": details.weight,
    })
    return {"message": "Personal details updated successfully."}

@app.put("/update-password/")
async def update_password(password_data: PasswordUpdate, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = serializer.loads(session_id)  # Get email from session ID
    user_data = await redis_client.hgetall(f"user:{email}")

    if user_data and bcrypt.checkpw(password_data.current_password.encode('utf-8'), user_data[b'password']):
        hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await redis_client.hset(f"user:{email}", "password", hashed_new_password)
        return {"message": "Password updated successfully."}
    else:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

# Run the application using: uvicorn main:app --reload
