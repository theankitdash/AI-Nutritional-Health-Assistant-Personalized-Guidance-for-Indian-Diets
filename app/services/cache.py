# Cache to store user profiles per session (in-memory)
user_profile_cache = {}

# Cache to hold chat histories per session (in-memory, reset on app restart)
conversation_summaries = {}

# Cache for health metrics per email — metrics (BMI, BMR, TDEE, etc.)
# don't change between messages, only when the user updates their profile.
health_metrics_cache = {}


def clear_user_cache(session_id: str):
    """Clear cached user profile for a session."""
    if session_id in user_profile_cache:
        del user_profile_cache[session_id]

def clear_health_metrics_cache(email: str):
    """Clear cached health metrics when user updates their profile."""
    if email in health_metrics_cache:
        del health_metrics_cache[email]
