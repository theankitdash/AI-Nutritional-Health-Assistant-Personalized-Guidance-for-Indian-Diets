from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import os
import aioredis
import bcrypt

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

# Pydantic models for personal details and user credentials
class PersonalDetails(BaseModel):
    name: str
    date_of_birth: str  # Change this to str for easier handling with Redis
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

# Endpoint to serve the HTML page at the root URL
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("static", "index.html")) as f:
        return f.read()

# Endpoint to serve the account settings page
@app.get("/account-settings", response_class=HTMLResponse)
async def read_account_settings():
    with open(os.path.join("static", "account-settings.html")) as f:
        return f.read()

# Endpoint to register user credentials
@app.post("/register/")
async def register_user(credentials: UserCredentials):
    hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Store hashed password in Redis
    await redis_client.hset(f"user:{credentials.email}", mapping={
        "password": hashed_password
    })
    return {"message": "User registered successfully."}

# Endpoint to login and store user details in Redis
@app.post("/login/")
async def login_user(credentials: UserCredentials):
    user_data = await redis_client.hgetall(f"user:{credentials.email}")

    if user_data and bcrypt.checkpw(credentials.password.encode('utf-8'), user_data[b'password']):
        # Store user session in Redis (optional, you can enhance this part)
        await redis_client.set(f"session:{credentials.email}", "active")
        return {"message": "User logged in successfully."}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

# Endpoint to add personal details (requires logged-in session)
@app.post("/personal-details/")
async def add_personal_details(details: PersonalDetails, email: str):
    # Store personal details in Redis
    await redis_client.hmset(f"personal_details:{email}", mapping={
        "name": details.name,
        "date_of_birth": details.date_of_birth,
        "gender": details.gender,
        "height": details.height,
        "weight": details.weight,
    })
    return {"message": "Personal details added successfully."}

# Endpoint to fetch personal details
@app.get("/personal-details/{email}")
async def get_personal_details(email: str):
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

# Endpoint to update personal details
@app.put("/personal-details/{email}")
async def update_personal_details(email: str, details: PersonalDetails):
    await redis_client.hmset(f"personal_details:{email}", mapping={
        "name": details.name,
        "date_of_birth": details.date_of_birth,
        "gender": details.gender,
        "height": details.height,
        "weight": details.weight,
    })
    return {"message": "Personal details updated successfully."}

@app.put("/update-password/")
async def update_password(password_data: PasswordUpdate, email: str):
    user_data = await redis_client.hgetall(f"user:{email}")

    if user_data and bcrypt.checkpw(password_data.current_password.encode('utf-8'), user_data[b'password']):
        hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await redis_client.hset(f"user:{email}", "password", hashed_new_password)
        return {"message": "Password updated successfully."}
    else:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

@app.post("/logout/")
async def logout_user(email: str):
    # Invalidate the user session (optional)
    await redis_client.delete(f"session:{email}")
    return {"message": "User logged out successfully."}

# Run the application using: uvicorn main:app --reload
