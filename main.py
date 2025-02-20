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
    food_preference: str 
    snack_preferences: str
    meal_timings: str
    cuisine_preferences: str
    spicy_food_tolerance: str
    preferred_meal_type: str
    favorite_meal: str
    meal_frequency: str
    hydration_level: str
    activity_level: str
    fitness_goal: str
    food_restrictions: str
    caffeine_intake: str
    average_sleep: str
    sleep_quality: str
    supplement_usage: str
    supplement_frequency: str
    cheat_day_frequency: str
    cultural_preferences: str
    preferred_ingredients: str
    sweet_preference: str
    eating_out_frequency: str
    preferred_drinks: str     

class HealthConditions(BaseModel):
    allergies: str
    diabetes: str
    hypertension: str
    cholesterol: str 
    thyroid: str
    kidney_disease: str
    liver_disease: str 
    lactose_intolerance: str
    gluten_sensitivity: str
    pcos: str  # Only applicable for females
    anemia: str
    osteoporosis: str
    ibs: str
    gerd: str
    gout: str
    other_conditions: str

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
        "food_preference": preferences.food_preference,
        "snack_preferences": preferences.snack_preferences,
        "meal_timings": preferences.meal_timings,
        "cuisine_preferences": preferences.cuisine_preferences,
        "spicy_food_tolerance": preferences.spicy_food_tolerance,
        "preferred_meal_type": preferences.preferred_meal_type,
        "favorite_meal": preferences.favorite_meal,
        "meal_frequency": preferences.meal_frequency,
        "hydration_level": preferences.hydration_level,
        "activity_level": preferences.activity_level,
        "fitness_goal": preferences.fitness_goal,
        "food_restrictions": preferences.food_restrictions,
        "caffeine_intake": preferences.caffeine_intake,
        "average_sleep": preferences.average_sleep,
        "sleep_quality": preferences.sleep_quality,
        "supplement_usage": preferences.supplement_usage,
        "supplement_frequency": preferences.supplement_frequency,
        "cheat_day_frequency": preferences.cheat_day_frequency,
        "cultural_preferences": preferences.cultural_preferences,
        "preferred_ingredients": preferences.preferred_ingredients,
        "sweet_preference": preferences.sweet_preference,
        "eating_out_frequency": preferences.eating_out_frequency,
        "preferred_drinks": preferences.preferred_drinks
           
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
        "allergies": health_conditions.allergies,
        "diabetes": health_conditions.diabetes,
        "hypertension": health_conditions.hypertension,
        "cholesterol": health_conditions.cholesterol,
        "thyroid": health_conditions.thyroid,
        "kidney_disease": health_conditions.kidney_disease,
        "liver_disease": health_conditions.liver_disease,
        "lactose_intolerance": health_conditions.lactose_intolerance,
        "gluten_sensitivity": health_conditions.gluten_sensitivity,
        "pcos": health_conditions.pcos,
        "anemia": health_conditions.anemia,
        "osteoporosis": health_conditions.osteoporosis,
        "ibs": health_conditions.ibs,
        "gerd": health_conditions.gerd,
        "gout": health_conditions.gout,
        "other_conditions": health_conditions.other_conditions
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
            "food_preference": result.get(b'food_preference', b'').decode('utf-8'),
            "cuisine_preferences": result.get(b'cuisine_preferences', b'').decode('utf-8').split(','),
            "spicy_food_tolerance": result.get(b'spicy_food_tolerance', b'').decode('utf-8'),
            "preferred_meal_type": result.get(b'preferred_meal_type', b'').decode('utf-8'),
            "favorite_meal": result.get(b'favorite_meal', b'').decode('utf-8'),
            "meal_frequency": result.get(b'meal_frequency', b'').decode('utf-8'),
            "hydration_level": result.get(b'hydration_level', b'').decode('utf-8'),
            "activity_level": result.get(b'activity_level', b'').decode('utf-8'),
            "fitness_goal": result.get(b'fitness_goal', b'').decode('utf-8'),
            "food_restrictions": result.get(b'food_restrictions', b'').decode('utf-8').split(','),
            "caffeine_intake": result.get(b'caffeine_intake', b'').decode('utf-8'),
            "average_sleep": result.get(b'average_sleep', b'').decode('utf-8'),
            "sleep_quality": result.get(b'sleep_quality', b'').decode('utf-8'),
            "supplement_usage": result.get(b'supplement_usage', b'').decode('utf-8'),
            "supplement_frequency": result.get(b'supplement_frequency', b'').decode('utf-8'),
            "snack_preferences": result.get(b'snack_preferences', b'').decode('utf-8').split(','),
            "meal_timings": result.get(b'meal_timings', b'').decode('utf-8').split(','),
            "cheat_day_frequency": result.get(b'cheat_day_frequency', b'').decode('utf-8'),
            "cultural_preferences": result.get(b'cultural_preferences', b'').decode('utf-8').split(','),
            "preferred_ingredients": result.get(b'preferred_ingredients', b'').decode('utf-8').split(','),
            "sweet_preference": result.get(b'sweet_preference', b'').decode('utf-8'),
            "eating_out_frequency": result.get(b'eating_out_frequency', b'').decode('utf-8'),
            "preferred_drinks": result.get(b'preferred_drinks', b'').decode('utf-8').split(',')   
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
            "allergies": result.get(b'allergies', b'').decode('utf-8'),
            "diabetes": result.get(b'diabetes', b'').decode('utf-8'),  
            "hypertension": result.get(b'hypertension', b'').decode('utf-8'),
            "cholesterol": result.get(b'cholesterol', b'').decode('utf-8'),
            "thyroid": result.get(b'thyroid', b'').decode('utf-8'),
            "kidney_disease": result.get(b'kidney_disease', b'').decode('utf-8'),
            "liver_disease": result.get(b'liver_disease', b'').decode('utf-8'),
            "lactose_intolerance": result.get(b'lactose_intolerance', b'').decode('utf-8'),
            "gluten_sensitivity": result.get(b'gluten_sensitivity', b'').decode('utf-8'),
            "pcos": result.get(b'pcos', b'').decode('utf-8'),
            "anemia": result.get(b'anemia', b'').decode('utf-8'),
            "osteoporosis": result.get(b'osteoporosis', b'').decode('utf-8'),
            "ibs": result.get(b'ibs', b'').decode('utf-8'),
            "gerd": result.get(b'gerd', b'').decode('utf-8'),
            "gout": result.get(b'gout', b'').decode('utf-8'),
            "other_conditions": result.get(b'other_conditions', b'').decode('utf-8')  
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
    
    # Detect or create a chat topic
    topic = await redis_client.get(f"{email}:current_topic")
    if not topic:
        topic = await detect_topic(message.message)  # Generate a topic
        await redis_client.set(f"{email}:current_topic", topic)
        await redis_client.sadd(f"{email}:topics", topic)
    
    # Generate response from the AI model
    response = await generate_bot_response(message.message, session_id, redis_client)
    
    # Save the full chat history
    chat_entry = f"User: {message.message}\nBot: {response['bot_response']}"
    await redis_client.rpush(f"{email}:chats:{topic}", chat_entry)

    # Return structured data with the chat message
    return ChatMessage(
        user_message=message.message,
        bot_response=response['bot_response']
    )

