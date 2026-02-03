from app.db_connect import connect_db
from app.services.cache import user_profile_cache
from app.services.faiss_service import get_food_faiss


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


def retrieve_food_node(state: dict):
    """Retrieve relevant food information from FAISS index."""
    try:
        food_faiss = get_food_faiss()
        if food_faiss is None:
            return {"retrieved_context": "Food database not available"}
        
        user_message = state.get("user_message", "")
        if not user_message:
            return {"retrieved_context": ""}
            
        docs = food_faiss.similarity_search(user_message, k=3)
        retrieved = "\n\n".join(d.page_content for d in docs)
        return {"retrieved_context": retrieved}
    except Exception as e:
        return {"retrieved_context": f"Error retrieving food data: {str(e)}"}
