from app.db_connect import get_pool
from app.services.cache import user_profile_cache, health_metrics_cache

async def fetch_context_node(state: dict):
    
    email = state.get("user_email", "")
    session_id = state.get("session_id", "")

    user_context = "No user email provided"
    health_metrics_context = "Health metrics unavailable"

    if not email:
        return {
            "user_context": user_context,
            "health_metrics_context": health_metrics_context,
        }

    # --- User Profile (cached per session) ---
    if session_id in user_profile_cache and user_profile_cache[session_id] is not None:
        user_context = user_profile_cache[session_id]
    else:
        user_context = await _fetch_user_profile(email)
        user_profile_cache[session_id] = user_context

    # --- Health Metrics (cached per email — only changes on profile update) ---
    if email in health_metrics_cache:
        health_metrics_context = health_metrics_cache[email]
    else:
        health_metrics_context = await _compute_and_cache_health_metrics(email)

    return {
        "user_context": user_context,
        "health_metrics_context": health_metrics_context,
    }


async def _fetch_user_profile(email: str) -> str:
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            personal = await conn.fetchrow("SELECT * FROM personal_details WHERE email=$1", email)
            preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email=$1", email)
            health = await conn.fetchrow("SELECT * FROM health_conditions WHERE email=$1", email)

        parts = []

        if personal:
            parts.append("PERSONAL DETAILS:")
            parts.append(f"- Name: {personal.get('name', 'N/A')}")
            parts.append(f"- Age: {personal.get('dateofbirth', 'N/A')}")
            parts.append(f"- Gender: {personal.get('gender', 'N/A')}")
            parts.append(f"- Height: {personal.get('height', 'N/A')} cm")
            parts.append(f"- Weight: {personal.get('weight', 'N/A')} kg")
            parts.append(f"- Waist: {personal.get('waist', 'N/A')} cm")
        else:
            parts.append("PERSONAL DETAILS: Not provided")

        parts.append("")

        if preferences:
            parts.append("DIETARY PREFERENCES:")
            parts.append(f"- Food Preference: {preferences.get('foodpreference', 'N/A')}")
            parts.append(f"- Cuisine Preferences: {preferences.get('cuisinepreferences', 'N/A')}")
            parts.append(f"- Meal Frequency: {preferences.get('mealfrequency', 'N/A')}")
            parts.append(f"- Favorite Meal: {preferences.get('favoritemeal', 'N/A')}")
            parts.append(f"- Snack Preferences: {preferences.get('snackpreferences', 'N/A')}")
            parts.append(f"- Food Restrictions: {preferences.get('foodrestrictions', 'N/A')}")
            parts.append(f"- Spicy Food Tolerance: {preferences.get('spicyfoodtolerance', 'N/A')}")
            parts.append(f"- Sweet Preference: {preferences.get('sweetpreference', 'N/A')}")
            parts.append("")
            parts.append("LIFESTYLE:")
            parts.append(f"- Activity Level: {preferences.get('activitylevel', 'N/A')}")
            parts.append(f"- Fitness Goal: {preferences.get('fitnessgoal', 'N/A')}")
            parts.append(f"- Hydration Level: {preferences.get('hydrationlevel', 'N/A')}")
            parts.append(f"- Average Sleep: {preferences.get('averagesleep', 'N/A')} hours")
            parts.append(f"- Sleep Quality: {preferences.get('sleepquality', 'N/A')}")
            parts.append(f"- Caffeine Intake: {preferences.get('caffeineintake', 'N/A')}")
        else:
            parts.append("DIETARY PREFERENCES: Not provided")

        parts.append("")

        if health:
            parts.append("HEALTH CONDITIONS:")
            try:
                health_dict = dict(health)
                health_dict.pop('email', None)
                important_conditions = []
                for key, value in health_dict.items():
                    if value and str(value).lower() not in ['none', 'no', '']:
                        formatted_key = key.replace('_', ' ').title()
                        important_conditions.append(f"- {formatted_key}: {value}")
                if important_conditions:
                    parts.extend(important_conditions)
                else:
                    parts.append("- No specific health conditions reported")
            except Exception:
                parts.append("- No specific health conditions reported")
        else:
            parts.append("HEALTH CONDITIONS: Not provided")

        return "\n".join(parts)
    except Exception as e:
        return f"Error fetching user profile: {str(e)}"


async def _compute_and_cache_health_metrics(email: str) -> str:

    try:
        from app.services.graphs.health_metrics_graph import compute_health_metrics
        result = await compute_health_metrics(email)
        metrics_context = result.get("metrics_context", "Health metrics unavailable")
        health_metrics_cache[email] = metrics_context
        return metrics_context
    except Exception as e:
        return f"Could not compute health metrics: {str(e)}"


def search_food_node(state: dict):
    user_message = state.get("user_message", "")
    if not user_message:
        return {"retrieved_context": ""}

    try:
        from app.services.tools import search_food_database
        print(f"[SEARCH] Food retrieval for: '{user_message[:60]}...'")
        retrieved = search_food_database(user_message, k=5)
        return {"retrieved_context": retrieved}
    except Exception as e:
        print(f"[SEARCH] Error in food search: {e}")
        return {"retrieved_context": ""}
