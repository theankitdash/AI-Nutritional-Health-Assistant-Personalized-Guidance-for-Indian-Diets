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

class HealthMetrics(BaseModel):
    age: int
    bmi: float
    bmr: float
    tdee: float
    bfp: float
    lbm: float
    muscle_mass: float
    visceral_fat: float
    whr: float
    metabolic_age: float
    hydration_level: float
    protein_intake: float
    
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

    # Trigger health metric calculation
    await calculate_and_store_health_metrics(email.decode('utf-8'))

    return {"message": "Personal details added successfully."}

@app.post("/preferences/")
async def add_preferences(preferences: Preferences, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    await redis_client.hset(f"preferences:{email.decode('utf-8')}", mapping=preferences.model_dump())

    # Recalculate health metrics
    await calculate_and_store_health_metrics(email.decode('utf-8'))

    return {"message": "Food preferences saved successfully."}

@app.post("/health-conditions/")
async def add_health_conditions(health_conditions: HealthConditions, session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis_client.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    await redis_client.hset(f"health_conditions:{email.decode('utf-8')}", mapping=health_conditions.model_dump())

    # Recalculate health metrics
    await calculate_and_store_health_metrics(email.decode('utf-8'))

    return {"message": "Health conditions saved successfully."}

async def calculate_and_store_health_metrics(email: str):
    # Fetch user details
    personal_details = await redis_client.hgetall(f"personal_details:{email}")
    preferences = await redis_client.hgetall(f"preferences:{email}")
    health_conditions = await redis_client.hgetall(f"health_conditions:{email}")

    if not personal_details or not preferences or not health_conditions:
        raise HTTPException(status_code=404, detail="User profile is incomplete. Please update all the details.")

    # Decode Redis data
    personal_details_data = PersonalDetails(**{k.decode(): v.decode() for k, v in personal_details.items()})
    preferences_data = Preferences(**{k.decode(): v.decode() for k, v in preferences.items()})
    health_data = HealthConditions(**{k.decode(): v.decode() for k, v in health_conditions.items()})

    # Calculate Health Metrics
    age = health_metrics.calculate_age(personal_details_data.dateOfBirth)
    bmi = health_metrics.calculate_bmi(personal_details_data.weight, personal_details_data.height)
    bmr = health_metrics.calculate_bmr(personal_details_data.weight, personal_details_data.height, age, personal_details_data.gender)
    tdee = health_metrics.calculate_tdee(bmr, preferences_data.activityLevel)
    bfp = health_metrics.calculate_bfp(bmi, age, personal_details_data.gender)
    lbm = health_metrics.calculate_lbm(personal_details_data.weight, bfp)
    muscle_mass=health_metrics.calculate_muscle_mass(lbm)
    visceral_fat=health_metrics.calculate_visceral_fat(bfp, personal_details_data.waist, personal_details_data.height)
    whr=health_metrics.calculate_whtr(personal_details_data.waist, personal_details_data.height)
    metabolic_age=health_metrics.calculate_metabolic_age(lbm, bmr, age)
    hydration_level=health_metrics.calculate_hydration_level(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age)
    protein_intake=health_metrics.calculate_protein_intake(preferences_data.activityLevel, preferences_data.fitnessGoal, lbm)
    #macro_nutrients=health_metrics.calculate_macronutrients(tdee, preferences_data.fitnessGoal, personal_details_data.gender)
    #micro_nutrients=health_metrics.calculate_micronutrients(preferences_data.fitnessGoal, age, personal_details_data.gender, preferences_data.activityLevel)
    #energy_surplus_deficit=health_metrics.calculate_energy_surplus_deficit(tdee, preferences_data.fitnessGoal)
    #glycemic_index=health_metrics.glycemic_index_load(preferences_data.foodPreference),  # To be updated later
    #bmd=health_metrics.calculate_bmd(personal_details_data.weight, personal_details_data.height, age, bfp, personal_details_data.gender)
    #resting_hr=health_metrics.calculate_resting_heart_rate(age, preferences_data.fitnessGoal)
    #max_heart_rate=health_metrics.calculate_max_heart_rate(age)
    #electrolyte_balance=health_metrics.calculate_electrolyte_balance(age, personal_details_data.gender, preferences_data.activityLevel, preferences_data.fitnessGoal)
    #body_water_percentage=health_metrics.calculate_body_water_percentage(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age, bfp, preferences_data.activityLevel, electrolyte_balance)
    #skeletal_mass=health_metrics.calculate_skeletal_muscle_mass(lbm)
    #protein_absorption=health_metrics.calculate_protein_absorption(health_metrics.calculate_protein_intake, preferences_data.foodPreference),  # To be updated later
    #metabolic_flexibility=health_metrics.calculate_metabolic_flexibility(preferences_data.activityLevel, preferences_data.foodPreference),  # To be updated later
    
    #sleep_score=health_metrics.calculate_sleep_score(preferences_data.averageSleep, preferences_data.sleepQuality)
    #fiber=health_metrics.daily_fiber_intake(age, personal_details_data.gender, preferences_data.activityLevel, preferences_data.fitnessGoal)


    health_metrics_data = HealthMetrics(
        age=age, bmi=bmi, bmr=bmr, tdee=tdee, bfp=bfp, lbm=lbm, muscle_mass=muscle_mass, visceral_fat=visceral_fat, 
        whr=whr, metabolic_age=metabolic_age, hydration_level=hydration_level, protein_intake=protein_intake
        
           )

    # Store computed health metrics in Redis
    await redis_client.hset(f"health_metrics:{email}", mapping=health_metrics_data.model_dump())

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

@app.get("/chat/history/")
async def get_chat_history(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")

    email = await redis_client.get(f"session:{session_id}")
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")

    history = await redis_client.lrange(f"{email.decode()}:chats", 0, -1)  # Fetch full history
    return {"history": [entry.decode("utf-8") for entry in history]}

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

    # Decode Redis data
    personal_details_data = PersonalDetails(**{k.decode(): v.decode() for k, v in personal_details.items()})
    preferences_data = Preferences(**{k.decode(): v.decode() for k, v in preferences.items()})
    health_data = HealthConditions(**{k.decode(): v.decode() for k, v in health_conditions.items()})
    
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
    await redis_client.rpush(f"{email}:chats", chat_entry)

    # Return structured data with the chat message
    return ChatMessage(
        user_message=message.message,
        bot_response=response['bot_response']
    )

async def generate_bot_response(user_message: str, 
                                personal_details: PersonalDetails, 
                                preferences: Preferences, 
                                health_conditions: HealthConditions, 
                                redis_client, email: str) -> dict:
    
    """Generate bot response using TinyLlama with health details and past context."""

    # Fetch last 5 chat messages for context (only Redis call in this function)
    chat_history = await redis_client.lrange(f"chat_history:{email}", -5, -1)
    chat_context = "\n".join([entry.decode("utf-8") for entry in chat_history])

    # Construct a concise prompt
    prompt = f"""
    User Profile:
    Personal Details: {', '.join([f'{k}: {v}' for k, v in personal_details.dict().items() if v])}
    Preferences: {', '.join([f'{k}: {v}' for k, v in preferences.dict().items() if v])}
    Health Conditions: {', '.join([f'{k}: {v}' for k, v in health_conditions.dict().items() if v])}

    Recent Conversation:
    {chat_context}

    Current Question:
    {user_message}

    Respond as a nutritional expert tailored to the user's profile:
    """

    # Generate response using TinyLlama
    response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])["message"]["content"]

    # Save latest chat history (for context only)
    await redis_client.rpush(f"chat_history:{email}", user_message)
    
    return {"bot_response": response}

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
