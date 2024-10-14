from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
import os
from datetime import date, datetime, timedelta, timezone
import mysql.connector
from mysql.connector import Error
import bcrypt
import jwt

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

# JWT Secret and Algorithm
SECRET_KEY = "your_secret_key"  # Keep this secret!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for receiving tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


# Function to create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to create MySQL tables if they don't exist
async def create_tables():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
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
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to get the current user by verifying the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return email

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

    connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user_credentials (email, password)
            VALUES (%s, %s)
        """, (credentials.email, hashed_password))
        connection.commit()
        return {"message": "User registered successfully."}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# Endpoint to login and generate a JWT token
@app.post("/login/")
async def login_user(credentials: UserCredentials):
    connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM user_credentials WHERE email = %s", (credentials.email,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(credentials.password.encode('utf-8'), result[0].encode('utf-8')):
            # Create JWT
            access_token = create_access_token(data={"sub": credentials.email})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# Endpoint to add personal details (requires logged-in session with JWT)
@app.post("/personal-details/")
async def add_personal_details(details: PersonalDetails, current_user: str = Depends(get_current_user)):
    connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO personal_details (email, name, date_of_birth, gender, height, weight)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user, details.name, details.date_of_birth, details.gender, details.height, details.weight))
        connection.commit()
        return {"message": "Personal details added successfully."}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# Endpoint to fetch personal details by JWT token (requires logged-in session)
@app.get("/personal-details/")
async def get_personal_details(current_user: str = Depends(get_current_user)):
    connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM personal_details WHERE email = %s", (current_user,))
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
        connection.close()

# Endpoint to update personal details (requires logged-in session with JWT)
@app.put("/personal-details/")
async def update_personal_details(details: PersonalDetails, current_user: str = Depends(get_current_user)):
    connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE personal_details
            SET name = %s, date_of_birth = %s, gender = %s, height = %s, weight = %s
            WHERE email = %s
        """, (details.name, details.date_of_birth, details.gender, details.height, details.weight, current_user))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"message": "Personal details updated successfully."}
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.put("/update-password/")
async def update_password(password_data: PasswordUpdate, current_user: str = Depends(get_current_user)):
    connection = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM user_credentials WHERE email = %s", (current_user,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password_data.current_password.encode('utf-8'), result[0].encode('utf-8')):
            hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                UPDATE user_credentials
                SET password = %s
                WHERE email = %s
            """, (hashed_new_password, current_user))
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found.")
            return {"message": "Password updated successfully."}
        else:
            raise HTTPException(status_code=401, detail="Current password is incorrect.")
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()


@app.post("/logout/")
async def logout_user():
    # Frontend should handle token removal on the client-side
    return {"message": "Logged out successfully."}

#uvicorn main:app --reload