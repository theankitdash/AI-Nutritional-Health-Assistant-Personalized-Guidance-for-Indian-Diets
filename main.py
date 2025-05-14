from fastapi import FastAPI, HTTPException, Request, Cookie
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.documents import Document
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from db_connect import connect_db
from models import (UserCredentials, PasswordUpdate, PersonalDetails, Preferences, HealthConditions, HealthMetrics, ChatRequest)
import health_metrics
import asyncpg
import uuid
import bcrypt 

import os
import json
import faiss
import os
import traceback

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

app = FastAPI()
"""
# Initialize the LLM
LLM = OllamaLLM(model="gemma:2b")

"""
LLM = ChatNVIDIA(
  model="google/gemma-7b",
  api_key=NVIDIA_API_KEY, 
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
)


# Load FAISS index
index = faiss.read_index("food_dataset/index.faiss")

# Load texts from JSON
with open("food_dataset/index.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

# Convert to LangChain documents
documents = [Document(page_content=txt) for txt in texts]

# Create docstore and ids
docstore = InMemoryDocstore(dict(zip([str(i) for i in range(len(texts))], documents)))
index_to_docstore_id = {i: str(i) for i in range(len(texts))}

# Build FAISS vectorstore manually — no pickle, no deserialization flag needed
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

faiss_index = FAISS(
    embedding_function=embedding,
    index=index,
    docstore=docstore,
    index_to_docstore_id=index_to_docstore_id,
)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("static/index.html")

@app.post("/register/")
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

@app.post("/login/")
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
    
@app.get("/check-login/")
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
        
@app.post("/logout/")
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
    
@app.put("/update-password/")
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
    
@app.post("/personal-details/")
async def add_personal_details(details: PersonalDetails, session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        conn = await connect_db()

        # Upsert into personal_details table
        await conn.execute("""
            INSERT INTO personal_details (email, name, dateofbirth, gender, height, weight, waist)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (email)
            DO UPDATE SET 
                name = EXCLUDED.name,
                dateofbirth = EXCLUDED.dateofbirth,
                gender = EXCLUDED.gender,
                height = EXCLUDED.height,
                weight = EXCLUDED.weight,
                waist = EXCLUDED.waist;
        """, email, *details.model_dump().values())

        await conn.close()

        await calculate_and_store_health_metrics(email)

        return {"message": "Personal details added successfully."}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save personal details.")    
    
@app.post("/preferences/")
async def add_preferences(preferences: Preferences, session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        conn = await connect_db()

        await conn.execute("""
            INSERT INTO preferences (
                email, foodPreference, snackPreferences, mealTimings, cheatDayFrequency,
                culturalPreferences, preferredIngredients, cuisinePreferences, spicyFoodTolerance,
                preferredMealType, favoriteMeal, mealFrequency, sweetPreference,
                eatingOutFrequency, hydrationLevel, preferredDrinks, activityLevel,
                fitnessGoal, foodRestrictions, caffeineIntake, averageSleep,
                sleepQuality, supplementUsage, supplementFrequency
            )
            VALUES (
                $1, $2, $3, $4, $5,
                $6, $7, $8, $9,
                $10, $11, $12, $13,
                $14, $15, $16, $17,
                $18, $19, $20, $21,
                $22, $23, $24
            )
            ON CONFLICT (email)
            DO UPDATE SET
                foodpreference = EXCLUDED.foodpreference, snackpreferences = EXCLUDED.snackpreferences,
                mealtimings = EXCLUDED.mealtimings, cheatdayfrequency = EXCLUDED.cheatdayfrequency,
                culturalpreferences = EXCLUDED.culturalpreferences, preferredingredients = EXCLUDED.preferredingredients,
                cuisinepreferences = EXCLUDED.cuisinepreferences, spicyfoodtolerance = EXCLUDED.spicyfoodtolerance,
                preferredmealtype = EXCLUDED.preferredmealtype, favoritemeal = EXCLUDED.favoritemeal,
                mealfrequency = EXCLUDED.mealfrequency, sweetpreference = EXCLUDED.sweetpreference,
                eatingoutfrequency = EXCLUDED.eatingoutfrequency, hydrationlevel = EXCLUDED.hydrationlevel,
                preferreddrinks = EXCLUDED.preferreddrinks, activitylevel = EXCLUDED.activitylevel,
                fitnessgoal = EXCLUDED.fitnessgoal, foodrestrictions = EXCLUDED.foodrestrictions, 
                caffeineintake = EXCLUDED.caffeineintake, averagesleep = EXCLUDED.averagesleep,
                sleepquality = EXCLUDED.sleepquality, supplementusage = EXCLUDED.supplementusage,
                supplementfrequency = EXCLUDED.supplementfrequency;
        """, email, *preferences.model_dump().values())

        await conn.close()

        await calculate_and_store_health_metrics(email)

        return {"message": "Food preferences saved successfully."}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save preferences.")    
    
@app.post("/health-conditions/")
async def add_health_conditions(health_conditions: HealthConditions, session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    data = health_conditions.model_dump(exclude_none=True)

    try:
        conn = await connect_db()

        # Manually build query to account for optional fields
        columns = ', '.join(['email'] + list(data.keys()))
        placeholders = ', '.join([f"${i+1}" for i in range(len(data) + 1)])
        updates = ', '.join([f"{k} = EXCLUDED.{k}" for k in data.keys()])

        values = [email] + list(data.values())

        query = f"""
            INSERT INTO health_conditions ({columns})
            VALUES ({placeholders})
            ON CONFLICT (email)
            DO UPDATE SET {updates};
        """

        await conn.execute(query, *values)
        await conn.close()

        await calculate_and_store_health_metrics(email)

        return {"message": "Health conditions saved successfully."}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save health conditions.")    
    
async def calculate_and_store_health_metrics(email: str):
    try:
        conn = await connect_db()

        # Fetch data from personal_details, preferences, and health_conditions tables
        personal_details = await conn.fetchrow("SELECT * FROM personal_details WHERE email = $1", email)
        preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email = $1", email)
        health_conditions = await conn.fetchrow("SELECT * FROM health_conditions WHERE email = $1", email)

        if not personal_details or not preferences or not health_conditions:
            await conn.close()
            raise HTTPException(status_code=404, detail="User profile is incomplete. Please update all the details.")

        # Decode data into appropriate classes
        personal_details_data = PersonalDetails(**personal_details)
        preferences_data = Preferences(**preferences)
        health_data = HealthConditions(**health_conditions)

        # Calculate Health Metrics
        age = health_metrics.calculate_age(personal_details_data.dateofbirth)
        bmi = health_metrics.calculate_bmi(personal_details_data.weight, personal_details_data.height)
        bmr = health_metrics.calculate_bmr(personal_details_data.weight, personal_details_data.height, age, personal_details_data.gender)
        tdee = health_metrics.calculate_tdee(bmr, preferences_data.activitylevel)
        bfp = health_metrics.calculate_bfp(bmi, age, personal_details_data.gender)
        lbm = health_metrics.calculate_lbm(personal_details_data.weight, bfp)
        muscle_mass = health_metrics.calculate_muscle_mass(lbm)
        visceral_fat = health_metrics.calculate_visceral_fat(bfp, personal_details_data.waist, personal_details_data.height)
        whr = health_metrics.calculate_whtr(personal_details_data.waist, personal_details_data.height)
        metabolic_age = health_metrics.calculate_metabolic_age(lbm, bmr, age)
        hydration_level = health_metrics.calculate_hydration_level(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age)
        protein_intake = health_metrics.calculate_protein_intake(preferences_data.activitylevel, preferences_data.fitnessgoal, lbm)
        macro_nutrients = health_metrics.calculate_macronutrients(tdee, preferences_data.fitnessgoal, personal_details_data.gender)
        micro_nutrients = health_metrics.calculate_micronutrients(preferences_data.fitnessgoal, age, personal_details_data.gender, preferences_data.activitylevel)
        energy_surplus_deficit = health_metrics.calculate_energy_surplus_deficit(tdee, preferences_data.fitnessgoal)
        #glycemic_index=health_metrics.glycemic_index_load(preferences_data.foodPreference),  # To be updated later
        bmd = health_metrics.calculate_bmd(personal_details_data.weight, personal_details_data.height, age, bfp, personal_details_data.gender)
        max_heart_rate = health_metrics.calculate_max_heart_rate(age)
        electrolyte_balance = health_metrics.calculate_electrolyte_balance(age, personal_details_data.gender, preferences_data.activitylevel, preferences_data.fitnessgoal)
        #body_water_percentage=health_metrics.calculate_body_water_percentage(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age, bfp, preferences_data.activityLevel)
        skeletal_mass = health_metrics.calculate_skeletal_muscle_mass(lbm)
        #protein_absorption=health_metrics.calculate_protein_absorption(health_metrics.calculate_protein_intake, preferences_data.foodPreference),  # To be updated later
        #metabolic_flexibility=health_metrics.calculate_metabolic_flexibility(preferences_data.activityLevel, preferences_data.foodPreference),  # To be updated later
    
        sleep_score = health_metrics.calculate_sleep_score(preferences_data.averagesleep)
        fiber = health_metrics.daily_fiber_intake(age, personal_details_data.gender, preferences_data.activitylevel, preferences_data.fitnessgoal)

        health_metrics_data = HealthMetrics(
            age=age, bmi=bmi, bmr=bmr, tdee=tdee, bfp=bfp, lbm=lbm, muscle_mass=muscle_mass, visceral_fat=visceral_fat,
            whr=whr, metabolic_age=metabolic_age, hydration_level=hydration_level, protein_intake=protein_intake, 
            macro_nutrients=macro_nutrients, micro_nutrients=micro_nutrients, energy_surplus_deficit=energy_surplus_deficit,
            bmd=bmd, max_heart_rate=max_heart_rate, electrolyte_balance=electrolyte_balance, skeletal_mass=skeletal_mass, 
            sleep_score=sleep_score, fiber=fiber
        )

        # Insert or update health metrics in PostgreSQL
        await conn.execute("""
            INSERT INTO health_metrics (
                email, age, bmi, bmr, tdee, bfp, lbm, muscle_mass, visceral_fat, whr, metabolic_age, hydration_level,
                protein_intake, macro_nutrients, micro_nutrients, energy_surplus_deficit, bmd, max_heart_rate, electrolyte_balance,
                skeletal_mass, sleep_score, fiber
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22
            )
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age, bmi = EXCLUDED.bmi, bmr = EXCLUDED.bmr, tdee = EXCLUDED.tdee, bfp = EXCLUDED.bfp,
                lbm = EXCLUDED.lbm, muscle_mass = EXCLUDED.muscle_mass, visceral_fat = EXCLUDED.visceral_fat, whr = EXCLUDED.whr,
                metabolic_age = EXCLUDED.metabolic_age, hydration_level = EXCLUDED.hydration_level, protein_intake = EXCLUDED.protein_intake,
                macro_nutrients = EXCLUDED.macro_nutrients, micro_nutrients = EXCLUDED.micro_nutrients, energy_surplus_deficit = EXCLUDED.energy_surplus_deficit,
                bmd = EXCLUDED.bmd, max_heart_rate = EXCLUDED.max_heart_rate, electrolyte_balance = EXCLUDED.electrolyte_balance,
                skeletal_mass = EXCLUDED.skeletal_mass, sleep_score = EXCLUDED.sleep_score, fiber = EXCLUDED.fiber
        """, email, *health_metrics_data.model_dump().values())

        await conn.close()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error calculating or storing health metrics.")    
    
@app.get("/personal-details/")
async def get_personal_details(session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        # Connect to PostgreSQL
        conn = await connect_db()

        # Retrieve personal details from PostgreSQL
        personal_details = await conn.fetchrow("SELECT * FROM personal_details WHERE email = $1", email)

        # Close the connection
        await conn.close()

        if not personal_details:
            raise HTTPException(status_code=404, detail="User not found.")

        # Return the personal details
        return {key: value for key, value in personal_details.items()}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching personal details.")    
    
@app.get("/preferences/")
async def get_preferences(session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        # Connect to PostgreSQL
        conn = await connect_db()

        # Retrieve preferences from PostgreSQL
        preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email = $1", email)

        # Close the connection
        await conn.close()

        if not preferences:
            raise HTTPException(status_code=404, detail="Preferences not found.")

        # Return the preferences
        return {key: value for key, value in preferences.items()}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching preferences.") 

@app.get("/health-conditions/")
async def get_health_conditions(session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        # Connect to PostgreSQL
        conn = await connect_db()

        # Retrieve health conditions from PostgreSQL
        health_conditions = await conn.fetchrow("SELECT * FROM health_conditions WHERE email = $1", email)

        # Close the connection
        await conn.close()

        if not health_conditions:
            raise HTTPException(status_code=404, detail="Health conditions not found.")

        # Return the health conditions
        return {key: value for key, value in health_conditions.items()}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching health conditions.")       
    
@app.post("/chat/")
async def chat_with_bot(chat: ChatRequest, session_id: str = Cookie(None)):
    email = await validate_session(session_id)

    try:
        # Connect to PostgreSQL
        conn = await connect_db()

        # Retrieve user data from PostgreSQL
        personal = await conn.fetchrow("SELECT * FROM personal_details WHERE email = $1", email)
        prefs = await conn.fetchrow("SELECT * FROM preferences WHERE email = $1", email)
        conditions = await conn.fetchrow("SELECT * FROM health_conditions WHERE email = $1", email)
        metrics = await conn.fetchrow("SELECT * FROM health_metrics WHERE email = $1", email)

       # Build user context
        user_context = f"""
        Personal Details:
        Name: {personal.get("name")}, Age: {health_metrics.calculate_age(personal.get("dateofbirth"))}, Gender: {personal.get("gender")}
        Height: {personal.get("height")} cm, Weight: {personal.get("weight")} kg, Waist: {personal.get("waist")} cm

        Preferences:
        Food Preference: {prefs.get("foodpreference")}, Snack Preference: {prefs.get("snackpreferences")}, Meal Timings: {prefs.get("mealtimings")}
        Activity Level: {prefs.get("activitylevel")}, Fitness Goal: {prefs.get("fitnessgoal")}, Cultural Preferences: {prefs.get("culturalpreferences")}, Cuisine Preferences: {prefs.get("cuisinepreferences")}
        Spicy Food Tolerance: {prefs.get("spicyfoodtolerance")}, Preferred Meal Type: {prefs.get("preferredmealtype")}
        Favorite Meal: {prefs.get("favoritemeal")}, Meal Frequency: {prefs.get("mealfrequency")}, Sweet Preference: {prefs.get("sweetpreference")}

        Health Conditions:
        Allergies: {conditions.get("allergies")}, Diabetes: {conditions.get("diabetes")}, Hypertension: {conditions.get("hypertension")}
        Other: {conditions.get("otherconditions")}, PCOS: {conditions.get("pcos")}, Anemia: {conditions.get("anemia")}
        Osteoporosis: {conditions.get("osteoporosis")}, IBS: {conditions.get("ibs")}, GERD: {conditions.get("gerd")}

        Metrics:
        BMI: {metrics.get("bmi")}, BMR: {metrics.get("bmr")}, TDEE: {metrics.get("tdee")}
        Body Fat Percentage: {metrics.get("bfp")}, Hydration Level: {metrics.get("hydration_level")}
        Muscle Mass: {metrics.get("muscle_mass")}, Sleep Score: {metrics.get("sleep_score")}, Fiber Intake: {metrics.get("fiber")}
        Protein Intake: {metrics.get("protein_intake")}, Macro Nutrients: {metrics.get("macro_nutrients")}, Micro Nutrients: {metrics.get("micro_nutrients")}
        Energy Surplus/Deficit: {metrics.get("energy_surplus_deficit")}, Electrolyte Balance: {metrics.get("electrolyte_balance")}

        """    
        # Retrieve last 10 messages from PostgreSQL chat history table
        history = await conn.fetch("SELECT message FROM chat_history WHERE email = $1 ORDER BY timestamp DESC LIMIT 10", email)

        conversation_history = "\n".join([msg['message'] for msg in reversed(history)]) if history else "No previous conversation."

        # Add new user message to history
        timestamp = datetime.now(timezone.utc)
        await conn.execute("INSERT INTO chat_history (email, message, timestamp) VALUES ($1, $2, $3)", email, f"User: {chat.message}", timestamp)

        # Search FAISS index
        retrieved_docs = faiss_index.similarity_search(chat.message, k=3)

        # Combine the retrieved documents into a string
        retrieved_context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Create the prompt
        prompt_template = PromptTemplate(
            input_variables=["user_context", "retrieved_context", "conversation_history", "user_message"],
            template=""" 
            You are a personalized nutrition assistant specialized in Indian dietary habits. 
            Use the user's health metrics, preferences, and health conditions to respond naturally.

            *User Profile*:
            {user_context}

            *Indian Nutrition Database*:
            {retrieved_context}

            *User's Current Message*:
            {user_message}

            Reply in a friendly, knowledgeable, and contextual way based on the above info.
            """
        )

        chain = prompt_template | LLM

        bot_response = chain.invoke({
            "user_context": user_context,
            "retrieved_context": retrieved_context,
            "user_message": chat.message
        })

        if isinstance(bot_response, BaseMessage):
            response = bot_response.content
        else:
            response = str(bot_response)

        # Save bot response to history
        await conn.execute("INSERT INTO chat_history (email, message, timestamp) VALUES ($1, $2, $3)", email, f"Bot: {response}", timestamp)

        return {"bot_response": response}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error processing the chat request.")  
    finally:
        await conn.close() 

# Run the application using: uvicorn main:app --reload      