from fastapi import FastAPI, HTTPException, Cookie
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from redis.asyncio import Redis
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import uuid
import bcrypt
import health_metrics
import json

app = FastAPI()

# Connect to Redis
redis = Redis(host="localhost", port=6379, db=0)

# Initialize the LLM
LLM = OllamaLLM(model="gemma:2b")

#Load food dataset
with open("food_dataset.json") as f:
    food_data = json.load(f)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("static/index.html")

# Pydantic models 
class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class PersonalDetails(BaseModel):
    name: str
    dateOfBirth: str
    gender: str
    height: float
    weight: float
    waist: float 

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
    macro_nutrients: str  
    micro_nutrients: str 
    energy_surplus_deficit: float
    bmd: str 
    max_heart_rate: int
    electrolyte_balance: str  
    skeletal_mass: float
    sleep_score: float
    fiber: str 

class ChatRequest(BaseModel):
    message: str    

@app.post("/register/")
async def register_user(credentials: UserCredentials):
    if len(credentials.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    
    hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        await redis.hset(f"user:{credentials.email}", mapping={
            "password": hashed_password
        })
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail="Internal Redis error.")
    
    return {"message": "User registered successfully."}

@app.post("/login/")
async def login_user(credentials: UserCredentials):
    user_data = await redis.hgetall(f"user:{credentials.email}")

    if user_data and bcrypt.checkpw(credentials.password.encode('utf-8'), user_data[b'password']):
        # Generate a random session ID using uuid4
        session_id = str(uuid.uuid4())

        await redis.set(f"session:{session_id}", credentials.email, ex=3600)

        response = JSONResponse(content={"message": "User logged in successfully."})
        response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, max_age=3600)  # Set the cookie
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

@app.post("/logout/")
async def logout_user(session_id: str = Cookie(None)):
    if session_id:
        await redis.delete(f"session:{session_id}")
    response = JSONResponse(content={"message": "User logged out successfully."})
    response.delete_cookie("session_id")  # Delete the cookie
    return response

async def validate_session(session_id: str):
    if not session_id:
        raise HTTPException(status_code=403, detail="User is not logged in.")
    
    email = await redis.get(f"session:{session_id}")  # Retrieve email using session ID
    if not email:
        raise HTTPException(status_code=403, detail="Invalid session.")
    
    return email.decode('utf-8') 

