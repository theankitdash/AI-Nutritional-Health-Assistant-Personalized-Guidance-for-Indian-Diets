from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import JSONResponse
from app.models import (UserCredentials, PasswordUpdate)
import uuid
import bcrypt 
from datetime import datetime, timezone, timedelta
from app.db_connect import connect_db
import asyncpg
import traceback
import re
from collections import defaultdict
import time

router = APIRouter()

SESSION_DURATION_HOURS = 1

login_attempts = defaultdict(list)
RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 300  # 5 minutes

def is_rate_limited(email: str) -> bool:
    """Check if email has exceeded login attempts in the time window"""
    now = time.time()
    # Remove old attempts outside the window
    login_attempts[email] = [ts for ts in login_attempts[email] if now - ts < RATE_LIMIT_WINDOW]
    
    if len(login_attempts[email]) >= RATE_LIMIT_ATTEMPTS:
        return True
    
    return False

def record_login_attempt(email: str):
    """Record a login attempt"""
    login_attempts[email].append(time.time())

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
    if " " in password:
        raise HTTPException(status_code=400, detail="Password must not contain spaces.")
    return True

async def get_session_email(session_id: str):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    conn = None
    try:
        conn = await connect_db()
        session_data = await conn.fetchrow(
            "SELECT email, expiration FROM sessions WHERE session_id = $1", session_id
        )
        now = datetime.now(timezone.utc)

        if not session_data:
            raise HTTPException(status_code=403, detail="Session invalid.")

        if session_data["expiration"] < now:
            # Delete expired session
            await conn.execute("DELETE FROM sessions WHERE session_id = $1", session_id)
            raise HTTPException(status_code=403, detail="Session expired.")

        return session_data["email"]

    except asyncpg.PostgresError:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Session validation failed.")
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error during session validation.")
    finally:
        if conn:
            await conn.close()

@router.post("/register/")
async def register_user(credentials: UserCredentials):
    validate_password(credentials.password)
    hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = None
    try: 
        conn = await connect_db()
        await conn.execute(
            "INSERT INTO credentials (email, password) VALUES ($1, $2)",
            credentials.email, hashed_password
        )

        return {"message": "User registered successfully."}
        
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Email already registered.")
    except asyncpg.PostgresError:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error during registration.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close()

@router.post("/login/")
async def login_user(credentials: UserCredentials):
    # Check rate limiting
    if is_rate_limited(credentials.email):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    
    conn = None
    try:
        conn = await connect_db()
        user = await conn.fetchrow("SELECT email, password FROM credentials WHERE email = $1", credentials.email)

        if not user or not bcrypt.checkpw(
            credentials.password.encode("utf-8"),
            user["password"].encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        session_id = str(uuid.uuid4())
        expiration_time = datetime.now(timezone.utc) + timedelta(hours=1)  # Session expires in 1 hour

        await conn.execute("""
            INSERT INTO sessions (session_id, email, expiration)
            VALUES ($1, $2, $3)
        """, session_id, credentials.email, expiration_time)

        # Clear login attempts on successful login
        login_attempts[credentials.email] = []

        response = JSONResponse(content={"message": "User logged in successfully."})
        response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, max_age=3600,samesite="strict")  # Cookie valid for 1 hour
        return response
        
    except asyncpg.PostgresError:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error during login.")
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close()

@router.get("/check-login/")
async def check_login(session_id: str = Cookie(None)):
    try:
        email = await get_session_email(session_id)
        return {"isAuthenticated": True}
    except HTTPException as e:
        if e.status_code == 403:
            return {"isAuthenticated": False}
        raise e
        
@router.post("/logout/")
async def logout_user(session_id: str = Cookie(None)):
    if session_id:
        conn = None
        try:
            conn = await connect_db()
            await conn.execute("DELETE FROM sessions WHERE session_id = $1", session_id)
        except Exception:
            traceback.print_exc()
        finally:
            await conn.close()    

    response = JSONResponse(content={"message": "User logged out successfully."})
    response.delete_cookie("session_id")
    return response

@router.put("/update-password/")
async def update_password(password_data: PasswordUpdate, session_id: str = Cookie(None)):
    email = await get_session_email(session_id)
    validate_password(password_data.new_password)

    conn = None
    try:
        conn = await connect_db()
        
        record = await conn.fetchrow(
            "SELECT password FROM credentials WHERE email = $1", email
        )

        if not record or not bcrypt.checkpw(
            password_data.current_password.encode("utf-8"),
            record["password"].encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Current password incorrect.")

        hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        await conn.execute(
            "UPDATE credentials SET password = $1 WHERE email = $2",
            hashed_new_password, email
        )

        return {"message": "Password updated successfully."}

    except asyncpg.PostgresError:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error updating password.")
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close() 