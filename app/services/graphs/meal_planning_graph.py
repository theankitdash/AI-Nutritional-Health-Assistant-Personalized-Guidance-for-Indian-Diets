from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from app.services.nvidia_api_service import call_nvidia_api
from app.services.graphs.health_metrics_graph import compute_health_metrics
from app.db_connect import connect_db


class MealPlanState(TypedDict):
    # Input
    email: str
    user_request: str
    
    # User profile context
    user_profile: Optional[str]
    health_metrics: Optional[str]
    dietary_restrictions: Optional[List[str]]
    
    # Meal planning context
    plan_duration: str  # "day", "week"
    calorie_target: Optional[float]
    meal_count: int
    
    # Food database context
    food_context: Optional[str]
    
    # Generated content
    meal_plan_raw: Optional[str]
    validation_result: Optional[str]
    final_meal_plan: Optional[str]
    
    # Error handling
    error: Optional[str]


# ============ NODES ============
async def analyze_requirements_node(state: MealPlanState) -> MealPlanState:
    """Parse user request and extract meal planning requirements."""
    request = state["user_request"].lower()
    
    # Determine plan duration
    if "week" in request or "7 day" in request:
        state["plan_duration"] = "week"
    else:
        state["plan_duration"] = "day"
    
    # Default meal count
    state["meal_count"] = 4  # Breakfast, Lunch, Dinner, Snacks
    
    # Fetch user profile
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
        
        # Build profile context
        profile_parts = []
        restrictions = []
        
        if personal:
            profile_parts.append(f"Name: {personal.get('name', 'N/A')}")
            profile_parts.append(f"Gender: {personal.get('gender', 'N/A')}")
            profile_parts.append(f"Weight: {personal.get('weight', 'N/A')} kg")
            profile_parts.append(f"Height: {personal.get('height', 'N/A')} cm")
        
        if preferences:
            profile_parts.append(f"Food Preference: {preferences.get('foodpreference', 'N/A')}")
            profile_parts.append(f"Cuisine: {preferences.get('cuisinepreferences', 'N/A')}")
            profile_parts.append(f"Fitness Goal: {preferences.get('fitnessgoal', 'N/A')}")
            profile_parts.append(f"Activity Level: {preferences.get('activitylevel', 'N/A')}")
            
            food_pref = preferences.get('foodpreference', '').lower()
            if 'vegetarian' in food_pref or 'vegan' in food_pref:
                restrictions.append(food_pref)
            
            food_restrict = preferences.get('foodrestrictions', '')
            if food_restrict and food_restrict.lower() != 'none':
                restrictions.append(food_restrict)
        
        if health_cond:
            health_dict = dict(health_cond)
            health_dict.pop('email', None)
            for key, value in health_dict.items():
                if value and value.lower() not in ['none', 'no', '']:
                    restrictions.append(f"{key}: {value}")
        
        state["user_profile"] = "\n".join(profile_parts)
        state["dietary_restrictions"] = restrictions
        
    except Exception as e:
        state["error"] = f"Error fetching profile: {str(e)}"
    
    return state


async def fetch_health_metrics_node(state: MealPlanState) -> MealPlanState:
    """Compute health metrics for calorie targeting."""
    if state.get("error"):
        return state
    
    try:
        metrics_result = await compute_health_metrics(state["email"])
        state["health_metrics"] = metrics_result.get("metrics_context", "")
        
        # Extract TDEE for calorie target
        tdee = metrics_result.get("tdee")
        if tdee:
            # Adjust based on goal
            # For now, use TDEE as base target
            state["calorie_target"] = float(tdee)
        else:
            state["calorie_target"] = 2000.0  # Default fallback
            
    except Exception as e:
        state["calorie_target"] = 2000.0
        state["health_metrics"] = "Metrics unavailable"
    
    return state


def fetch_food_context_node(state: MealPlanState) -> MealPlanState:
    """Retrieve relevant Indian food options using hybrid search."""
    if state.get("error"):
        return state
    
    try:
        from app.services.hybrid_retriever import hybrid_search
        
        # Search for foods based on preferences using hybrid retrieval
        query = f"Indian {state.get('user_request', 'meal')} healthy"
        docs = hybrid_search(query, k_final=10)
        state["food_context"] = "\n".join(d.page_content for d in docs)
        
    except Exception as e:
        state["food_context"] = ""
        
    return state


