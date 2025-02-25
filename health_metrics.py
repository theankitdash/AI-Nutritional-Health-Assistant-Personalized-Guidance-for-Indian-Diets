import datetime

# Age
def calculate_age(dob: str) -> int:
    birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# BMI
def calculate_bmi(weight: float, height: float, age) -> dict: 
    bmi = weight / ((height / 100) ** 2), 2

    return round(bmi,2)

# Basal Metabolic Rate (BMR)
def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    
    gender = gender.lower()

    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Invalid gender. Please enter 'male' or 'female'.")

    return round(bmr,2)

# Total Daily Energy Expenditure (TDEE)
def calculate_tdee(bmr: float, activity_level: str ) -> float:
 
    activity_factors = {
        "Sedentary": 1.2,  # Little to no exercise
        "Lightly Active": 1.375,  # Light exercise 1-3 days/week
        "Moderately Active": 1.55,  # Moderate exercise 3-5 days/week
        "Very Active": 1.725,  # Hard exercise 6-7 days/week
    }

    if activity_level not in activity_factors:
        raise ValueError("Invalid activity level. Choose from 'Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', or 'Super Active'.")

    tdee = bmr * activity_factors[activity_level]

    return round(tdee,2)

# Body Fat Percentage (BFP)
def calculate_bfp(bmi: float, age: int, gender: str) -> float:

    gender = gender.lower()
    
    if gender == 'male':
        gender_value = 1
    elif gender == 'female':
        gender_value = 0
    else:
        raise ValueError("Invalid gender. Please enter 'male' or 'female'.")
    
    bfp = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_value) - 5.4

    return round(bfp, 2)

# Lean Body Mass
def calculate_lbm(weight: float, bfp: float) -> float:
    
    lbm = weight * (1 - (bfp / 100))

    return round(lbm,2)

# Muscle Mass
def calculate_muscle_mass(lbm: float) -> float:

    muscle_mass = lbm * 0.50

    return round(muscle_mass, 2)


# Visceral Fat
def calculate_visceral_fat(bfp: float, waist: float, height: float) -> float:
    
    visceral_fat = ((waist / height) * 10) + (bfp / 10)
    return round(visceral_fat, 2)

# Waist-to-Height Ratio (WHtR)
def calculate_whtr(waist: float, height: float) -> float:
    
    wht_ratio = waist / height
    return round(wht_ratio, 2)

# Metabolic Age
def calculate_metabolic_age(lbm: float, bmr: float, age: int) -> float:

    avg_bmr = (21.6 * lbm) + 370  

    # Metabolic Age Calculation
    metabolic_age = (bmr / avg_bmr) * age
   
    return round(metabolic_age, 2)

# Hydration Level
def calculate_hydration_level(weight: float, height: float, gender: str, age: int) -> float:
    
    if gender == "male":
        tbw = (2.447 * weight) + (0.3362 * height) - (0.1074 * age) + 0.09156
    elif gender == "female":
        tbw = (-2.097 * weight) + (0.2466 * height) - (0.1069 * age) + 0.1069

    hydration_level = (tbw / weight) * 100

    return round(hydration_level, 2)

# Protein Requirement
def calculate_protein_intake(activity_level: str,  goal: str, lbm: float) -> float:

    activity_factors = {
        "sedentary": 1.2,   # Reduced protein needs for low activity
        "lightly active": 1.4,
        "moderately active": 1.6,
        "very active": 1.8
    }

    goal_factors = {
        "general well-being": 1.0,  # Standard protein intake for overall health
        "maintenance": 1.1,         # Slightly higher for sustaining muscle
        "muscle gain": 1.3,         # Higher intake for muscle building
        "weight loss": 1.2          # Increased intake to preserve muscle
    }

    activity_level = activity_level.lower()
    goal = goal.lower()

    if activity_level not in activity_factors or goal not in goal_factors:
        raise ValueError("Invalid activity level or goal. Choose valid options.")
    
    # Calculate daily protein intake
    protein_intake = lbm * (activity_factors[activity_level] + goal_factors[goal])
    
    return round(protein_intake, 2)

