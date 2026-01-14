from fastapi import APIRouter, HTTPException, Cookie
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.routers.auth import get_session_email
from app.models import ChatRequest
from dotenv import load_dotenv
import os
import faiss
import json
import traceback

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
    with open("app/food_dataset/index.json", "r", encoding="utf-8") as f:
        food_texts = json.load(f)

    with open("app/user_embeddings/index.json", "r", encoding="utf-8") as f:
        user_texts = json.load(f)

    # Convert to LangChain Documents
    food_docs = [Document(page_content=txt) for txt in food_texts]
    user_docs = [Document(page_content=txt) for txt in user_texts]

    # Build individual docstores
    food_docstore = InMemoryDocstore(dict(zip([f"food_{i}" for i in range(len(food_docs))], food_docs)))
    user_docstore = InMemoryDocstore(dict(zip([f"user_{i}" for i in range(len(user_docs))], user_docs)))

    # Index-to-ID mapping
    food_index_map = {i: f"food_{i}" for i in range(len(food_docs))}
    user_index_map = {i: f"user_{i}" for i in range(len(user_docs))}

    # Create FAISS instances
    food_faiss = FAISS(
        embedding_function=embedding,
        index=food_index,
        docstore=food_docstore,
        index_to_docstore_id=food_index_map,
    )

    user_faiss = FAISS(
        embedding_function=embedding,
        index=user_index,
        docstore=user_docstore,
        index_to_docstore_id=user_index_map,
    )

    return food_faiss, user_faiss

def initialize_faiss_indexes():
    """Initialize FAISS indexes at startup. Called once when app starts."""
    global food_faiss, user_faiss
    food_faiss, user_faiss = load_faiss_index()

@router.post("/chat/")
async def chat_with_bot(chat: ChatRequest, session_id: str = Cookie(None)):
    global food_faiss, user_faiss
    
    email = await get_session_email(session_id)

    # Initialize chat history for this session if not present
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatMessageHistory()

    chat_history = chat_histories[session_id]

    # Use pre-loaded FAISS indexes (loaded at startup)
    # No need to load on every request - significant performance improvement

    try:
        # Search FAISS index
        user_docs = user_faiss.similarity_search(chat.message, k=1)
        retrieved_docs = food_faiss.similarity_search(chat.message, k=3)

        # Combine the retrieved documents into a string
        user_context = "\n\n".join([doc.page_content for doc in user_docs])
        retrieved_context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Add user's message to chat history
        chat_history.add_user_message(chat.message)
        #print(f"[ChatHistory] Added user message: {chat.message}")

        # Convert chat history to formatted string for prompt
        conversation_history = "\n".join(
            f"{'User' if msg.type == 'human' else 'Assistant'}: {msg.content}"
            for msg in chat_history.messages
        )

        # Create the prompt
        prompt_template = PromptTemplate(
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

        chain = prompt_template | LLM

        bot_response = chain.invoke({
            "user_context": user_context,
            "retrieved_context": retrieved_context,
            "conversation_history": conversation_history,
            "user_message": chat.message
        })

        if isinstance(bot_response, BaseMessage):
            response = bot_response.content
            chat_history.add_ai_message(response)
            #print(f"[ChatHistory] Added AI message: {response}")
        else:
            response = str(bot_response)
            chat_history.add_ai_message(response)
            #print(f"[ChatHistory] Added AI message: {response}")

        return {"bot_response": response}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error processing the chat request.")  