import uuid
from fastapi import FastAPI, HTTPException, Cookie, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import aioredis
import bcrypt
import magic  
import pytesseract
from PIL import Image
from chatbot import generate_bot_response
from io import BytesIO
import pytesseract
import pdfplumber
import fitz

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
redis_client = aioredis.from_url(f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}")

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

class Message(BaseModel):
    message: str  

class Preferences(BaseModel):
    diet_preference: str      

class HealthConditions(BaseModel):
    allergies: str

class ChatMessage(BaseModel):
    user_message: str
    bot_response: str

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("static/index.html")

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
        # Generate a random session ID using uuid4
        session_id = str(uuid.uuid4())
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
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")

    await redis_client.hset(f"personal_details:{email.decode('utf-8')}", mapping={
        "name": details.name,
        "date_of_birth": details.date_of_birth,
        "gender": details.gender,
        "height": details.height,
        "weight": details.weight,
    })
    return {"message": "Personal details added successfully."}

@app.post("/preferences/")
async def add_preferences(preferences: Preferences, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    await redis_client.hset(f"preferences:{email.decode('utf-8')}", mapping={
        "diet_preference": preferences.diet_preference,
    })
    
    return {"message": "Food preferences saved successfully."}

@app.post("/health-conditions/")
async def add_health_conditions(health_conditions: HealthConditions, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    await redis_client.hset(f"health_conditions:{email.decode('utf-8')}", mapping={
        "allergies": health_conditions.allergies or " ",
    })
    
    return {"message": "Health conditions saved successfully."}

@app.get("/personal-details/")
async def get_personal_details(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    result = await redis_client.hgetall(f"personal_details:{email.decode('utf-8')}")
    if result:
        return {
            "email": email.decode('utf-8'),
            "name": result[b'name'].decode('utf-8'),
            "date_of_birth": result[b'date_of_birth'].decode('utf-8'),
            "gender": result[b'gender'].decode('utf-8'),
            "height": float(result[b'height']),
            "weight": float(result[b'weight']),
        }
    else:
        raise HTTPException(status_code=404, detail="User not found.")
    
@app.get("/preferences/")
async def get_preferences(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    result = await redis_client.hgetall(f"preferences:{email.decode('utf-8')}")
    if result:
        return {
            "diet_preference": result[b'diet_preference'].decode('utf-8'),
        }
    else:
        raise HTTPException(status_code=404, detail="Preferences not found.")

@app.get("/health-conditions/")
async def get_health_conditions(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    result = await redis_client.hgetall(f"health_conditions:{email.decode('utf-8')}")
    if result:
        return {
            "allergies": result[b'allergies'].decode('utf-8') if result.get(b'allergies') else None,
        }
    else:
        raise HTTPException(status_code=404, detail="Health conditions not found.")          

@app.put("/update-password/")
async def update_password(password_data: PasswordUpdate, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    user_data = await redis_client.hgetall(f"user:{email.decode('utf-8')}")

    if user_data and bcrypt.checkpw(password_data.current_password.encode('utf-8'), user_data[b'password']):
        hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await redis_client.hset(f"user:{email.decode('utf-8')}", "password", hashed_new_password)
        return {"message": "Password updated successfully."}
    else:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    
@app.post("/chat/")
async def chat_with_bot(message: Message, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    # Generate response from the AI model
    response = await generate_bot_response(message.message, session_id, redis_client)
    
    # Return structured data with the chat message
    return ChatMessage(
        user_message=message.message,
        bot_response=response['bot_response']
    )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    content = await extract_file_content(file)

    analyzed_content = await generate_bot_response(content, session_id, redis_client)
    
    return analyzed_content

async def extract_file_content(uploaded_file: UploadFile) -> str:
    file_content = ""

    # Detect the file type
    mime = magic.Magic(mime=True)
    first_bytes = await uploaded_file.read(2048)
    mime_type = mime.from_buffer(first_bytes)
    await uploaded_file.seek(0)  # Reset file pointer

    if mime_type.startswith('image/'):
        image_bytes = await uploaded_file.read()  # Read file into memory
        image = Image.open(BytesIO(image_bytes))  # Open image from memory
        file_content = pytesseract.image_to_string(image)  # Extract text
    elif mime_type == "text/plain":
        file_content = (await uploaded_file.read()).decode("utf-8")  # Read text file
    elif mime_type == "application/pdf":
        pdf_bytes = await uploaded_file.read()  # Read file into memory
        pdf_reader = fitz.open(stream=pdf_bytes, filetype="pdf")  # Load PDF in memory
        extracted_text = ""
        # Use pdfplumber for high-accuracy text extraction
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""  # Extract formatted text
        
        # If no text was found, use OCR on each page
        if not extracted_text.strip():
            for page_num in range(len(pdf_reader)):
                pix = pdf_reader[page_num].get_pixmap()  # Convert PDF page to image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                extracted_text += pytesseract.image_to_string(img)  # OCR processing
        
        file_content = extracted_text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    return file_content    

# Run the application using: uvicorn main:app --reload
