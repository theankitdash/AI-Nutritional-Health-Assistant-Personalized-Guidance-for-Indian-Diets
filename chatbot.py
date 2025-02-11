import ollama
from aioredis import Redis
import health_metrics        

async def generate_bot_response(user_message: str, session_id: str, redis_client: Redis) -> dict:
    # Default response
    bot_response = "I'm sorry, I don't understand. Can you please rephrase?"

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

    # 🔹 **DYNAMICALLY PASS ALL DETAILS TO TINYLLAMA**
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
        f"Bot: Answer the user's query based on the above information."
    )

    # **TinyLlama Generates Response Automatically**
    response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])["message"]["content"]

    return {"bot_response": response}