# Macronutrient Breakdown
def calculate_macronutrients(tdee: float, goal: str, gender:str) -> dict:
    
    goal = goal.lower()
    gender = gender.lower()

    # Macronutrient split based on goals
    macro_splits = {
        "weight loss": {"carbs": 0.40, "protein": 0.30, "fats": 0.30},
        "muscle gain": {"carbs": 0.50, "protein": 0.25, "fats": 0.25},
        "maintenance": {"carbs": 0.50, "protein": 0.20, "fats": 0.30},
        "general wellbeing": {"carbs": 0.45, "protein": 0.25, "fats": 0.30}
    }

    if goal not in macro_splits:
        raise ValueError("Invalid goal. Choose from: Weight Loss, Muscle Gain, Maintenance, General Wellbeing.")

    # Get the macro percentages
    macros = macro_splits[goal]

    # Gender Adjustments
    if gender == "female":
        macros["protein"] -= 0.02  # Slightly lower protein
        macros["fats"] += 0.02     # Slightly higher fat for hormonal health
    elif gender == "male":
        macros["protein"] += 0.02  # Slightly higher protein
        macros["fats"] -= 0.02     # Slightly lower fat

    # Convert to grams
    protein_g = round((macros["protein"] * tdee) / 4, 2)
    carbs_g = round((macros["carbs"] * tdee) / 4, 2)
    fats_g = round((macros["fats"] * tdee) / 9, 2)

    return {"Protein (g)": protein_g, "Carbohydrates (g)": carbs_g, "Fats (g)": fats_g}

# Micronutrient Requirements (Basic)
def calculate_micronutrients(goal:str, age: int, gender: str, activity_level: str) -> dict:
    
    goal = goal.lower()
    gender = gender.lower()
    activity_level = activity_level.lower()

     # Base micronutrient recommendations
    micronutrients = {
        "Vitamin A (mcg)": 900,
        "Vitamin D (IU)": 800,
        "Vitamin E (mg)": 15,
        "Vitamin K (mcg)": 120,
        "Vitamin C (mg)": 90,
        "Vitamin B1 (Thiamine, mg)": 1.2,
        "Vitamin B2 (Riboflavin, mg)": 1.3,
        "Vitamin B3 (Niacin, mg)": 16,
        "Vitamin B5 (Pantothenic Acid, mg)": 5,
        "Vitamin B6 (mg)": 1.3,
        "Vitamin B7 (Biotin, mcg)": 30,
        "Vitamin B9 (Folate, mcg)": 400,
        "Vitamin B12 (mcg)": 2.4,
        "Calcium (mg)": 1000,
        "Magnesium (mg)": 400,
        "Potassium (mg)": 3500,
        "Sodium (mg)": 2000,
        "Phosphorus (mg)": 700,
        "Iron (mg)": 8,
        "Zinc (mg)": 11,
        "Copper (mcg)": 900,
        "Selenium (mcg)": 55,
        "Iodine (mcg)": 150,
        "Choline (mg)": 550, 
        "Fluoride (mg)": 4,   
        "Manganese (mg)": 2.3, 
        "Chromium (mcg)": 35, 
        "Molybdenum (mcg)": 45 
    }

    # Adjustments based on goal
    if goal == "weight loss":
        micronutrients["Vitamin D (IU)"] += 200
        micronutrients["Magnesium (mg)"] += 50
        micronutrients["Omega-3 (mg)"] = 1000
        micronutrients["Sodium (mg)"] = 1500

    elif goal == "muscle gain":
        micronutrients["Vitamin D (IU)"] += 300
        micronutrients["Zinc (mg)"] += 5
        micronutrients["Vitamin B12 (mcg)"] += 0.6
        micronutrients["Magnesium (mg)"] += 50
        micronutrients["Omega-3 (mg)"] = 1200
        micronutrients["Choline (mg)"] += 50  

    elif goal == "maintenance":
        micronutrients["Vitamin C (mg)"] += 10
        micronutrients["Vitamin E (mg)"] += 5
        micronutrients["Potassium (mg)"] += 200

    # Adjustments based on gender
    if gender == "female":
        micronutrients["Iron (mg)"] = 18
        micronutrients["Calcium (mg)"] = 1200
        micronutrients["Folate (mcg)"] = 600
        micronutrients["Choline (mg)"] = 425  

    # Adjustments based on age
    if age > 50:
        micronutrients["Vitamin D (IU)"] += 200
        micronutrients["Calcium (mg)"] = 1200

    # Adjustments based on activity level
    if activity_level in ["very active", "moderately active"]:
        micronutrients["Magnesium (mg)"] += 50
        micronutrients["Potassium (mg)"] += 300
        micronutrients["Manganese (mg)"] += 0.5  # Supports muscle function
        micronutrients["Chromium (mcg)"] += 5  # Helps energy metabolism

    return micronutrients


