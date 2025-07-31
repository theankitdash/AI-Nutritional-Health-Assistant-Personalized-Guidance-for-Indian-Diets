from db_connect import connect_db
import health_metrics
from models import (PersonalDetails, Preferences, HealthConditions, HealthMetrics)
from fastapi import HTTPException
import traceback

async def calculate_and_store_health_metrics(email: str):
    try:
        conn = await connect_db()

        # Fetch data from personal_details, preferences, and health_conditions tables
        personal_details = await conn.fetchrow("SELECT * FROM personal_details WHERE email = $1", email)
        preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email = $1", email)
        health_conditions = await conn.fetchrow("SELECT * FROM health_conditions WHERE email = $1", email)

        if not personal_details or not preferences or not health_conditions:
            await conn.close()
            raise HTTPException(status_code=404, detail="User profile is incomplete. Please update all the details.")

        # Decode data into appropriate classes
        personal_details_data = PersonalDetails(**personal_details)
        preferences_data = Preferences(**preferences)
        health_data = HealthConditions(**health_conditions)

        # Calculate Health Metrics
        age = health_metrics.calculate_age(personal_details_data.dateofbirth)
        bmi = health_metrics.calculate_bmi(personal_details_data.weight, personal_details_data.height)
        bmr = health_metrics.calculate_bmr(personal_details_data.weight, personal_details_data.height, age, personal_details_data.gender)
        tdee = health_metrics.calculate_tdee(bmr, preferences_data.activitylevel)
        bfp = health_metrics.calculate_bfp(bmi, age, personal_details_data.gender)
        lbm = health_metrics.calculate_lbm(personal_details_data.weight, bfp)
        muscle_mass = health_metrics.calculate_muscle_mass(lbm)
        visceral_fat = health_metrics.calculate_visceral_fat(bfp, personal_details_data.waist, personal_details_data.height)
        whr = health_metrics.calculate_whtr(personal_details_data.waist, personal_details_data.height)
        metabolic_age = health_metrics.calculate_metabolic_age(lbm, bmr, age)
        hydration_level = health_metrics.calculate_hydration_level(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age)
        protein_intake = health_metrics.calculate_protein_intake(preferences_data.activitylevel, preferences_data.fitnessgoal, lbm)
        macro_nutrients = health_metrics.calculate_macronutrients(tdee, preferences_data.fitnessgoal, personal_details_data.gender)
        micro_nutrients = health_metrics.calculate_micronutrients(preferences_data.fitnessgoal, age, personal_details_data.gender, preferences_data.activitylevel)
        energy_surplus_deficit = health_metrics.calculate_energy_surplus_deficit(tdee, preferences_data.fitnessgoal)
        #glycemic_index=health_metrics.glycemic_index_load(preferences_data.foodPreference),  # To be updated later
        bmd = health_metrics.calculate_bmd(personal_details_data.weight, personal_details_data.height, age, bfp, personal_details_data.gender)
        max_heart_rate = health_metrics.calculate_max_heart_rate(age)
        electrolyte_balance = health_metrics.calculate_electrolyte_balance(age, personal_details_data.gender, preferences_data.activitylevel, preferences_data.fitnessgoal)
        #body_water_percentage=health_metrics.calculate_body_water_percentage(personal_details_data.weight, personal_details_data.height, personal_details_data.gender, age, bfp, preferences_data.activityLevel)
        skeletal_mass = health_metrics.calculate_skeletal_muscle_mass(lbm)
        #protein_absorption=health_metrics.calculate_protein_absorption(health_metrics.calculate_protein_intake, preferences_data.foodPreference),  # To be updated later
        #metabolic_flexibility=health_metrics.calculate_metabolic_flexibility(preferences_data.activityLevel, preferences_data.foodPreference),  # To be updated later
    
        sleep_score = health_metrics.calculate_sleep_score(preferences_data.averagesleep)
        fiber = health_metrics.daily_fiber_intake(age, personal_details_data.gender, preferences_data.activitylevel, preferences_data.fitnessgoal)

        health_metrics_data = HealthMetrics(
            age=age, bmi=bmi, bmr=bmr, tdee=tdee, bfp=bfp, lbm=lbm, muscle_mass=muscle_mass, visceral_fat=visceral_fat,
            whr=whr, metabolic_age=metabolic_age, hydration_level=hydration_level, protein_intake=protein_intake, 
            macro_nutrients=macro_nutrients, micro_nutrients=micro_nutrients, energy_surplus_deficit=energy_surplus_deficit,
            bmd=bmd, max_heart_rate=max_heart_rate, electrolyte_balance=electrolyte_balance, skeletal_mass=skeletal_mass, 
            sleep_score=sleep_score, fiber=fiber
        )

        # Insert or update health metrics in PostgreSQL
        await conn.execute("""
            INSERT INTO health_metrics (
                email, age, bmi, bmr, tdee, bfp, lbm, muscle_mass, visceral_fat, whr, metabolic_age, hydration_level,
                protein_intake, macro_nutrients, micro_nutrients, energy_surplus_deficit, bmd, max_heart_rate, electrolyte_balance,
                skeletal_mass, sleep_score, fiber
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22
            )
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age, bmi = EXCLUDED.bmi, bmr = EXCLUDED.bmr, tdee = EXCLUDED.tdee, bfp = EXCLUDED.bfp,
                lbm = EXCLUDED.lbm, muscle_mass = EXCLUDED.muscle_mass, visceral_fat = EXCLUDED.visceral_fat, whr = EXCLUDED.whr,
                metabolic_age = EXCLUDED.metabolic_age, hydration_level = EXCLUDED.hydration_level, protein_intake = EXCLUDED.protein_intake,
                macro_nutrients = EXCLUDED.macro_nutrients, micro_nutrients = EXCLUDED.micro_nutrients, energy_surplus_deficit = EXCLUDED.energy_surplus_deficit,
                bmd = EXCLUDED.bmd, max_heart_rate = EXCLUDED.max_heart_rate, electrolyte_balance = EXCLUDED.electrolyte_balance,
                skeletal_mass = EXCLUDED.skeletal_mass, sleep_score = EXCLUDED.sleep_score, fiber = EXCLUDED.fiber
        """, email, *health_metrics_data.model_dump().values())

        await conn.close()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error calculating or storing health metrics.") 
