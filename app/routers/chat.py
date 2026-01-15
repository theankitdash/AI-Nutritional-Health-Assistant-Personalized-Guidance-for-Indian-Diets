from typing import TypedDict, List
from fastapi import APIRouter, HTTPException, Cookie
from dotenv import load_dotenv
import os, json, traceback, faiss

from langgraph.graph import StateGraph, END
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings

from app.models import ChatRequest
from app.routers.auth import get_session_email

router = APIRouter()
load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

LLM = ChatNVIDIA(
  model="google/gemma-7b",
  api_key=NVIDIA_API_KEY, 
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
)

# Build FAISS vectorstore manually — no pickle, no deserialization flag needed
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Global variables to store FAISS indexes (loaded once at startup)
food_faiss = None
user_faiss = None

# A dict to hold chat histories per session (in-memory, reset on app restart)
chat_histories = {}

def load_faiss_index():
    
    # Load FAISS index
    food_index = faiss.read_index("app/food_dataset/index.faiss")
    user_index = faiss.read_index("app/user_embeddings/index.faiss")
    
    # Load texts from JSON
    with open("app/food_dataset/index.json", encoding="utf-8") as f:
        food_texts = json.load(f)

    with open("app/user_embeddings/index.json", encoding="utf-8") as f:
        user_texts = json.load(f)
    
    # Convert to LangChain Documents
    food_docs = [Document(page_content=t) for t in food_texts]
    user_docs = [Document(page_content=t) for t in user_texts]

     # Build individual docstores
    food_store = InMemoryDocstore({f"food_{i}": d for i, d in enumerate(food_docs)})
    user_store = InMemoryDocstore({f"user_{i}": d for i, d in enumerate(user_docs)})

    # Index-to-ID mapping
    food_map = {i: f"food_{i}" for i in range(len(food_docs))}
    user_map = {i: f"user_{i}" for i in range(len(user_docs))}

    return (
        FAISS(embedding, food_index, food_store, food_map),
        FAISS(embedding, user_index, user_store, user_map),
    )

def initialize_faiss_indexes():
    global food_faiss, user_faiss
    food_faiss, user_faiss = load_faiss_index()

# LangGraph State
class ChatState(TypedDict):
    user_message: str
    user_context: str
    retrieved_context: str
    messages: List[BaseMessage]
    response: str

# LangGraph Nodes
def retrieve_user_node(state: ChatState):
    docs = user_faiss.similarity_search(state["user_message"], k=1)
    state["user_context"] = "\n\n".join(d.page_content for d in docs)
    return state

def retrieve_food_node(state: ChatState):
    docs = food_faiss.similarity_search(state["user_message"], k=3)
    state["retrieved_context"] = "\n\n".join(d.page_content for d in docs)
    return state

def llm_node(state: ChatState):
    prompt = PromptTemplate(    
        input_variables=["user_context", "retrieved_context", "conversation_history", "user_message"],
            template=""" 
            You are a personalized nutrition assistant specialized in Indian dietary habits. 
            Use the user's health metrics, preferences, and health conditions to respond naturally.

            *User Profile*:
            {user_context}

            *Indian Nutrition Database*:
            {retrieved_context}

            *Conversation History*:
            {conversation_history}

            *User's Current Message*:
            {user_message}

            Reply in a friendly, knowledgeable, and contextual way based on the above info.
            """
    )

    history_text = "\n".join(
        f"{'User' if m.type=='human' else 'Assistant'}: {m.content}"
        for m in state["messages"]
    )

    final_prompt = prompt.format(
        user_context=state["user_context"],
        retrieved_context=state["retrieved_context"],
        conversation_history=history_text,
        user_message=state["user_message"],
    )

    result = LLM.invoke(final_prompt)
    state["response"] = result.content
    state["messages"].append(AIMessage(content=result.content))
    return state

# Build Graph
graph = StateGraph(ChatState)

graph.add_node("user_retrieval", retrieve_user_node)
graph.add_node("food_retrieval", retrieve_food_node)
graph.add_node("llm", llm_node)

graph.set_entry_point("user_retrieval")
graph.add_edge("user_retrieval", "food_retrieval")
graph.add_edge("food_retrieval", "llm")
graph.add_edge("llm", END)

chat_graph = graph.compile()

@router.post("/chat/")
async def chat(chat: ChatRequest, session_id: str = Cookie(None)):
    try:
        await get_session_email(session_id)

        if session_id not in chat_histories:
            chat_histories[session_id] = InMemoryChatMessageHistory()

        history = chat_histories[session_id]
        history.add_user_message(chat.message)

        result = chat_graph.invoke({
            "user_message": chat.message,
            "messages": history.messages,
            "user_context": "",
            "retrieved_context": "",
            "response": "",
        })

        return {"bot_response": result["response"]}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Chat processing failed")
