from app.services.nvidia_api_service import call_nvidia_api

async def handle_meal_plan_node(state: dict):
    """Handle meal planning with a single LLM call (generate + validate).
    
    Uses user_context and health_metrics_context already in state
    (fetched once by fetch_context_node) instead of re-querying the DB.
    """
    from app.services.tools import search_food_database

    user_message = state.get("user_message", "")

    # Determine plan duration from the message
    lower_msg = user_message.lower()
    duration = "weekly" if ("week" in lower_msg or "7 day" in lower_msg) else "daily"

    # Get food context via hybrid search (no LLM call)
    food_context = search_food_database(user_message, k=10)

    prompt = f"""You are an expert Indian nutrition dietitian. Create a personalized meal plan
AND validate it against the user's dietary restrictions and health conditions.

USER PROFILE:
{state.get("user_context", "Not available")}

HEALTH METRICS:
{state.get("health_metrics_context", "Not available")}

AVAILABLE INDIAN FOODS (from database):
{food_context}

USER REQUEST:
{user_message}

Create a {duration} meal plan with:
1. **Breakfast** — Light, energizing start
2. **Mid-Morning Snack** — Optional healthy snack
3. **Lunch** — Main meal with balanced macros
4. **Evening Snack** — Light option
5. **Dinner** — Lighter than lunch, easy to digest

For each meal include: dish name (Indian), brief description, approximate calories, key nutrients.

At the end, add a brief "✅ Nutrition Check" section confirming the plan respects
dietary restrictions, aligns with the calorie target from health metrics, and flags
any potential concerns. Use authentic, practical Indian dishes."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = await call_nvidia_api(messages, max_tokens=4096)
        meal_plan = result.strip()

        formatted = f"🍽️ **Your Personalized Indian Meal Plan**\n\n{meal_plan}"
        return {"response": formatted, "meal_plan": formatted}
    except Exception as e:
        return {
            "response": f"I encountered an issue creating your meal plan. Please try again. Error: {str(e)}",
            "meal_plan": "",
        }


async def handle_nutrition_query_node(state: dict):
    """Handle nutrition-related queries about food and nutrients."""
    prompt = f"""You are a nutrition expert specializing in Indian foods.

*User Profile*:
{state.get("user_context", "Not available")}

*Health Metrics*:
{state.get("health_metrics_context", "Not available")}

*Indian Food Database*:
{state.get("retrieved_context", "Not available")}

*User Question*:
{state.get("user_message", "")}

Provide accurate nutrition information. Be specific about key nutrients.
Keep your response concise and under 100 words unless the user asks for details."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = await call_nvidia_api(messages, max_tokens=512)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing nutrition query: {str(e)}"}


async def handle_health_advice_node(state: dict):
    """Handle health-related advice requests."""
    prompt = f"""You are a health-aware nutrition advisor for Indian diets.

*User Profile*:
{state.get("user_context", "Not available")}

*Health Metrics*:
{state.get("health_metrics_context", "Not available")}

*User's Health Conditions*:
Check their profile for conditions like diabetes, hypertension, cholesterol, etc.

*Indian Food Database*:
{state.get("retrieved_context", "Not available")}

*User Question*:
{state.get("user_message", "")}

Give brief, practical health advice. Keep your response concise and under 100 words unless the user asks for details.
Note: This is general nutrition guidance, not medical advice."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = await call_nvidia_api(messages, max_tokens=512)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing health advice: {str(e)}"}


async def handle_general_node(state: dict):
    """Handle general conversation and other queries."""
    prompt = f"""You are a friendly Indian nutrition assistant.

*User Profile*:
{state.get("user_context", "Not available")}

*Conversation Summary*:
{state.get("summary", "")}

*User Message*:
{state.get("user_message", "")}

Keep your response friendly and concise (under 100 words). Only elaborate if the user asks for details."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = await call_nvidia_api(messages, max_tokens=256)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}


async def update_summary(
    user_message: str,
    response: str,
    existing_summary: str,
) -> str:
    """Update conversation summary — runs as a background task, NOT in the graph.
    
    This was the old summary_node. Moving it out of the critical path saves
    2-5 seconds per message since the user doesn't wait for it.
    """
    summary_prompt = f"""You are updating a running conversation summary.

Existing summary:
{existing_summary}

New interaction:
User: {user_message}
Assistant: {response}

Update the summary using ONLY explicit information.
- Preserve user goals, constraints, preferences, and unresolved questions
- Remove redundancy
- Do NOT infer or assume anything
- Keep it under 120 words"""

    try:
        messages = [{"role": "user", "content": summary_prompt}]
        result = await call_nvidia_api(messages, max_tokens=256)
        return result.strip()
    except Exception:
        return existing_summary