# Energy Surplus/Deficit
def calculate_energy_surplus_deficit(tdee: float, goal: str) -> dict:

    # Normalize input
    goal = goal.lower()

     # Adjusted calorie intake based on goal
    energy_adjustments = {
        "weight loss": -500,  # Moderate deficit (~0.5 kg/week)
        "muscle gain":  300,  # Moderate surplus (~0.3 kg/week)
        "maintenance":  0,    # No change
        "general wellbeing":  0  # Keep TDEE as is
    }
    
    if goal not in energy_adjustments:
        raise ValueError("Invalid goal. Choose from: Weight Loss, Muscle Gain, Maintenance, General Wellbeing.")

    adjusted_calories = tdee + energy_adjustments[goal]

    return round(adjusted_calories)

# Glycemic Index & Load
def glycemic_index_load(food: str, portion_size: float) -> dict:

    food = food.lower()

    food_data ={}

    gi = food_data[food]["gi"]
    carbs = (food_data[food]["carbs"] * portion_size) / 100  # Adjust for portion size

    glycemic_load = round((gi * carbs) / 100, 2)

    # GI & GL Categories
    gi_category = "Low" if gi <= 55 else "Medium" if gi <= 70 else "High"
    gl_category = "Low" if glycemic_load < 10 else "Medium" if glycemic_load < 20 else "High"

    return {
        "Food": food.title(),
        "Portion Size (g)": portion_size,
        "Glycemic Index": gi,
        "GI Category": gi_category,
        "Carbohydrates (g)": round(carbs, 2),
        "Glycemic Load": glycemic_load,
        "GL Category": gl_category
    }

# Bone Mineral Density (BMD)
def calculate_bmd(weight: float, height: float, age: int, bfp: float, gender: str) -> dict:
    
    gender = gender.lower()

    if gender == "male":
        k = 2.9
    elif gender == "female":
        k = 2.8

    # BMD Calculation Formula
    bmd = (0.2 * weight) + (0.07 * height) - (0.2 * age) - (0.15 * bfp) + k

    # Bone Health Categories (T-Score Approximation)
    if bmd >= 1:
        category = "Normal"
    elif -1 < bmd < 1:
        category = "Osteopenia (Low Bone Mass)"
    else:
        category = "Osteoporosis (Very Low Bone Mass)"

    return {
        "Bone Mineral Density (BMD)": round(bmd, 2),
        "Bone Health Category": category
    }

