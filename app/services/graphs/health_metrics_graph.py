from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.db_connect import connect_db
import app.health_metrics as health_metrics
from datetime import date


# LangGraph State
class HealthMetricsState(TypedDict):
    # Input
    email: str
    
    # User Data (fetched from DB)
    personal_details: Optional[dict]
    preferences: Optional[dict]
    health_conditions: Optional[dict]
    
    # Base Metrics (computed first)
    age: Optional[int]
    bmi: Optional[float]
    bmr: Optional[float]
    bfp: Optional[float]
    
    # Derived Metrics (depend on base)
    tdee: Optional[float]
    lbm: Optional[float]
    muscle_mass: Optional[float]
    visceral_fat: Optional[float]
    whr: Optional[float]
    metabolic_age: Optional[float]
    hydration_level: Optional[float]
    skeletal_mass: Optional[float]
    max_heart_rate: Optional[int]
    bmd: Optional[str]
    
    # Nutrition Metrics
    protein_intake: Optional[float]
    macro_nutrients: Optional[str]
    micro_nutrients: Optional[str]
    energy_surplus_deficit: Optional[float]
    electrolyte_balance: Optional[str]
    sleep_score: Optional[float]
    fiber: Optional[str]
    
    # Final formatted context
    metrics_context: Optional[str]
    error: Optional[str]


# Node: Fetch user data from database
async def fetch_user_data_node(state: HealthMetricsState) -> HealthMetricsState:
    """Fetch personal details, preferences, and health conditions from DB."""
    try:
        conn = await connect_db()
        
        personal = await conn.fetchrow(
            "SELECT * FROM personal_details WHERE email=$1", state["email"]
        )
        preferences = await conn.fetchrow(
            "SELECT * FROM preferences WHERE email=$1", state["email"]
        )
        health_cond = await conn.fetchrow(
            "SELECT * FROM health_conditions WHERE email=$1", state["email"]
        )
        
        await conn.close()
        
        if not personal or not preferences:
            state["error"] = "Missing user profile data"
            return state
        
        state["personal_details"] = dict(personal) if personal else None
        state["preferences"] = dict(preferences) if preferences else None
        state["health_conditions"] = dict(health_cond) if health_cond else None
        
    except Exception as e:
        state["error"] = f"Database error: {str(e)}"
    
    return state


# Node: Compute base metrics (independent calculations)
def compute_base_metrics_node(state: HealthMetricsState) -> HealthMetricsState:
    """Calculate age, BMI, BMR, BFP - these don't depend on other metrics."""
    if state.get("error"):
        return state
    
    pd = state["personal_details"]
    if not pd:
        state["error"] = "No personal details available"
        return state
    
    try:
        # Calculate age from date of birth
        dob = pd.get("dateofbirth")
        if isinstance(dob, str):
            dob = date.fromisoformat(dob)
        
        age = health_metrics.calculate_age(dob)
        height = float(pd.get("height", 0))
        weight = float(pd.get("weight", 0))
        gender = pd.get("gender", "").lower()
        
        state["age"] = age
        state["bmi"] = health_metrics.calculate_bmi(weight, height)
        state["bmr"] = health_metrics.calculate_bmr(weight, height, age, gender)
        state["bfp"] = health_metrics.calculate_bfp(state["bmi"], age, gender)
        
    except Exception as e:
        state["error"] = f"Error computing base metrics: {str(e)}"
    
    return state


# Node: Compute derived metrics (depend on base metrics)
def compute_derived_metrics_node(state: HealthMetricsState) -> HealthMetricsState:
    """Calculate TDEE, LBM, muscle mass, etc. - these depend on base metrics."""
    if state.get("error"):
        return state
    
    pd = state["personal_details"]
    pref = state["preferences"]
    
    if not pd or not pref:
        return state
    
    try:
        weight = float(pd.get("weight", 0))
        height = float(pd.get("height", 0))
        waist = float(pd.get("waist", 0))
        gender = pd.get("gender", "").lower()
        activity_level = pref.get("activitylevel", "Sedentary")
        
        # TDEE depends on BMR
        state["tdee"] = health_metrics.calculate_tdee(state["bmr"], activity_level)
        
        # LBM depends on BFP
        state["lbm"] = health_metrics.calculate_lbm(weight, state["bfp"])
        
        # Muscle mass depends on LBM
        state["muscle_mass"] = health_metrics.calculate_muscle_mass(state["lbm"])
        
        # Skeletal mass depends on LBM
        state["skeletal_mass"] = health_metrics.calculate_skeletal_muscle_mass(state["lbm"])
        
        # Other derived metrics
        state["visceral_fat"] = health_metrics.calculate_visceral_fat(state["bfp"], waist, height)
        state["whr"] = health_metrics.calculate_whtr(waist, height)
        state["metabolic_age"] = health_metrics.calculate_metabolic_age(state["lbm"], state["bmr"], state["age"])
        state["hydration_level"] = health_metrics.calculate_hydration_level(weight, height, gender, state["age"])
        state["max_heart_rate"] = health_metrics.calculate_max_heart_rate(state["age"])
        state["bmd"] = health_metrics.calculate_bmd(weight, height, state["age"], state["bfp"], gender)
        
    except Exception as e:
        state["error"] = f"Error computing derived metrics: {str(e)}"
    
    return state


