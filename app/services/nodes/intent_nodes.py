from app.services.nvidia_api_service import call_nvidia_api

def classify_intent_node(state: dict):
    """Classify the user's intent to route to appropriate handler."""
    user_message = state.get("user_message", "")
    
    if not user_message:
        return {"intent": "general"}
    
    classify_prompt = f"""Classify the following user message into ONE of these categories:
- meal_plan: User wants a meal plan, diet schedule, or food recommendations for a day/week
- nutrition_query: User is asking about calories, nutrients, or specific food information
- health_advice: User is asking for health-related advice based on their conditions
- general: General conversation, greetings, or other topics

User message: "{user_message}"

Respond with ONLY the category name (meal_plan, nutrition_query, health_advice, or general). Nothing else."""

    try:
        messages = [{"role": "user", "content": classify_prompt}]
        result = call_nvidia_api(messages).strip().lower()
        
        valid_intents = ["meal_plan", "nutrition_query", "health_advice", "general"]
        if result in valid_intents:
            return {"intent": result}
        else:
            return {"intent": "general"}
    except Exception:
        return {"intent": "general"}


def route_by_intent(state: dict) -> str:
    """Route to appropriate handler based on classified intent."""
    intent = state.get("intent", "general")
    
    intent_to_handler = {
        "meal_plan": "handle_meal_plan",
        "nutrition_query": "handle_nutrition_query",
        "health_advice": "handle_health_advice",
        "general": "handle_general",
    }
    
    return intent_to_handler.get(intent, "handle_general")
