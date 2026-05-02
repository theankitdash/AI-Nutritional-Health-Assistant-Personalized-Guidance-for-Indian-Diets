from fastapi import APIRouter, HTTPException, Cookie, BackgroundTasks
import traceback 
from app.models import ChatRequest
from app.routers.auth import get_session_email
from app.services.graphs.chat_graph import execute_chat
from app.services.cache import conversation_summaries, user_profile_cache
from app.services.nodes.handler_nodes import update_summary

router = APIRouter()


async def _background_summary_update(session_id: str, user_message: str, response: str):
    try:
        existing = conversation_summaries.get(session_id, "")
        new_summary = await update_summary(user_message, response, existing)
        conversation_summaries[session_id] = new_summary
    except Exception:
        # Summary failure should never crash the app
        traceback.print_exc()


@router.post("/chat/")
async def chat(chat: ChatRequest, background_tasks: BackgroundTasks, session_id: str = Cookie(None)):
    try:
        email = await get_session_email(session_id)

        if session_id not in conversation_summaries:
            conversation_summaries[session_id] = ""
        
        # Check if user profile is cached for this session
        if session_id not in user_profile_cache:
            # Cache miss - will be fetched by fetch_context_node
            user_profile_cache[session_id] = None

        result = await execute_chat(chat.message, email, session_id, conversation_summaries[session_id])
        
        # Fire-and-forget: update summary in the background
        background_tasks.add_task(
            _background_summary_update,
            session_id,
            chat.message,
            result["response"],
        )

        return {"bot_response": result["response"]}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Chat processing failed")
