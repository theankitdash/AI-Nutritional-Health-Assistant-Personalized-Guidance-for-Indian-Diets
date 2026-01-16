from fastapi import APIRouter, HTTPException, Cookie
import traceback 

from app.models import ChatRequest
from app.routers.auth import get_session_email
from app.services.chat_graph_service import execute_chat

router = APIRouter()

# A dict to hold chat histories per session (in-memory, reset on app restart)
conversation_summaries = {}

@router.post("/chat/")
async def chat(chat: ChatRequest, session_id: str = Cookie(None)):
    try:
        await get_session_email(session_id)

        if session_id not in conversation_summaries:
            conversation_summaries[session_id] = ""

        result = execute_chat(chat.message, conversation_summaries[session_id])
        
        # Update summary for next conversation turn
        conversation_summaries[session_id] = result["summary"]

        return {"bot_response": result["response"]}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Chat processing failed")
