import pandas as pd
import datetime
from aioredis import Redis

# Load dataset
DATASET_PATH = "Food_DATASET.csv"
food_data = pd.read_csv(DATASET_PATH)

def calculate_age(dob: str) -> int:
    birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    activity_map = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "super_active": 1.9,
    }
    return bmr * activity_map.get(activity_level.lower(), 1.2)

# Nutrient tracker using the dataset
def track_nutrients(food_items: list) -> dict:
    total_nutrients = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    for food in food_items:
        item = food_data[food_data['Food'].str.contains(food, case=False, na=False)]
        if not item.empty:
            total_nutrients["calories"] += item["Calories"].sum()
            total_nutrients["protein"] += item["Protein"].sum()
            total_nutrients["carbs"] += item["Carbs"].sum()
            total_nutrients["fat"] += item["Fat"].sum()
    return total_nutrients

# Main chatbot response generator
async def generate_bot_response(user_message: str, session_id: str, redis_client: Redis) -> dict:
    # Default response
    bot_response = "I'm sorry, I don't understand. Can you please rephrase?"

    # Fetch user details from Redis
    user_email = await redis_client.get(f"session:{session_id}")
    if not user_email:
        return {"bot_response": "Session expired or invalid. Please log in again."}

    user_email = user_email.decode("utf-8")
    personal_details = await redis_client.hgetall(f"personal_details:{user_email}")
    if not personal_details:
        return {"bot_response": "Your profile details are missing. Please update your profile."}

    try:
        weight = float(personal_details[b'weight'].decode("utf-8"))
        height = float(personal_details[b'height'].decode("utf-8"))
        dob = personal_details[b'date_of_birth'].decode("utf-8")
        gender = personal_details[b'gender'].decode("utf-8")
        age = calculate_age(dob)
    except KeyError:
        return {"bot_response": "Some details are missing in your profile. Please update your weight, height, date of birth, and gender."}

    # Recognize commands
    if "nutrition plan" in user_message.lower():
        bot_response = "Based on your profile, I can create a nutrition plan. Please specify your activity level (e.g., sedentary, moderately active)."

    elif "calculate bmi" in user_message.lower():
        bmi = weight / ((height / 100) ** 2)
        bot_response = f"Your BMI is {bmi:.2f}. A healthy BMI range is 18.5 to 24.9."

    elif "calculate bmr" in user_message.lower():
        bot_response = "Please specify your activity level (e.g., sedentary, lightly active) to calculate BMR and TDEE."

    elif "bmr" in user_message.lower():
        # User specifies activity level
        try:
            activity_level = user_message.split(":")[1].strip()
            bmr = calculate_bmr(weight, height, age, gender)
            tdee = calculate_tdee(bmr, activity_level)
            bot_response = f"Your BMR is {bmr:.2f} kcal/day, and your TDEE is {tdee:.2f} kcal/day for an {activity_level} lifestyle."
        except Exception:
            bot_response = "Could not calculate BMR/TDEE. Ensure you provide activity level like: sedentary, moderately active, etc."

    elif "track nutrients" in user_message.lower():
        try:
            food_items = [item.strip() for item in user_message.split(":")[1].split(",")]
            nutrients = track_nutrients(food_items)
            bot_response = (f"Nutrients from your food: {nutrients['calories']} kcal, "
                            f"{nutrients['protein']}g protein, {nutrients['carbs']}g carbs, "
                            f"{nutrients['fat']}g fat.")
        except Exception:
            bot_response = "I couldn't track nutrients. Ensure you provide a list of food items separated by commas."

    # Return response
    return {"bot_response": bot_response}