from app.db_connect import connect_db
from app.services.cache import user_profile_cache
from app.services.nvidia_api_service import call_nvidia_api
from app.services.tools import search_food_database


async def retrieve_user_node(state: dict):
    """Fetch user profile from cache or database."""
    email = state.get("user_email", "")
    session_id = state.get("session_id", "")
    
    if not email:
        return {"user_context": "No user email provided"}
    
    if session_id in user_profile_cache and user_profile_cache[session_id] is not None:
        return {"user_context": user_profile_cache[session_id]}
    
    try:
        conn = await connect_db()
        try:
            personal = await conn.fetchrow("SELECT * FROM personal_details WHERE email=$1", email)
            preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email=$1", email)
            health = await conn.fetchrow("SELECT * FROM health_conditions WHERE email=$1", email)
            
            user_context_parts = []
            
            if personal:
                user_context_parts.append("PERSONAL DETAILS:")
                user_context_parts.append(f"- Name: {personal.get('name', 'N/A')}")
                user_context_parts.append(f"- Age: {personal.get('dateofbirth', 'N/A')}")
                user_context_parts.append(f"- Gender: {personal.get('gender', 'N/A')}")
                user_context_parts.append(f"- Height: {personal.get('height', 'N/A')} cm")
                user_context_parts.append(f"- Weight: {personal.get('weight', 'N/A')} kg")
                user_context_parts.append(f"- Waist: {personal.get('waist', 'N/A')} cm")
            else:
                user_context_parts.append("PERSONAL DETAILS: Not provided")
            
            user_context_parts.append("")
            
            if preferences:
                user_context_parts.append("DIETARY PREFERENCES:")
                user_context_parts.append(f"- Food Preference: {preferences.get('foodpreference', 'N/A')}")
                user_context_parts.append(f"- Cuisine Preferences: {preferences.get('cuisinepreferences', 'N/A')}")
                user_context_parts.append(f"- Meal Frequency: {preferences.get('mealfrequency', 'N/A')}")
                user_context_parts.append(f"- Favorite Meal: {preferences.get('favoritemeal', 'N/A')}")
                user_context_parts.append(f"- Snack Preferences: {preferences.get('snackpreferences', 'N/A')}")
                user_context_parts.append(f"- Food Restrictions: {preferences.get('foodrestrictions', 'N/A')}")
                user_context_parts.append(f"- Spicy Food Tolerance: {preferences.get('spicyfoodtolerance', 'N/A')}")
                user_context_parts.append(f"- Sweet Preference: {preferences.get('sweetpreference', 'N/A')}")
                user_context_parts.append("")
                user_context_parts.append("LIFESTYLE:")
                user_context_parts.append(f"- Activity Level: {preferences.get('activitylevel', 'N/A')}")
                user_context_parts.append(f"- Fitness Goal: {preferences.get('fitnessgoal', 'N/A')}")
                user_context_parts.append(f"- Hydration Level: {preferences.get('hydrationlevel', 'N/A')}")
                user_context_parts.append(f"- Average Sleep: {preferences.get('averagesleep', 'N/A')} hours")
                user_context_parts.append(f"- Sleep Quality: {preferences.get('sleepquality', 'N/A')}")
                user_context_parts.append(f"- Caffeine Intake: {preferences.get('caffeineintake', 'N/A')}")
            else:
                user_context_parts.append("DIETARY PREFERENCES: Not provided")
            
            user_context_parts.append("")
             
            if health:
                user_context_parts.append("HEALTH CONDITIONS:")
                try:
                    health_dict = dict(health)
                    health_dict.pop('email', None)
                    important_conditions = []
                    for key, value in health_dict.items():
                        if value and str(value).lower() not in ['none', 'no', '']:
                            formatted_key = key.replace('_', ' ').title()
                            important_conditions.append(f"- {formatted_key}: {value}")
                    if important_conditions:
                        user_context_parts.extend(important_conditions)
                    else:
                        user_context_parts.append("- No specific health conditions reported")
                except Exception:
                    user_context_parts.append("- No specific health conditions reported")
            else:
                user_context_parts.append("HEALTH CONDITIONS: Not provided")
            
            user_context = "\n".join(user_context_parts)
            user_profile_cache[session_id] = user_context
            return {"user_context": user_context}
        finally:
            await conn.close()
    except Exception as e:
        return {"user_context": f"Error fetching user profile: {str(e)}"}


async def compute_health_metrics_node(state: dict):
    """Compute health metrics on-demand using LangGraph."""
    from app.services.graphs.health_metrics_graph import compute_health_metrics
    
    email = state.get("user_email", "")
    if not email:
        return {"health_metrics_context": "No user email provided"}
    
    try:
        result = await compute_health_metrics(email)
        metrics_context = result.get("metrics_context", "Health metrics unavailable")
        return {"health_metrics_context": metrics_context}
    except Exception as e:
        return {"health_metrics_context": f"Could not compute health metrics: {str(e)}"}


def tool_decision_node(state: dict):
    """
    Agentic tool-calling node: asks the LLM whether the user's message
    needs food database information. If yes, runs hybrid search.
    If no, skips retrieval entirely.
    """
    user_message = state.get("user_message", "")
    if not user_message:
        return {"retrieved_context": ""}

    # Ask the LLM whether food retrieval is needed
    decision_prompt = f"""You are a decision classifier. Given the user message below, 
decide if it requires looking up food/nutrition data from a database.

User message: "{user_message}"

Reply with ONLY "YES" or "NO". Nothing else.
- YES: if the message asks about specific foods, nutrients, calories, dietary info, or needs food recommendations
- NO: if it's a greeting, general question, or doesn't need food data"""

    try:
        messages = [{"role": "user", "content": decision_prompt}]
        decision = call_nvidia_api(messages).strip().upper()

        if "YES" in decision:
            print(f"[TOOL] Food retrieval triggered for: '{user_message[:60]}...'")
            retrieved = search_food_database(user_message, k=5)
            return {"retrieved_context": retrieved}
        else:
            print(f"[TOOL] No food retrieval needed for: '{user_message[:60]}...'")
            return {"retrieved_context": ""}

    except Exception as e:
        print(f"[TOOL] Error in tool decision: {e}")
        # Fallback: do the retrieval to be safe
        try:
            retrieved = search_food_database(user_message, k=5)
            return {"retrieved_context": retrieved}
        except Exception:
            return {"retrieved_context": ""}
