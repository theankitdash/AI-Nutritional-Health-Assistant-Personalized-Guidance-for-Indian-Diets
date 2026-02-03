from app.services.nvidia_api_service import call_nvidia_api

async def handle_meal_plan_node(state: dict):
    """Handle meal planning requests using the dedicated meal planning graph."""
    from app.services.graphs.meal_planning_graph import generate_meal_plan
    
    try:
        result = await generate_meal_plan(
            email=state.get("user_email", ""),
            user_request=state.get("user_message", "")
        )
        meal_plan = result.get("final_meal_plan", "")
        
        if meal_plan:
            return {"response": meal_plan, "meal_plan": meal_plan}
        else:
            return {
                "response": "I apologize, but I couldn't generate a meal plan at this time. Please try again.",
                "meal_plan": ""
            }
    except Exception as e:
        return {
            "response": f"I encountered an issue creating your meal plan. Please try again. Error: {str(e)}",
            "meal_plan": ""
        }


def handle_nutrition_query_node(state: dict):
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
        result = call_nvidia_api(messages)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing nutrition query: {str(e)}"}


def handle_health_advice_node(state: dict):
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
        result = call_nvidia_api(messages)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing health advice: {str(e)}"}


def handle_general_node(state: dict):
    """Handle general conversation and other queries."""
    prompt = f"""You are a friendly Indian nutrition assistant.

*User Profile*:
{state.get("user_context", "Not available")}

*Health Metrics*:
{state.get("health_metrics_context", "Not available")}

*Indian Food Database*:
{state.get("retrieved_context", "Not available")}

*Conversation Summary*:
{state.get("summary", "")}

*User Message*:
{state.get("user_message", "")}

Keep your response friendly and concise (under 100 words). Only elaborate if the user asks for details."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = call_nvidia_api(messages)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}


def summary_node(state: dict):
    """Update conversation summary."""
    summary_prompt = f"""You are updating a running conversation summary.

Existing summary:
{state.get('summary', '')}

New interaction:
User: {state.get('user_message', '')}
Assistant: {state.get('response', '')}

Update the summary using ONLY explicit information.
- Preserve user goals, constraints, preferences, and unresolved questions
- Remove redundancy
- Do NOT infer or assume anything
- Keep it under 120 words"""

    try:
        messages = [{"role": "user", "content": summary_prompt}]
        result = call_nvidia_api(messages)
        return {"summary": result.strip()}
    except Exception:
        return {"summary": state.get('summary', '')}
