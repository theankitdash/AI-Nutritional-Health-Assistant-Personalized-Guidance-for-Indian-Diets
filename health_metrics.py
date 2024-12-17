import datetime

def calculate_age(dob: str) -> int:
    birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_bmi(weight: float, height: float) -> float:
    bmi = weight / ((height / 100) ** 2)
    return round(bmi, 2)

def calculate_bfp_from_bmi(bmi: float, age: int, gender: str) -> float:
    if gender.lower() == 'male':
        bfp = 1.20 * bmi + 0.23 * age - 16.2
    elif gender.lower() == 'female':
        bfp = 1.20 * bmi + 0.23 * age - 5.4
    return round(bfp, 2)

def calculate_visceral_fat(weight: float, waist: float) -> float:
    visceral_fat = (waist / weight) * 100
    return round(visceral_fat, 2)

def calculate_whr(waist: float, height: float) -> float:
    whtr = waist / height
    return round(whtr, 2)

def lipid_profile(total_cholesterol: float, hdl: float, ldl: float) -> dict:
    cholesterol_ratio = total_cholesterol / hdl
    return {
        'total_cholesterol': total_cholesterol,
        'hdl': hdl,
        'ldl': ldl,
        'cholesterol_ratio': round(cholesterol_ratio, 2)
    }

def calculate_lbm(weight: float, height: float, gender: str) -> float:
    if gender.lower() == 'male':
        lbm = 0.407 * weight + 0.267 * height - 19.2
    elif gender.lower() == 'female':
        lbm = 0.252 * weight + 0.473 * height - 48.3
    return round(lbm, 2)

def calculate_metabolic_age(bmr: float, age: int) -> int:
    if bmr > (age * 24):
        return age - 5
    elif bmr < (age * 24):
        return age + 5
    return age

def check_blood_sugar_level(fasting_glucose: float, post_meal_glucose: float) -> dict:
    result = {
        'fasting': 'normal' if 70 <= fasting_glucose <= 99 else 'high' if fasting_glucose > 99 else 'low',
        'post_meal': 'normal' if 140 <= post_meal_glucose <= 180 else 'high' if post_meal_glucose > 180 else 'low'
    }
    return result

def food_allergy_insights(allergy_list: list) -> str:
    if allergy_list:
        return f"Warning: Allergies detected: {', '.join(allergy_list)}."
    return "No food allergies detected."

def vitamin_mineral_levels(vitamin_d: float, calcium: float) -> dict:
    return {
        'vitamin_d_status': 'normal' if 30 <= vitamin_d <= 100 else 'deficient',
        'calcium_status': 'normal' if 8.5 <= calcium <= 10.5 else 'low'
    }

def hydration_level(weight: float) -> float:
    recommended_water = weight * 30
    return recommended_water

def bmd_status(age: int, gender: str) -> str:
    if gender == 'female' and age > 65:
        return "Osteoporosis risk: High"
    elif gender == 'male' and age > 70:
        return "Osteoporosis risk: High"
    return "Normal BMD"

def electrolyte_balance(sodium: float, potassium: float) -> dict:
    return {
        'sodium_status': 'normal' if 135 <= sodium <= 145 else 'abnormal',
        'potassium_status': 'normal' if 3.5 <= potassium <= 5.0 else 'abnormal'
    }

def track_nutrients(food_items: list, food_data) -> dict:
    total_nutrients = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    for food in food_items:
        item = food_data[food_data['Food'].str.contains(food, case=False, na=False)]
        if not item.empty:
            total_nutrients["calories"] += item["Calories"].sum()
            total_nutrients["protein"] += item["Protein"].sum()
            total_nutrients["carbs"] += item["Carbs"].sum()
            total_nutrients["fat"] += item["Fat"].sum()
    return total_nutrients
