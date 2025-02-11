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
        weight = float(personal_details[b'weight'].decode("utf-8"))
        height = float(personal_details[b'height'].decode("utf-8"))
        dob = personal_details[b'date_of_birth'].decode("utf-8")
        gender = personal_details[b'gender'].decode("utf-8")
        age = health_metrics.calculate_age(dob)
        diet_preference = preferences[b'diet_preference'].decode("utf-8")
        allergies = health_conditions[b'allergies'].decode("utf-8")
        # fasting_glucose = float(personal_details[b'fasting_glucose'].decode("utf-8"))
        # post_meal_glucose = float(personal_details[b'post_meal_glucose'].decode("utf-8"))
        # vitamin_d = float(personal_details[b'vitamin_d'].decode("utf-8"))
        # calcium = float(personal_details[b'calcium'].decode("utf-8"))
        # sodium = float(personal_details[b'sodium'].decode("utf-8"))
        # potassium = float(personal_details[b'potassium'].decode("utf-8"))
        # waist = float(personal_details[b'waist'].decode("utf-8"))
    except KeyError:
        return {"bot_response": "Some details are missing in your profile. Please update your weight, height, date of birth, and gender."}

    # Recognize commands
    if "nutrition plan" in user_message.lower():
        bot_response = "Based on your profile, I can create a nutrition plan. Please specify your activity level (e.g., sedentary, moderately active)."

    elif "calculate bmi" in user_message.lower():
        bmi = health_metrics.calculate_bmi(weight, height)
        bot_response = f"Your BMI is {bmi:.2f}. A healthy BMI range is 18.5 to 24.9."

    elif "calculate bmr" in user_message.lower():
        bmr = health_metrics.calculate_bmr(weight, height, age, gender)
        bot_response = f"Your Basal Metabolic Rate (BMR) is {bmr:.2f} kcal/day."    

    elif "calculate bfp" in user_message.lower():
        bmi = health_metrics.calculate_bmi(weight, height)
        bfp = health_metrics.calculate_bfp_from_bmi(bmi, age, gender)
        bot_response = f"Your Body Fat Percentage (BFP) is {bfp}%. Ideal ranges vary, but generally below 25% for men and 30% for women is considered healthy."

    # elif "calculate visceral fat" in user_message.lower():
    #     visceral_fat = health_metrics.calculate_visceral_fat(weight, waist)
    #     bot_response = f"Your Visceral Fat level is {visceral_fat}%. High visceral fat can increase health risks."

    # elif "calculate waist-to-height ratio" in user_message.lower():
    #     whtr = health_metrics.calculate_whr(waist, height)
    #     bot_response = f"Your Waist-to-Height Ratio (WHtR) is {whtr}. A value above 0.5 may indicate higher health risks."

    elif "check lipid profile" in user_message.lower():
        total_cholesterol = float(personal_details[b'total_cholesterol'].decode("utf-8"))
        hdl = float(personal_details[b'hdl'].decode("utf-8"))
        ldl = float(personal_details[b'ldl'].decode("utf-8"))
        lipid_info = health_metrics.lipid_profile(total_cholesterol, hdl, ldl)
        bot_response = (f"Your Total Cholesterol: {lipid_info['total_cholesterol']} mg/dL, "
                        f"HDL: {lipid_info['hdl']} mg/dL, LDL: {lipid_info['ldl']} mg/dL. "
                        f"Cholesterol ratio: {lipid_info['cholesterol_ratio']:.2f}.")

    elif "calculate lean body mass" in user_message.lower():
        lbm = health_metrics.calculate_lbm(weight, height, gender)
        bot_response = f"Your Lean Body Mass (LBM) is {lbm} kg."

    elif "calculate metabolic age" in user_message.lower():
        bmr = health_metrics.calculate_bmr(weight, height, age, gender)
        metabolic_age = health_metrics.calculate_metabolic_age(bmr, age)
        bot_response = f"Your Metabolic Age is {metabolic_age} years."

    # elif "check blood sugar" in user_message.lower():
    #     sugar_levels = health_metrics.check_blood_sugar_level(fasting_glucose, post_meal_glucose)
    #     bot_response = (f"Fasting blood sugar level: {sugar_levels['fasting']}, "
    #                     f"Post-meal blood sugar level: {sugar_levels['post_meal']}.")

    elif "food allergy" in user_message.lower():
        allergy_insights = health_metrics.food_allergy_insights(allergies.split(","))
        bot_response = allergy_insights

    # elif "vitamin and mineral levels" in user_message.lower():
    #     vitamin_info = health_metrics.vitamin_mineral_levels(vitamin_d, calcium)
    #     bot_response = (f"Vitamin D status: {vitamin_info['vitamin_d_status']}, "
    #                     f"Calcium status: {vitamin_info['calcium_status']}.")

    elif "check hydration levels" in user_message.lower():
        hydration = health_metrics.hydration_level(weight)
        bot_response = f"Your recommended daily water intake is {hydration} mL."

    elif "check bone mineral density" in user_message.lower():
        bmd_status = health_metrics.bmd_status(age, gender)
        bot_response = bmd_status

    # elif "check electrolyte balance" in user_message.lower():
    #     electrolyte_info = health_metrics.electrolyte_balance(sodium, potassium)
    #     bot_response = (f"Sodium status: {electrolyte_info['sodium_status']}, "
    #                     f"Potassium status: {electrolyte_info['potassium_status']}.")

    # elif "track nutrients" in user_message.lower():
    #     try:
    #         food_items = [item.strip() for item in user_message.split(":")[1].split(",")]
    #         nutrients = health_metrics.track_nutrients(food_items, food_data)
    #         bot_response = (f"Nutrients from your food: {nutrients['calories']} kcal, "
    #                         f"{nutrients['protein']}g protein, {nutrients['carbs']}g carbs, "
    #                         f"{nutrients['fat']}g fat.")
    #     except Exception:
    #         bot_response = "I couldn't track nutrients. Ensure you provide a list of food items separated by commas."

    # Create a prompt for TinyLlama to process
    prompt = (
        f"User: {user_message}\n"
        f"User Profile: Weight: {weight} kg, Height: {height} cm, Age: {age}, Gender: {gender}, "
        f"Diet Preference: {diet_preference}, Allergies: {allergies}\n"
        f"Bot:"
    )

    # Get response from TinyLlama using Ollama
    bot_response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": prompt}])["message"]["content"]
    
    # Return response
    return {"bot_response": bot_response}
