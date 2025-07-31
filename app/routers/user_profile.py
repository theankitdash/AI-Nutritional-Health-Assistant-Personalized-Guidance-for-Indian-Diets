from fastapi import APIRouter, HTTPException, Cookie
from app.models import (PersonalDetails, Preferences, HealthConditions)
from app.routers.auth import validate_session
from app.db_connect import connect_db
from app.services.health_metrics_service import calculate_and_store_health_metrics
from app.services.faiss_utils import update_faiss_for_user
import traceback

router = APIRouter()

@router.post("/personal-details/")
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
        await update_faiss_for_user(email)

        return {"message": "Personal details added successfully."}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save personal details.")    
    
@router.post("/preferences/")
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
        await update_faiss_for_user(email)

        return {"message": "Food preferences saved successfully."}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save preferences.")    
    
@router.post("/health-conditions/")
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
        await update_faiss_for_user(email)

        return {"message": "Health conditions saved successfully."}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save health conditions.")    
    
@router.get("/personal-details/")
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
    
@router.get("/preferences/")
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

@router.get("/health-conditions/")
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