from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# Pydantic models 
class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class PersonalDetails(BaseModel):
    name: str
    dateofbirth: date
    gender: str
    height: float
    weight: float
    waist: float 

class Preferences(BaseModel):
    foodpreference: str 
    snackpreferences: str 
    mealtimings: str 
    cheatdayfrequency: str
    culturalpreferences: str 
    preferredingredients: str 
    cuisinepreferences: str
    spicyfoodtolerance: str
    preferredmealtype: str
    favoritemeal: str
    mealfrequency: str
    sweetpreference: str
    eatingoutfrequency: str
    hydrationlevel: float
    preferreddrinks: str
    activitylevel: str
    fitnessgoal: str
    foodrestrictions: str
    caffeineintake: str
    averagesleep: float
    sleepquality: str
    supplementusage: str
    supplementfrequency: str     

class HealthConditions(BaseModel):
    allergies: str
    diabetes: str
    hypertension: str 
    cholesterol: str
    thyroid: str
    kidneydisease: str
    liverdisease: str
    lactoseintolerance: str
    glutensensitivity: str
    pcos: Optional[str] = None
    anemia: str
    osteoporosis: str
    ibs: str
    gerd: str
    gout: str
    otherconditions: str 

class HealthMetrics(BaseModel):
    age: int
    bmi: float
    bmr: float
    tdee: float
    bfp: float
    lbm: float
    muscle_mass: float
    visceral_fat: float
    whr: float
    metabolic_age: float
    hydration_level: float
    protein_intake: float  
    macro_nutrients: str  
    micro_nutrients: str 
    energy_surplus_deficit: float
    bmd: str 
    max_heart_rate: int
    electrolyte_balance: str  
    skeletal_mass: float
    sleep_score: float
    fiber: str 

class ChatRequest(BaseModel):
    message: str 