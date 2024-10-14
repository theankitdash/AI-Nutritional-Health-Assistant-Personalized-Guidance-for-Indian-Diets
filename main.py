from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import os
from datetime import date
import mysql.connector
from mysql.connector import Error
import bcrypt
import aioredis
from contextlib import asynccontextmanager

# Initialize FastAPI app
app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# MySQL Database Connection Details
MYSQL_CONFIG = {
    "host": "localhost",         
    "user": "root",         
    "password": "Chiku@4009", 
    "database": "nutrify-health" 
}

# Pydantic models for personal details and user credentials
class PersonalDetails(BaseModel):
    name: str
    date_of_birth: date  
    gender: str
    height: float
    weight: float

class UserCredentials(BaseModel):
    email: EmailStr
    password: str

# Redis Client (for storing messages)
@asynccontextmanager
async def get_redis_client():
    redis_client = await aioredis.from_url("redis://localhost:6379", decode_responses=True)
    try:
        yield redis_client
    finally:
        await redis_client.close()
        print("Redis connection closed.")

# MySQL Connection Manager
@asynccontextmanager
async def get_mysql_connection():
    mysql_connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield mysql_connection
    finally:
        if mysql_connection.is_connected():
            mysql_connection.close()
            print("MySQL connection closed.")

# Function to create MySQL tables if they don't exist
async def create_tables(connection):
    try:
        cursor = connection.cursor()
        # Create credentials table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_credentials (
                email VARCHAR(100) PRIMARY KEY,
                password VARCHAR(255) NOT NULL
            )
        """)
        # Create personal details table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal_details (
                email VARCHAR(100) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                date_of_birth DATE NOT NULL,
                gender VARCHAR(10) NOT NULL,
                height FLOAT NOT NULL,
                weight FLOAT NOT NULL,
                FOREIGN KEY (email) REFERENCES user_credentials(email)
                ON DELETE CASCADE
            )
        """)
        connection.commit()
        print("Tables 'user_credentials' and 'personal_details' created successfully.")
    except Error as e:
        print(f"Error creating tables: {e}")

# Startup event
async def startup_event(app: FastAPI):
    async with get_mysql_connection() as mysql_connection:
        if mysql_connection.is_connected():
            print("Connected successfully to the database.")
            await create_tables(mysql_connection)

# Middleware for checking session (cookie-based)
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Exclude static files from session check
    if request.url.path.startswith("/static/"):
        response = await call_next(request)
        return response
    
    session_id = request.cookies.get("session_id")
    
    # Protect routes based on session, but allow public routes
    if request.url.path not in ["/", "/login", "/register/"] and not session_id:
        return HTMLResponse(content="Unauthorized", status_code=401)
    
    response = await call_next(request)
    return response

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

    async with get_mysql_connection() as mysql_connection:
        try:
            cursor = mysql_connection.cursor()
            cursor.execute("""
                INSERT INTO user_credentials (email, password)
                VALUES (%s, %s)
            """, (credentials.email, hashed_password))
            mysql_connection.commit()
            return {"message": "User registered successfully."}
        except Error as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

# Endpoint to login and set session
@app.post("/login/")
async def login_user(credentials: UserCredentials, response: Response):
    async with get_mysql_connection() as mysql_connection:
        try:
            cursor = mysql_connection.cursor()
            cursor.execute("SELECT password FROM user_credentials WHERE email = %s", (credentials.email,))
            result = cursor.fetchone()

            if result and bcrypt.checkpw(credentials.password.encode('utf-8'), result[0].encode('utf-8')):
                # Set a session cookie if login is successful
                response.set_cookie(key="session_id", value=credentials.email, httponly=True, max_age=1800)
                return {"message": "Login successful."}
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password.")
        except Error as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

# Endpoint to logout and clear session
@app.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="session_id")
    return {"message": "Logged out successfully."}

# Endpoint to add personal details (requires logged-in session)
@app.post("/personal-details/")
async def add_personal_details(request: Request, details: PersonalDetails):
    email = request.cookies.get("session_id")  # Get the email from the session cookie
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    async with get_mysql_connection() as mysql_connection:
        try:
            cursor = mysql_connection.cursor()
            cursor.execute("""
                INSERT INTO personal_details (email, name, date_of_birth, gender, height, weight)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, details.name, details.date_of_birth, details.gender, details.height, details.weight))
            mysql_connection.commit()
            return {"message": "Personal details added successfully."}
        except Error as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

# Endpoint to fetch personal details by session email (requires logged-in session)
@app.get("/personal-details/")
async def get_personal_details(request: Request):
    email = request.cookies.get("session_id")  # Get the email from the session cookie
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    async with get_mysql_connection() as mysql_connection:
        try:
            cursor = mysql_connection.cursor()
            cursor.execute("SELECT * FROM personal_details WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                return {
                    "email": result[0],
                    "name": result[1],
                    "date_of_birth": result[2],
                    "gender": result[3],
                    "height": result[4],
                    "weight": result[5],
                }
            else:
                raise HTTPException(status_code=404, detail="User not found.")
        except Error as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

# Endpoint to update personal details (requires logged-in session)
@app.put("/personal-details/")
async def update_personal_details(request: Request, details: PersonalDetails):
    email = request.cookies.get("session_id")  # Get the email from the session cookie
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    async with get_mysql_connection() as mysql_connection:
        try:
            cursor = mysql_connection.cursor()
            cursor.execute("""
                UPDATE personal_details
                SET name = %s, date_of_birth = %s, gender = %s, height = %s, weight = %s
                WHERE email = %s
            """, (details.name, details.date_of_birth, details.gender, details.height, details.weight, email))
            mysql_connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found.")
            return {"message": "Personal details updated successfully."}
        except Error as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

# Redis-based message handling
@app.post("/messages/")
async def send_message(request: Request, message: str):
    email = request.cookies.get("session_id")  # Get the email from the session cookie
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    async with get_redis_client() as redis_client:
        message_id = f"{email}:{len(await redis_client.keys(email + ':*'))}"  # Unique message ID based on count
        await redis_client.set(message_id, message)
        return {"message": "Message sent successfully.", "message_id": message_id}

# Endpoint to fetch messages for a user (requires logged-in session)
@app.get("/messages/")
async def fetch_messages(request: Request):
    email = request.cookies.get("session_id")  # Get the email from the session cookie
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    async with get_redis_client() as redis_client:
        keys = await redis_client.keys(email + ':*')  # Fetch message keys for the user
        messages = {key: await redis_client.get(key) for key in keys}
        return messages

#uvicorn main:app --reload