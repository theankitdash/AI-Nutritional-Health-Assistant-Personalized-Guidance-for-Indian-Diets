import datetime

# Age
def calculate_age(dob: str) -> int:
    birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# BMR
def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# BMI
def calculate_bmi(weight: float, height: float) -> float:
    bmi = weight / ((height / 100) ** 2)
    return round(bmi, 2)

# BFP
def calculate_bfp_from_bmi(bmi: float, age: int, gender: str) -> float:
    if gender.lower() == 'male':
        bfp = 1.20 * bmi + 0.23 * age - 16.2
    else:
        bfp = 1.20 * bmi + 0.23 * age - 5.4
    return round(bfp, 2)

# Visceral Fat
def calculate_visceral_fat(weight: float, waist: float) -> float:
    visceral_fat = (waist / weight) * 100
    return round(visceral_fat, 2)

# WHR
def calculate_whr(waist: float, height: float) -> float:
    whtr = waist / height
    return round(whtr, 2)

# Cholesterol Ratio
def lipid_profile(total_cholesterol: float, hdl: float, ldl: float, triglycerides: float) -> dict:
    cholesterol_ratio = total_cholesterol / hdl
    tg_hdl_ratio = triglycerides / hdl
    return {
        'total_cholesterol': total_cholesterol,
        'hdl': hdl,
        'ldl': ldl,
        'triglycerides': triglycerides,
        'cholesterol_ratio': round(cholesterol_ratio, 2),
        'tg_hdl_ratio': round(tg_hdl_ratio, 2)
    }

# Lean Body Mass
def calculate_lbm(weight: float, height: float, gender: str) -> float:
    if gender.lower() == 'male':
        lbm = 0.407 * weight + 0.267 * height - 19.2
    else:
        lbm = 0.252 * weight + 0.473 * height - 48.3
    return round(lbm, 2)

# Metabolic Age
def calculate_metabolic_age(bmr: float, age: int) -> int:
    return max(10, min(80, round(age + (bmr - (age * 24)) / 5)))

# Blood Sugar Level with HbA1c
def check_blood_sugar_level(fasting_glucose: float, post_meal_glucose: float, hba1c: float) -> dict:
    return {
        'fasting': 'normal' if 70 <= fasting_glucose <= 99 else 'high' if fasting_glucose > 99 else 'low',
        'post_meal': 'normal' if post_meal_glucose < 140 else 'high',
        'hba1c_status': 'normal' if hba1c < 5.7 else 'prediabetic' if 5.7 <= hba1c < 6.5 else 'diabetic'
    }

# Vitamin and Mineral Levels
def vitamin_mineral_levels(vitamin_d: float, calcium: float) -> dict:
    return {
        'vitamin_d_status': 'normal' if 30 <= vitamin_d <= 100 else 'deficient',
        'calcium_status': 'normal' if 8.5 <= calcium <= 10.5 else 'low'
    }

# Hydration Level
def hydration_level(weight: float, activity_level: str) -> float:
    factor = 35 if activity_level.lower() == 'high' else 30
    return round(weight * factor, 2)

# BMD Status
def bmd_status(age: int, gender: str) -> str:
    if (gender == 'female' and age > 65) or (gender == 'male' and age > 70):
        return "Osteoporosis risk: High"
    return "Normal BMD"

# Electrolyte Balance
def electrolyte_balance(sodium: float, potassium: float) -> dict:
    return {
        'sodium_status': 'normal' if 135 <= sodium <= 145 else 'abnormal',
        'potassium_status': 'normal' if 3.5 <= potassium <= 5.0 else 'abnormal'
    }

# Muscle Mass (Estimated)
def calculate_muscle_mass(weight: float, lbm: float) -> float:
    return round(lbm * 1.1, 2)

# Protein Requirement
def calculate_protein_intake(weight: float, activity_level: str) -> float:
    factor = 1.2 if activity_level.lower() == 'low' else 1.6 if activity_level.lower() == 'moderate' else 2.0
    return round(weight * factor, 2)

# Heart Rate
def calculate_max_heart_rate(age: int) -> int:
    return 220 - age

# VO₂ Max (Estimated)
def calculate_vo2_max(age: int, resting_hr: int) -> float:
    return round(15.3 * (220 - age) / resting_hr, 2)