@app.put("/update-password/")
async def update_password(password_data: PasswordUpdate, session_id: str = Cookie(None)):
    
    email = await validate_session(session_id)

    user_data = await redis.hgetall(f"user:{email}")

    if user_data and bcrypt.checkpw(password_data.current_password.encode('utf-8'), user_data[b'password']):
        hashed_new_password = bcrypt.hashpw(password_data.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await redis.hset(f"user:{email}", "password", hashed_new_password)
        return {"message": "Password updated successfully."}
    else:
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

@app.post("/personal-details/")
async def add_personal_details(details: PersonalDetails, session_id: str = Cookie(None)):

    email = await validate_session(session_id)

    await redis.hset(f"personal_details:{email}", mapping=details.model_dump())

    # Trigger health metric calculation
    await calculate_and_store_health_metrics(email)

    return {"message": "Personal details added successfully."}    

@app.post("/preferences/")
async def add_preferences(preferences: Preferences, session_id: str = Cookie(None)):

    email = await validate_session(session_id)
    
    await redis.hset(f"preferences:{email}", mapping=preferences.model_dump())

    # Recalculate health metrics
    await calculate_and_store_health_metrics(email)

    return {"message": "Food preferences saved successfully."}

@app.post("/health-conditions/")
async def add_health_conditions(health_conditions: HealthConditions, session_id: str = Cookie(None)):
    
    email = await validate_session(session_id)

    await redis.hset(f"health_conditions:{email}", mapping=health_conditions.model_dump())

    # Recalculate health metrics
    await calculate_and_store_health_metrics(email)

    return {"message": "Health conditions saved successfully."}

async def calculate_and_store_health_metrics(email: str):
    
    # Fetch user details
    personal_details = await redis.hgetall(f"personal_details:{email}")
    preferences = await redis.hgetall(f"preferences:{email}")
    health_conditions = await redis.hgetall(f"health_conditions:{email}")

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
    macro_nutrients=health_metrics.calculate_macronutrients(tdee, preferences_data.fitnessGoal, personal_details_data.gender)
    micro_nutrients=health_metrics.calculate_micronutrients(preferences_data.fitnessGoal, age, personal_details_data.gender, preferences_data.activityLevel)
    energy_surplus_deficit=health_metrics.calculate_energy_surplus_deficit(tdee, preferences_data.fitnessGoal)
    #glycemic_index=health_metrics.glycemic_index_load(preferences_data.foodPreference),  # To be updated later
    bmd=health_metrics.calculate_bmd(personal_details_data.weight, personal_details_data.height, age, bfp, personal_details_data.gender)
    max_heart_rate=health_metrics.calculate_max_heart_rate(age)
    electrolyte_balance=health_metrics.calculate_electrolyte_balance(age, personal_details_data.gender, preferences_data.activityLevel, preferences_data.fitnessGoal)
    #body_water_percentage=health_metrics.calculate_body_water_percentage(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age, bfp, preferences_data.activityLevel)
    skeletal_mass=health_metrics.calculate_skeletal_muscle_mass(lbm)
    #protein_absorption=health_metrics.calculate_protein_absorption(health_metrics.calculate_protein_intake, preferences_data.foodPreference),  # To be updated later
    #metabolic_flexibility=health_metrics.calculate_metabolic_flexibility(preferences_data.activityLevel, preferences_data.foodPreference),  # To be updated later
    
    sleep_score=health_metrics.calculate_sleep_score(preferences_data.averageSleep)
    fiber=health_metrics.daily_fiber_intake(age, personal_details_data.gender, preferences_data.activityLevel, preferences_data.fitnessGoal)


    health_metrics_data = HealthMetrics(
        age=age, bmi=bmi, bmr=bmr, tdee=tdee, bfp=bfp, lbm=lbm, muscle_mass=muscle_mass, visceral_fat=visceral_fat, 
        whr=whr, metabolic_age=metabolic_age, hydration_level=hydration_level, protein_intake=protein_intake, macro_nutrients=macro_nutrients,
        micro_nutrients=micro_nutrients, energy_surplus_deficit=energy_surplus_deficit, bmd=bmd, max_heart_rate=max_heart_rate,
        electrolyte_balance=electrolyte_balance, skeletal_mass=skeletal_mass, sleep_score=sleep_score, fiber=fiber    
           )

    # Store computed health metrics in Redis
    await redis.hset(f"health_metrics:{email}", mapping=health_metrics_data.model_dump())

@app.get("/personal-details/")
async def get_personal_details(session_id: str = Cookie(None)):
    
    email = await validate_session(session_id)
    
    result = await redis.hgetall(f"personal_details:{email}")
    if not result:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {key: value for key, value in result.items()}  
    
@app.get("/preferences/")
async def get_preferences(session_id: str = Cookie(None)):
    
    email = await validate_session(session_id)
    
    result = await redis.hgetall(f"preferences:{email}")
    if not result:
        raise HTTPException(status_code=404, detail="Preferences not found.")
    
    return {key: value for key, value in result.items()}  

@app.get("/health-conditions/")
async def get_health_conditions(session_id: str = Cookie(None)):

    email = await validate_session(session_id)
    
    result = await redis.hgetall(f"health_conditions:{email}")

    if not result:
        raise HTTPException(status_code=404, detail="Health conditions not found.")  
        
    return {key: value for key, value in result.items()} 

@app.post("/chat/")
async def chat_with_bot(chat: ChatRequest, session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    # Fetch all user data from Redis
    personal = await redis.hgetall(f"personal_details:{email}")
    prefs = await redis.hgetall(f"preferences:{email}")
    conditions = await redis.hgetall(f"health_conditions:{email}")
    metrics = await redis.hgetall(f"health_metrics:{email}")

    if not personal or not prefs or not conditions or not metrics:
        raise HTTPException(status_code=400, detail="Missing user profile data.")

    # Decode Redis byte values
    personal = {k.decode(): v.decode() for k, v in personal.items()}
    prefs = {k.decode(): v.decode() for k, v in prefs.items()}
    conditions = {k.decode(): v.decode() for k, v in conditions.items()}
    metrics = {k.decode(): v.decode() for k, v in metrics.items()}

    user_context = f"""
    Personal Details:
    Name: {personal.get("name")}, Age: {health_metrics.calculate_age(personal.get("dateOfBirth"))}, Gender: {personal.get("gender")}
    Height: {personal.get("height")} cm, Weight: {personal.get("weight")} kg, Waist: {personal.get("waist")} cm

    Preferences:
    Food Preference: {prefs.get("foodPreference")}, Snack Preference: {prefs.get("snackPreferences")}, Meal Timings: {prefs.get("mealTimings")}
    Activity Level: {prefs.get("activityLevel")}, Fitness Goal: {prefs.get("fitnessGoal")}, Cultural Preferences: {prefs.get("culturalPreferences")}, Cuisine Preferences: {prefs.get("cuisinePreferences")}
    Spicy Food Tolerance: {prefs.get("spicyFoodTolerance")}, Preferred Meal Type: {prefs.get("preferredMealType")}
    Favorite Meal: {prefs.get("favoriteMeal")}, Meal Frequency: {prefs.get("mealFrequency")}, Sweet Preference: {prefs.get("sweetPreference")}

    Health Conditions:
    Allergies: {conditions.get("allergies")}, Diabetes: {conditions.get("diabetes")}, Hypertension: {conditions.get("hypertension")}
    Other: {conditions.get("otherConditions")}, PCOS: {conditions.get("pcos")}, Anemia: {conditions.get("anemia")}
    Osteoporosis: {conditions.get("osteoporosis")}, IBS: {conditions.get("ibs")}, GERD: {conditions.get("gerd")}

    Metrics:
    BMI: {metrics.get("bmi")}, BMR: {metrics.get("bmr")}, TDEE: {metrics.get("tdee")}
    Body Fat Percentage: {metrics.get("bfp")}, Hydration Level: {metrics.get("hydration_level")}
    Muscle Mass: {metrics.get("muscle_mass")}, Sleep Score: {metrics.get("sleep_score")}, Fiber Intake: {metrics.get("fiber")}
    Protein Intake: {metrics.get("protein_intake")}, Macro Nutrients: {metrics.get("macro_nutrients")}, Micro Nutrients: {metrics.get("micro_nutrients")}
    Energy Surplus/Deficit: {metrics.get("energy_surplus_deficit")}, Electrolyte Balance: {metrics.get("electrolyte_balance")}

    """

    # Retrieve last 5 messages from Redis list
    history_key = f"chat_history:{email}"
    history = await redis.lrange(history_key, -10, -1)  # last 10 messages
    history = [msg.decode() for msg in history]

    conversation_history = "\n".join(history) if history else "No previous conversation."

    # Add new user message to history
    await redis.rpush(history_key, f"User: {chat.message}")
    await redis.ltrim(history_key, -10, -1)  # Keep only last 10 messages

    # Create the prompt
    prompt_template = PromptTemplate(
        input_variables=["user_context", "conversation_history", "user_message"],
        template="""
        You are a personalized nutrition assistant specialized in Indian dietary habits. Use the user's health data and preferences to respond naturally.

        User Profile:
        {user_context}

        Previous Conversation:
        {conversation_history}

        User Now Says:
        {user_message}

        Reply in a friendly, knowledgeable, and contextual way based on the above info.
        """
    )

    chain = LLMChain(llm=LLM, prompt=prompt_template)

    response = chain.run({
        "user_context": user_context,
        "conversation_history": conversation_history,
        "user_message": chat.message
    })

    # Save bot response to history
    await redis.rpush(history_key, f"Bot: {response}")
    await redis.ltrim(history_key, -10, -1)

    return {"bot_response": response}

# Run the application using: uvicorn main1:app --reload      