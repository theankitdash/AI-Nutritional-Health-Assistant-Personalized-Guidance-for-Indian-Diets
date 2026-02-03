from fastapi import APIRouter, HTTPException, Cookie
import traceback 
from app.models import ChatRequest
from app.routers.auth import get_session_email
from app.services.graphs.chat_graph import execute_chat
from app.services.cache import conversation_summaries, user_profile_cache, clear_user_cache

router = APIRouter()

@router.post("/chat/")
async def chat(chat: ChatRequest, session_id: str = Cookie(None)):
    try:
        email = await get_session_email(session_id)

        if session_id not in conversation_summaries:
            conversation_summaries[session_id] = ""
        
        # Check if user profile is cached for this session
        if session_id not in user_profile_cache:
            # Cache miss - will be fetched by retrieve_user_node
            user_profile_cache[session_id] = None

        result = await execute_chat(chat.message, email, session_id, conversation_summaries[session_id])
        
        # Update summary for next conversation turn
        conversation_summaries[session_id] = result["summary"]

        return {"bot_response": result["response"]}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Chat processing failed")