# Resting Heart Rate 
def calculate_resting_heart_rate(age: int, fitness_level: str) -> dict:
    """
    Estimates Resting Heart Rate (RHR) based on age and fitness level.

    :param age: Age in years
    :param fitness_level: 'Athlete', 'Excellent', 'Good', 'Average', 'Below Average', 'Poor'
    :return: Estimated RHR and heart health category
    """
    fitness_level = fitness_level.strip().title()  # Normalize input

    rhr_ranges = {
        "Athlete": (40, 54),
        "Excellent": (55, 64),
        "Good": (65, 72),
        "Average": (73, 78),
        "Below Average": (79, 84),
        "Poor": (85, 100)
    }

    if fitness_level not in rhr_ranges:
        return {"Error": "Invalid fitness level. Choose from 'Athlete', 'Excellent', 'Good', 'Average', 'Below Average', 'Poor'."}

    # Base RHR range from fitness level
    rhr_min, rhr_max = rhr_ranges[fitness_level]
    
    # Adjust RHR based on age (older adults tend to have higher RHR)
    age_adjustment = 0
    if age > 40:
        age_adjustment = (age - 40) // 10 * 2  # +2 bpm for every 10 years over 40

    adjusted_min = rhr_min + age_adjustment
    adjusted_max = rhr_max + age_adjustment
    avg_rhr = round((adjusted_min + adjusted_max) / 2)

    return {
        "Fitness Level": fitness_level,
        "Age": age,
        "Estimated RHR (bpm)": avg_rhr,
        "Healthy Range (bpm)": f"{adjusted_min} - {adjusted_max}"
    }

# Max Heart Rate
def calculate_max_heart_rate(age: int) -> int:
    return 220 - age

# Body Water Percentage (BWP)
def calculate_body_water_percentage(weight: float, height: float, gender: str, age: int, bfp: float, activity: str, electrolyte: str) -> float:
    
    gender = gender.lower()
    activity = activity.lower()
    electrolyte = electrolyte.lower()

    # Assign coefficients based on gender
    if gender == "male":
        A, B, C, D, E = 0.60, 0.01, 0.02, 0.10, -5.4
    elif gender == "female":
        A, B, C, D, E = 0.50, 0.01, 0.02, 0.10, -2.7

    # Activity Factor
    activity_levels = {
        "sedentary": 0.0,
        "lightly active": 0.5,
        "moderately active": 1.0,
        "very active": 1.5
    }

    # Electrolyte Balance Adjustment
    electrolyte_levels = {
        "Optimal": 0.0,
        "moderate deficiency": -1.5,
        "deficient": -3.0,
        "severe deficiency": -5.0
    }

    electrolyte_adjustment = electrolyte_levels[electrolyte]

    activity_factor = activity_levels[activity]

    # Calculate Total Body Water (TBW)
    tbw = (weight * A) + (height * B) - (age * C) - (bfp * D) + E + activity_factor + electrolyte_adjustment

    # Calculate Body Water Percentage (BWP)
    bwp = (tbw / weight) * 100

    return round(bwp,2)

# Skeletal Muscle Mass (SMM)
def calculate_skeletal_muscle_mass(lbm: float) -> dict:

    smm = lbm * 0.52

    return round(smm, 2)

# Protein Absorption Efficiency
def calculate_protein_absorption(protein_intake: float, food: str) -> float:
    
    # Protein digestibility based on common foods
    digestibility_factors = {
        "whey protein": 0.97,
        "egg": 0.97,
        "chicken breast": 0.92,
        "fish": 0.92,
        "milk": 0.90,
        "cheese": 0.89,
        "yogurt": 0.88,
        "soybeans": 0.88,
        "tofu": 0.85,
        "lentils": 0.80,
        "beans": 0.75,
        "quinoa": 0.75,
        "brown rice": 0.70,
        "almonds": 0.65,
        "vegetables": 0.60
    }
    
    food = food.lower()
    
    if food not in digestibility_factors:
        raise ValueError("Invalid food item. Please enter a common protein source like 'chicken breast', 'lentils', 'tofu', etc.")

    absorbed_protein = protein_intake * digestibility_factors[food]
    efficiency = (absorbed_protein / protein_intake) * 100
    
    return round(efficiency, 2)

