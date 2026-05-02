from fastapi import APIRouter, HTTPException, Cookie
from app.models import (PersonalDetails, Preferences, HealthConditions)
from app.routers.auth import get_session_email
from app.db_connect import connect_db
from app.services.cache import clear_user_cache, clear_health_metrics_cache
import traceback
import asyncpg

router = APIRouter()

@router.post("/personal-details/")
async def add_personal_details(details: PersonalDetails, session_id: str = Cookie(None)):
    email = await get_session_email(session_id)
    
    conn = None
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
    
    except asyncpg.PostgresError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save personal details.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close()

    # Invalidate caches so next chat message fetches fresh data
    clear_user_cache(session_id)
    clear_health_metrics_cache(email)

    return {"message": "Personal details added successfully."}
    
@router.post("/preferences/")
async def add_preferences(preferences: Preferences, session_id: str = Cookie(None)):
    email = await get_session_email(session_id)

    conn = None
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
    
    except asyncpg.PostgresError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save preferences.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close()

    # Invalidate caches so next chat message fetches fresh data
    clear_user_cache(session_id)
    clear_health_metrics_cache(email)

    return {"message": "Food preferences saved successfully."}
    
@router.post("/health-conditions/")
async def add_health_conditions(health_conditions: HealthConditions, session_id: str = Cookie(None)):
    email = await get_session_email(session_id)

    data = health_conditions.model_dump(exclude_none=True)

    conn = None
    try:
        conn = await connect_db()

        # Remove PCOS field entirely for non-female users
        if 'pcos' in data:
            personal = await conn.fetchrow("SELECT gender FROM personal_details WHERE email=$1", email)
            if personal and personal['gender'].lower() != 'female':
                # Remove PCOS from data for non-female users
                data.pop('pcos')

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

    except asyncpg.PostgresError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to save health conditions.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close()

    # Invalidate caches so next chat message fetches fresh data
    clear_user_cache(session_id)
    clear_health_metrics_cache(email)

    return {"message": "Health conditions saved successfully."}
    
@router.get("/personal-details/")
async def get_personal_details(session_id: str = Cookie(None)):
    email = await get_session_email(session_id)

    conn = None
    try:
        conn = await connect_db()

        personal_details = await conn.fetchrow("SELECT * FROM personal_details WHERE email = $1", email)

        if not personal_details:
            return {}
        
        return {key: value for key, value in personal_details.items()}
        
    except asyncpg.PostgresError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error fetching personal details.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close() 
    
@router.get("/preferences/")
async def get_preferences(session_id: str = Cookie(None)):
    email = await get_session_email(session_id)

    conn = None
    try:
        conn = await connect_db()

        preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email = $1", email)

        if not preferences:
            return {}

        return {key: value for key, value in preferences.items()}

    except asyncpg.PostgresError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error fetching preferences.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close() 

@router.get("/health-conditions/")
async def get_health_conditions(session_id: str = Cookie(None)):
    email = await get_session_email(session_id)

    conn = None
    try:
        conn = await connect_db()

        health_conditions = await conn.fetchrow("SELECT * FROM health_conditions WHERE email = $1", email)

        if not health_conditions:
            return {}

        return {key: value for key, value in health_conditions.items()}

    except asyncpg.PostgresError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error fetching health conditions.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected error occurred.")
    finally:
        if conn:
            await conn.close()  