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
from io import BytesIO
import pytesseract
import pdfplumber
import fitz
import health_metrics
import ollama

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
    dateOfBirth: str
    gender: str
    height: float
    weight: float
    waist: float

class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class Message(BaseModel):
    message: str  

class Preferences(BaseModel):
    foodPreference: str 
    snackPreferences: str 
    mealTimings: str 
    cheatDayFrequency: str
    culturalPreferences: str 
    preferredIngredients: str 
    cuisinePreferences: str
    spicyFoodTolerance: str
    preferredMealType: str
    favoriteMeal: str
    mealFrequency: str
    sweetPreference: str
    eatingOutFrequency: str
    hydrationLevel: float
    preferredDrinks: str
    activityLevel: str
    fitnessGoal: str
    foodRestrictions: str
    caffeineIntake: str
    averageSleep: float
    sleepQuality: str
    supplementUsage: str
    supplementFrequency: str     

class HealthConditions(BaseModel):
    allergies: str
    diabetes: str
    hypertension: str 
    cholesterol: str
    thyroid: str
    kidneyDisease: str
    liverDisease: str
    lactoseIntolerance: str
    glutenSensitivity: str
    pcos: str
    anemia: str
    osteoporosis: str
    ibs: str
    gerd: str
    gout: str
    otherConditions: str

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

    await redis_client.hset(f"personal_details:{email.decode('utf-8')}", mapping=details.model_dump())
    return {"message": "Personal details added successfully."}

@app.post("/preferences/")
async def add_preferences(preferences: Preferences, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    await redis_client.hset(f"preferences:{email.decode('utf-8')}", mapping=preferences.model_dump())
    return {"message": "Food preferences saved successfully."}

@app.post("/health-conditions/")
async def add_health_conditions(health_conditions: HealthConditions, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    await redis_client.hset(f"health_conditions:{email.decode('utf-8')}", mapping=health_conditions.model_dump())

    return {"message": "Health conditions saved successfully."}

@app.get("/personal-details/")
async def get_personal_details(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    result = await redis_client.hgetall(f"personal_details:{email.decode('utf-8')}")
    if not result:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {key: value for key, value in result.items()}  
    
@app.get("/preferences/")
async def get_preferences(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    result = await redis_client.hgetall(f"preferences:{email.decode('utf-8')}")
    if not result:
        raise HTTPException(status_code=404, detail="Preferences not found.")
    
    return {key: value for key, value in result.items()}  

@app.get("/health-conditions/")
async def get_health_conditions(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    result = await redis_client.hgetall(f"health_conditions:{email.decode('utf-8')}")

    if not result:
        raise HTTPException(status_code=404, detail="Health conditions not found.")  
        
    return {key: value for key, value in result.items()}    

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
    
@app.get("/chat/topics/")
async def get_chat_topics(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    email = await redis_client.get(f"session:{session_id}")
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")

    topics = await redis_client.smembers(f"{email}:topics")
    return {"topics": list(topics)}

@app.get("/chat/history/")
async def get_chat_history(topic: str, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    email = await redis_client.get(f"session:{session_id}")
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")

    history = await redis_client.lrange(f"{email}:chats:{topic}", 0, -1)  # Fetch full history
    return {"topic": topic, "history": history}

@app.post("/chat/")
async def chat_with_bot(message: Message, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    email = email.decode("utf-8")

    # Fetch user details
    personal_details = await redis_client.hgetall(f"personal_details:{email}")
    preferences = await redis_client.hgetall(f"preferences:{email}")
    health_conditions = await redis_client.hgetall(f"health_conditions:{email}")

    if not personal_details or not preferences or not health_conditions:
        raise HTTPException(status_code=404, detail="User profile is incomplete. Please update all the details.")
    
    # Decode Redis data
    personal_details_data = PersonalDetails(**{k.decode(): v.decode() for k, v in personal_details.items()})
    preferences_data = Preferences(**{k.decode("utf-8"): v.decode("utf-8") for k, v in preferences.items()}) if preferences else None
    health_data = HealthConditions(**{k.decode("utf-8"): v.decode("utf-8") for k, v in health_conditions.items()}) if health_conditions else None

    
    # Detect or create a chat topic
    topic = await redis_client.get(f"{email}:current_topic")
    if not topic:
        topic = await detect_topic(message.message)  # Generate a topic
        await redis_client.set(f"{email}:current_topic", topic)
        await redis_client.sadd(f"{email}:topics", topic)
    
    # Generate response with structured user details
    response = await generate_bot_response(
        user_message=message.message,
        personal_details=personal_details_data,
        preferences=preferences_data,
        health_conditions=health_data,
        redis_client=redis_client,
         email=email
    )
    
    # Save the full chat history
    chat_entry = f"User: {message.message}\nBot: {response['bot_response']}"
    await redis_client.rpush(f"{email}:chats:{topic}", chat_entry)

    # Return structured data with the chat message
    return ChatMessage(
        user_message=message.message,
        bot_response=response['bot_response']
    )

async def generate_bot_response(user_message: str, personal_details: PersonalDetails, preferences: Preferences, health_conditions: HealthConditions, redis_client, email: str) -> dict:
    """Generate bot response using TinyLlama with health details and past context."""

    # Fetch last 5 chat messages for context (only Redis call in this function)
    chat_history = await redis_client.lrange(f"chat_history:{email}", -5, -1)
    chat_context = "\n".join(chat_history)

    # Construct a concise prompt
    prompt = f"""
    User Query: {user_message}
    
    Previous Context:
    {chat_context}

    Bot:
    """

    # Generate response using TinyLlama
    response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])["message"]["content"]

    # Save latest chat history (for context only)
    await redis_client.rpush(f"chat_history:{email}", user_message)
    
    return {"bot_response": response}

async def detect_topic(user_message: str) -> str:
    """Generate a chat topic based on the first user message."""
    keywords = ["diet", "weight loss", "exercise", "calories", "hydration"]
    for word in keywords:
        if word in user_message.lower():
            return word.capitalize()
    return f"Chat-{uuid.uuid4().hex[:6]}"

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