# Metabolic Flexibility – Fat vs. Carb Burning
def calculate_metabolic_flexibility(activity_level: str, diet_type: str) -> float:

    # Activity Level Influence
    activity_rer = {
        "sedentary": 0.95,
        "lightly active": 0.90,
        "moderately active": 0.85,
        "very active": 0.80,
    }

    # Diet Influence
    diet_rer = {
        "high-carb": 0.05,
        "balanced": 0.00,
        "low-carb": -0.05,
        "keto": -0.10
    }

    # Validate input
    if activity_level not in activity_rer or diet_type not in diet_rer:
        raise ValueError("Invalid input. Choose correct activity level and diet type.")

    # Calculate Estimated RER
    estimated_rer = activity_rer[activity_level] + diet_rer[diet_type]

    # Keep RER within physiological range (0.7 - 1.0)
    estimated_rer = max(0.7, min(estimated_rer, 1.0))
    
    mf_score = round(1 - abs(estimated_rer - 0.85), 2)

    # Classify Metabolic Flexibility
    if mf_score >= 0.9:
        flexibility_status = "Excellent"
    elif 0.75 <= mf_score < 0.9:
        flexibility_status = "Good"
    elif 0.6 <= mf_score < 0.75:
        flexibility_status = "Moderate"
    else:
        flexibility_status = "Poor"

    return mf_score

# Electrolyte Balance – Sodium, Potassium, Magnesium
def calculate_electrolyte_balance(sodium: float, potassium: float, magnesium: float, calcium: float) -> dict:

    # Recommended Daily Intake (RDI) - Reference values in mg
    rdi = {"sodium": 2300, "potassium": 4700, "magnesium": 420, "calcium": 1300}

    # Calculate intake percentage
    sodium_pct = (sodium / rdi["sodium"]) * 100
    potassium_pct = (potassium / rdi["potassium"]) * 100
    magnesium_pct = (magnesium / rdi["magnesium"]) * 100
    calcium_pct = (calcium / rdi["calcium"]) * 100

    # Electrolyte Balance Score (Average of all % intakes)
    electrolyte_score = (sodium_pct + potassium_pct + magnesium_pct + calcium_pct) / 4

    # Electrolyte Status Classification
    if electrolyte_score >= 90:
        status = "Optimal"
    elif 60 <= electrolyte_score < 90:
        status = "Moderate Deficiency"
    elif 40 <= electrolyte_score < 60:
        status = "Deficient"    
    else:
        status = "Severe Deficiency"

    return {
        "Sodium Intake (%)": round(sodium_pct, 2),
        "Potassium Intake (%)": round(potassium_pct, 2),
        "Magnesium Intake (%)": round(magnesium_pct, 2),
        "Calcium Intake (%)": round(calcium_pct, 2),
        "Electrolyte Score (%)": round(electrolyte_score, 2),
        "Electrolyte Status": status
    }

# Sleep Quality & Duration Score
def calculate_sleep_score(duration: float) -> float:

    sleep_score = round((duration / 8) * 100, 2)
    return sleep_score

# Daily Fiber Intake – Essential for Digestion & Gut Health
def daily_fiber_intake(age: int, gender: str, activity_level: str, goal: str) -> dict:

    gender = gender.lower()
    activity_level = activity_level.lower()
    goal = goal.lower()

    # Base fiber requirements based on age & gender
    if gender == "male":
        base_fiber = 38 if age <= 50 else 30
    elif gender == "female":
        base_fiber = 25 if age <= 50 else 21
    else:
        raise ValueError("Invalid gender. Choose 'male' or 'female'.")

    # Activity level adjustment
    activity_adjustment = {
        "sedentary": 0,
        "lightly active": 3,
        "moderately active": 5,
        "very active": 10
    }

    # Goal-based adjustment
    goal_adjustment = {
        "weight loss": 5,
        "muscle gain": -2,
        "maintenance": 0,
        "general wellbeing": 2
    }

    if activity_level not in activity_adjustment:
        raise ValueError("Invalid activity level. Choose 'sedentary', 'lightly active', 'moderately active', or 'very active'.")

    if goal not in goal_adjustment:
        raise ValueError("Invalid goal. Choose 'weight loss', 'muscle gain', 'maintenance', or 'general wellbeing'.")

    # Final fiber requirement
    recommended_fiber = base_fiber + activity_adjustment[activity_level] + goal_adjustment[goal]

    return {
        "Recommended Daily Fiber Intake (g)": recommended_fiber,
        "Category": f"{gender.capitalize()} ({'≤50' if age <= 50 else '>50'} years, {activity_level.capitalize()} activity, {goal.capitalize()} goal)"
    }
