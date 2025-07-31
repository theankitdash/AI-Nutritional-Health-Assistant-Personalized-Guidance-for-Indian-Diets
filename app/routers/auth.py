from fastapi import APIRouter, HTTPException, Request, Cookie
from fastapi.responses import JSONResponse
from app.models import (UserCredentials, PasswordUpdate)
import uuid
import bcrypt 
from datetime import datetime, timezone, timedelta
from app.db_connect import connect_db
import asyncpg
import traceback

router = APIRouter()

@router.post("/register/")
async def register_user(credentials: UserCredentials):
    if len(credentials.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        conn = await connect_db()
        # Check if the email already exists in the credentials table
        user_exists = await conn.fetchrow("SELECT email FROM credentials WHERE email = $1", credentials.email)
        if user_exists:
            await conn.close()
            raise HTTPException(status_code=400, detail="Email already registered.")
        
        # Insert the new user into the credentials table
        await conn.execute(
            "INSERT INTO credentials (email, password) VALUES ($1, $2)",
            credentials.email, hashed_password
        )
        
        await conn.close()
        
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=500, detail="Internal PostgreSQL error.")
    
    return {"message": "User registered successfully."}

@router.post("/login/")
async def login_user(credentials: UserCredentials):
    try:
        # Connect to PostgreSQL
        conn = await connect_db()

        # Retrieve user data from the credentials table
        user_data = await conn.fetchrow("SELECT email, password FROM credentials WHERE email = $1", credentials.email)

        # Check if the user exists and the password is correct
        if user_data and bcrypt.checkpw(credentials.password.encode('utf-8'), user_data['password'].encode('utf-8')):
            # Generate a random session ID using uuid4
            session_id = str(uuid.uuid4())
            expiration_time = datetime.now(timezone.utc) + timedelta(hours=1)  # Session expires in 1 hour

            # Insert session data into the `sessions` table
            await conn.execute("""
                INSERT INTO sessions (session_id, email, expiration)
                VALUES ($1, $2, $3)
            """, session_id, credentials.email, expiration_time)

            # Close the connection
            await conn.close()

            # Create the response with a cookie containing the session ID
            response = JSONResponse(content={"message": "User logged in successfully."})
            response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, max_age=3600)  # Set the cookie
            return response
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    except asyncpg.PostgresError as e:
        print("Postgres Error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal PostgreSQL error.")
    
@router.get("/check-login/")
async def check_login(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        return {"isAuthenticated": False}

    if session_id:
        try:
            # Connect to PostgreSQL
            conn = await connect_db()

            # Retrieve session data from the sessions table
            session_data = await conn.fetchrow("SELECT email, expiration FROM sessions WHERE session_id = $1", session_id)

            # Check if the session exists and has not expired
            if session_data and session_data['expiration'] > datetime.now(timezone.utc):
                # Close the connection
                await conn.close()
                return {"isAuthenticated": True}

        except asyncpg.PostgresError:
            return {"isAuthenticated": False}
        
@router.post("/logout/")
async def logout_user(session_id: str = Cookie(None)):
    if session_id:
        try:
            conn = await connect_db()
            await conn.execute("DELETE FROM sessions WHERE session_id = $1", session_id)
            await conn.close()
        except Exception:
            pass  # Optionally log this

    response = JSONResponse(content={"message": "User logged out successfully."})
    response.delete_cookie("session_id")
    return response

async def validate_session(session_id: str):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    try:
        conn = await connect_db()
        session_data = await conn.fetchrow(
            "SELECT email, expiration FROM sessions WHERE session_id = $1", session_id
        )
        await conn.close()

        if not session_data or session_data["expiration"] < datetime.now(timezone.utc):
            raise HTTPException(status_code=403, detail="Invalid or expired session.")

        return session_data["email"]

    except Exception:
        raise HTTPException(status_code=500, detail="Session validation failed.")        
    
@router.put("/update-password/")
async def update_password(password_data: PasswordUpdate, session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        conn = await connect_db()
        
        # Get stored hashed password
        user_record = await conn.fetchrow(
            "SELECT password FROM credentials WHERE email = $1", email
        )

        if not user_record:
            await conn.close()
            raise HTTPException(status_code=404, detail="User not found.")

        # Validate current password
        stored_hashed_password = user_record["password"]
        if not bcrypt.checkpw(password_data.current_password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            await conn.close()
            raise HTTPException(status_code=401, detail="Current password is incorrect.")

        # Hash new password
        hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update in DB
        await conn.execute(
            "UPDATE credentials SET password = $1 WHERE email = $2",
            hashed_new_password, email
        )

        await conn.close()
        return {"message": "Password updated successfully."}

    except Exception:
        raise HTTPException(status_code=500, detail="Error updating password.")   