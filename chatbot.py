import ollama
from aioredis import Redis
import health_metrics
import os
import aiohttp
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")

USDA_API_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

async def fetch_nutrition_data_from_usda(query: str):
    """Fetch nutrition data from USDA API based on user input."""
    params = {"query": query, "api_key": USDA_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(USDA_API_URL, params=params) as response:
            if response.status == 200:
                return await response.json()
            return None

async def generate_bot_response(user_message: str, session_id: str, redis_client: Redis) -> dict:

    # Fetch user details from Redis
    user_email = await redis_client.get(f"session:{session_id}")
    if not user_email:
        return {"bot_response": "Session expired or invalid. Please log in again."}

    user_email = user_email.decode("utf-8")
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
        hydration = health_metrics.hydration_level(weight)

    except KeyError:
        return {"bot_response": "Some details are missing in your profile. Please update your weight, height, date of birth, and gender."}

    # Check if the query is related to nutrition
    if any(keyword in user_message.lower() for keyword in ["calories", "nutrients", "recipe", "meal plan", "diet"]):
        nutrition_data = await fetch_nutrition_data_from_usda(user_message)
        if nutrition_data:
            return {"bot_response": f"Here is the USDA-based nutrition information: {nutrition_data}"}
        return {"bot_response": "I'm unable to fetch nutrition details at the moment. Please try again later."}

    # 🔹 Construct a strict prompt for TinyLlama
    prompt = (
        f"User: {user_message}\n"
        f"User Profile:\n"
        f"- Name: {name}\n"
        f"- Weight: {weight} kg\n"
        f"- Height: {height} cm\n"
        f"- Age: {age} years\n"
        f"- Gender: {gender}\n"
        f"- BMI: {bmi:.2f}\n"
        f"- BMR: {bmr:.2f} kcal/day\n"
        f"- Body Fat Percentage (BFP): {bfp:.2f}%\n"
        f"- Lean Body Mass (LBM): {lbm:.2f} kg\n"
        f"- Hydration Level: {hydration} mL/day\n"
        f"- Preferences: {preferences_data}\n"
        f"- Health Conditions: {health_data}\n"
        f"Bot: Only respond using real-time suggestions, emotional support, or valid data from health metric calculations."
    )

    # **TinyLlama Generates Response Automatically**
    response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])["message"]["content"]

    return {"bot_response": response}