def generate_meals_node(state: MealPlanState) -> MealPlanState:
    """Generate personalized meal plan using LLM."""
    if state.get("error"):
        return state
    
    restrictions_str = ", ".join(state.get("dietary_restrictions", [])) or "None"
    
    prompt = f"""You are an expert Indian nutrition dietitian. Create a detailed meal plan.

USER PROFILE:
{state.get("user_profile", "Not available")}

HEALTH METRICS:
{state.get("health_metrics", "Not available")}

DIETARY RESTRICTIONS:
{restrictions_str}

DAILY CALORIE TARGET: {state.get("calorie_target", 2000):.0f} kcal

AVAILABLE INDIAN FOODS:
{state.get("food_context", "")}

USER REQUEST:
{state["user_request"]}

PLAN DURATION: {state["plan_duration"]}

Create a {"weekly" if state["plan_duration"] == "week" else "daily"} meal plan with:
1. **Breakfast** - Light, energizing start
2. **Mid-Morning Snack** - Optional healthy snack
3. **Lunch** - Main meal with balance of macros
4. **Evening Snack** - Light option
5. **Dinner** - Lighter than lunch, easy to digest

For each meal include:
- Dish name (Indian)
- Brief description
- Approximate calories
- Key nutrients

Ensure the total daily calories align with the target.
Use authentic Indian dishes that are practical to prepare."""

    messages = [{"role": "user", "content": prompt}]
    result = call_nvidia_api(messages)
    state["meal_plan_raw"] = result.strip()
    
    return state


def validate_nutrition_node(state: MealPlanState) -> MealPlanState:
    """Validate the meal plan against user's health requirements."""
    if state.get("error"):
        return state
    
    restrictions_str = ", ".join(state.get("dietary_restrictions", [])) or "None"
    
    validate_prompt = f"""Review this meal plan for nutritional completeness and safety.

MEAL PLAN:
{state["meal_plan_raw"]}

USER RESTRICTIONS:
{restrictions_str}

CALORIE TARGET: {state.get("calorie_target", 2000):.0f} kcal

Check for:
1. Does it respect dietary restrictions (vegetarian, allergies, conditions)?
2. Are calories approximately correct?
3. Is there protein, fiber, and essential nutrients?
4. Any potential conflicts with health conditions?

If there are issues, list them. If the plan is good, say "VALIDATED" and briefly explain why it's suitable."""

    messages = [{"role": "user", "content": validate_prompt}]
    result = call_nvidia_api(messages)
    state["validation_result"] = result.strip()
    
    return state


def format_meal_plan_node(state: MealPlanState) -> MealPlanState:
    """Format the final meal plan response."""
    if state.get("error"):
        state["final_meal_plan"] = f"Unable to create meal plan: {state['error']}"
        return state
    
    # Combine meal plan with validation notes
    final_parts = [
        "🍽️ **Your Personalized Indian Meal Plan**\n",
        state.get("meal_plan_raw", ""),
        "\n---\n",
        f"📊 **Calorie Target**: ~{state.get('calorie_target', 2000):.0f} kcal/day",
        "\n",
        "✅ **Nutrition Check**:",
        state.get("validation_result", "Not validated"),
    ]
    
    state["final_meal_plan"] = "\n".join(final_parts)
    
    return state


# ============ BUILD GRAPH ============

def build_meal_planning_graph():
    """Build the meal planning agent graph."""
    graph = StateGraph(MealPlanState)
    
    # Add nodes
    graph.add_node("analyze_requirements", analyze_requirements_node)
    graph.add_node("fetch_health_metrics", fetch_health_metrics_node)
    graph.add_node("fetch_food_context", fetch_food_context_node)
    graph.add_node("generate_meals", generate_meals_node)
    graph.add_node("validate_nutrition", validate_nutrition_node)
    graph.add_node("format_meal_plan", format_meal_plan_node)
    
    # Define flow
    graph.set_entry_point("analyze_requirements")
    graph.add_edge("analyze_requirements", "fetch_health_metrics")
    graph.add_edge("fetch_health_metrics", "fetch_food_context")
    graph.add_edge("fetch_food_context", "generate_meals")
    graph.add_edge("generate_meals", "validate_nutrition")
    graph.add_edge("validate_nutrition", "format_meal_plan")
    graph.add_edge("format_meal_plan", END)
    
    return graph.compile()


# Compiled graph
meal_planning_graph = build_meal_planning_graph()


async def generate_meal_plan(email: str, user_request: str) -> dict:
    """Execute the meal planning pipeline."""
    result = await meal_planning_graph.ainvoke({
        "email": email,
        "user_request": user_request,
        "user_profile": None,
        "health_metrics": None,
        "dietary_restrictions": None,
        "plan_duration": "day",
        "calorie_target": None,
        "meal_count": 4,
        "food_context": None,
        "meal_plan_raw": None,
        "validation_result": None,
        "final_meal_plan": None,
        "error": None,
    })
    return result
