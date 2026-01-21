# Cache to store user profiles per session (in-memory)
user_profile_cache = {}

# Cache to hold chat histories per session (in-memory, reset on app restart)
conversation_summaries = {}


def clear_user_cache(session_id: str):
    """Clear cached user profile for a session."""
    if session_id in user_profile_cache:
        del user_profile_cache[session_id]