async def generate_bot_response(user_message: str, session_id: str, redis_client) -> dict:
    """Generate bot response using TinyLlama with health details and past context."""
    
    user_email = await redis_client.get(f"session:{session_id}")
    if not user_email:
        return {"bot_response": "Session expired or invalid. Please log in again."}

    user_email = user_email.decode("utf-8")
    
    # Fetch user details
    personal_details = await redis_client.hgetall(f"personal_details:{user_email}")
    preferences = await redis_client.hgetall(f"preferences:{user_email}")
    health_conditions = await redis_client.hgetall(f"health_conditions:{user_email}")

    if not personal_details:
        return {"bot_response": "Your profile details are missing. Please update your profile."}

    try:
        # Extract all details from Redis (decode from bytes to strings)
        user_profile = {k.decode("utf-8"): v.decode("utf-8") for k, v in personal_details.items()}
        preferences_data = {k.decode("utf-8"): v.decode("utf-8") for k, v in preferences.items()}
        health_data = {k.decode("utf-8"): v.decode("utf-8") for k, v in health_conditions.items()}

        # Essential details
        name = user_profile.get("name", "User")
        weight = float(user_profile.get("weight", 0))
        height = float(user_profile.get("height", 0))
        dob = user_profile.get("date_of_birth", "")
        gender = user_profile.get("gender", "Unknown")

        # Calculate additional health metrics
        age = health_metrics.calculate_age(dob)
        bmi = health_metrics.calculate_bmi(weight, height)
        bmr = health_metrics.calculate_bmr(weight, height, age, gender)
        bfp = health_metrics.calculate_bfp_from_bmi(bmi, age, gender)
        lbm = health_metrics.calculate_lbm(weight, height, gender)
        metabolicage = health_metrics.calculate_metabolic_age(bmr, age)
        musclemass = health_metrics.calculate_muscle_mass(weight, bfp) 
        proteinintake = health_metrics.calculate_protein_intake(weight, activity_level=preferences_data.get("activity_level", "sedentary")) 
        maxheartrate = health_metrics.calculate_max_heart_rate(age)
        hydration = health_metrics.hydration_level(weight, activity_level=preferences_data.get("activity_level", "sedentary"))

    except KeyError:
        return {"bot_response": "Some details are missing in your profile. Please update your weight, height, date of birth, and gender."}

    # Fetch last 5 chat messages for context
    chat_history = await redis_client.lrange(f"chat_history:{user_email}", -5, -1)
    chat_context = "\n".join(chat_history)

    # **Construct a Concise Prompt**
    prompt = f"""
    User Query: {user_message}
    
    User Details:
    - Age: {age} years
    - Weight: {weight} kg
    - Height: {height} cm
    - Gender: {gender}
    
    Previous Context:
    {chat_context}
    
    Bot:
    """

    # Generate response using TinyLlama
    response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])["message"]["content"]

    # Save latest chat history (for context only)
    await redis_client.rpush(f"chat_history:{user_email}", user_message)
    
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