# Node: Compute nutrition-related metrics
def compute_nutrition_metrics_node(state: HealthMetricsState) -> HealthMetricsState:
    """Calculate macros, protein intake, fiber, electrolytes, etc."""
    if state.get("error"):
        return state
    
    pd = state["personal_details"]
    pref = state["preferences"]
    
    if not pd or not pref:
        return state
    
    try:
        gender = pd.get("gender", "").lower()
        activity_level = pref.get("activitylevel", "Sedentary")
        fitness_goal = pref.get("fitnessgoal", "General Well-being")
        avg_sleep = float(pref.get("averagesleep", 7))
        
        # Protein intake
        state["protein_intake"] = health_metrics.calculate_protein_intake(
            activity_level, fitness_goal, state["lbm"]
        )
        
        # Macronutrients
        state["macro_nutrients"] = health_metrics.calculate_macronutrients(
            state["tdee"], fitness_goal, gender
        )
        
        # Micronutrients
        state["micro_nutrients"] = health_metrics.calculate_micronutrients(
            fitness_goal, state["age"], gender, activity_level
        )
        
        # Energy adjustment
        state["energy_surplus_deficit"] = health_metrics.calculate_energy_surplus_deficit(
            state["tdee"], fitness_goal
        )
        
        # Electrolyte balance
        state["electrolyte_balance"] = health_metrics.calculate_electrolyte_balance(
            state["age"], gender, activity_level, fitness_goal
        )
        
        # Sleep score
        state["sleep_score"] = health_metrics.calculate_sleep_score(avg_sleep)
        
        # Fiber
        state["fiber"] = health_metrics.daily_fiber_intake(
            state["age"], gender, activity_level, fitness_goal
        )
        
    except Exception as e:
        state["error"] = f"Error computing nutrition metrics: {str(e)}"
    
    return state


# Node: Format metrics as readable context for LLM
def finalize_metrics_node(state: HealthMetricsState) -> HealthMetricsState:
    """Assemble all metrics into a formatted string for LLM context."""
    if state.get("error"):
        state["metrics_context"] = f"Unable to compute health metrics: {state['error']}"
        return state
    
    try:
        context_parts = [
            "HEALTH METRICS (Computed):",
            f"- Age: {state['age']} years",
            f"- BMI: {state['bmi']:.1f}",
            f"- BMR: {state['bmr']:.0f} kcal/day",
            f"- TDEE: {state['tdee']:.0f} kcal/day",
            f"- Body Fat %: {state['bfp']:.1f}%",
            f"- Lean Body Mass: {state['lbm']:.1f} kg",
            f"- Muscle Mass: {state['muscle_mass']:.1f} kg",
            f"- Skeletal Muscle Mass: {state['skeletal_mass']:.1f} kg",
            f"- Visceral Fat Score: {state['visceral_fat']:.1f}",
            f"- Waist-to-Height Ratio: {state['whr']:.2f}",
            f"- Metabolic Age: {state['metabolic_age']:.0f} years",
            f"- Hydration Level: {state['hydration_level']:.1f}%",
            f"- Max Heart Rate: {state['max_heart_rate']} bpm",
            f"- Protein Intake: {state['protein_intake']:.0f}g/day",
            f"- Sleep Score: {state['sleep_score']:.0f}%",
            f"- Energy Target: {state['energy_surplus_deficit']:.0f} kcal/day",
            "",
            state['macro_nutrients'],
            "",
            f"Bone Health: {state['bmd']}",
            "",
            state['fiber'],
        ]
        
        state["metrics_context"] = "\n".join(context_parts)
        
    except Exception as e:
        state["metrics_context"] = f"Error formatting metrics: {str(e)}"
    
    return state


# Build the Health Metrics Graph
def build_health_metrics_graph():
    """Build and compile the health metrics computation graph."""
    graph = StateGraph(HealthMetricsState)
    
    # Add nodes
    graph.add_node("fetch_user_data", fetch_user_data_node)
    graph.add_node("compute_base_metrics", compute_base_metrics_node)
    graph.add_node("compute_derived_metrics", compute_derived_metrics_node)
    graph.add_node("compute_nutrition_metrics", compute_nutrition_metrics_node)
    graph.add_node("finalize_metrics", finalize_metrics_node)
    
    # Define flow
    graph.set_entry_point("fetch_user_data")
    graph.add_edge("fetch_user_data", "compute_base_metrics")
    graph.add_edge("compute_base_metrics", "compute_derived_metrics")
    graph.add_edge("compute_derived_metrics", "compute_nutrition_metrics")
    graph.add_edge("compute_nutrition_metrics", "finalize_metrics")
    graph.add_edge("finalize_metrics", END)
    
    return graph.compile()


# Compiled graph instance
health_metrics_graph = build_health_metrics_graph()


async def compute_health_metrics(email: str) -> dict:
    """Execute health metrics computation pipeline and return result."""
    result = await health_metrics_graph.ainvoke({
        "email": email,
        "personal_details": None,
        "preferences": None,
        "health_conditions": None,
        "age": None,
        "bmi": None,
        "bmr": None,
        "bfp": None,
        "tdee": None,
        "lbm": None,
        "muscle_mass": None,
        "visceral_fat": None,
        "whr": None,
        "metabolic_age": None,
        "hydration_level": None,
        "skeletal_mass": None,
        "max_heart_rate": None,
        "bmd": None,
        "protein_intake": None,
        "macro_nutrients": None,
        "micro_nutrients": None,
        "energy_surplus_deficit": None,
        "electrolyte_balance": None,
        "sleep_score": None,
        "fiber": None,
        "metrics_context": None,
        "error": None,
    })
    return result
