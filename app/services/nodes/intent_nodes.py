_MEAL_PLAN_KEYWORDS = {
    "meal plan", "diet plan", "weekly plan", "daily plan", "7 day", "7-day",
    "week meal", "week diet", "meal schedule", "diet schedule", "eating plan",
    "food plan", "what to eat today", "what should i eat", "plan my meals",
    "create a plan", "suggest a diet",
}

_NUTRITION_KEYWORDS = {
    "calorie", "calories", "protein", "carbs", "carbohydrate", "fat content",
    "nutrients", "nutrition", "macro", "fiber content", "vitamin", "mineral",
    "per 100g", "per gram", "how many calories", "nutritional", "kcal",
    "kilocalorie", "glycemic", "omega", "calcium", "iron", "sodium",
}

_HEALTH_KEYWORDS = {
    "diabetes", "diabetic", "hypertension", "blood pressure", "cholesterol",
    "heart disease", "thyroid", "kidney", "liver", "weight loss", "weight gain",
    "obesity", "allergic", "allergy", "intolerant", "gluten", "pcod", "pcos",
    "should i eat", "is it good for", "good for my health", "safe to eat",
    "health condition", "medical", "gut", "digestion", "inflammation",
}


def _classify_intent_locally(message: str) -> str:
    """
    Rule-based intent classifier — no API call, executes in <1 ms.

    Priority order: meal_plan > nutrition_query > health_advice > general
    (meal_plan is checked first because it is the most specific intent)
    """
    lower = message.lower()

    if any(kw in lower for kw in _MEAL_PLAN_KEYWORDS):
        return "meal_plan"

    if any(kw in lower for kw in _NUTRITION_KEYWORDS):
        return "nutrition_query"

    if any(kw in lower for kw in _HEALTH_KEYWORDS):
        return "health_advice"

    return "general"


async def classify_intent_node(state: dict):
    """
    Classify the user's intent using fast local keyword rules.

    No LLM call is made — saves 2–8 s per request with no meaningful accuracy
    loss for these 4 clearly-bounded intent categories.
    """
    user_message = state.get("user_message", "")

    if not user_message:
        return {"intent": "general"}

    intent = _classify_intent_locally(user_message)
    return {"intent": intent}


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
