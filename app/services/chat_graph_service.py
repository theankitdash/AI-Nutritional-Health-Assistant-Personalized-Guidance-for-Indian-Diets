from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os
from app.services.faiss_service import get_food_faiss, get_user_faiss

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

LLM = ChatNVIDIA(
  model="google/gemma-7b",
  api_key=NVIDIA_API_KEY, 
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
)

# LangGraph State
class ChatState(TypedDict):
    user_message: str
    user_context: str
    retrieved_context: str
    summary: str
    response: str

# LangGraph Nodes
def retrieve_user_node(state: ChatState):
    user_faiss = get_user_faiss()
    docs = user_faiss.similarity_search(state["user_message"], k=1)
    state["user_context"] = "\n\n".join(d.page_content for d in docs)
    return state

def retrieve_food_node(state: ChatState):
    food_faiss = get_food_faiss()
    docs = food_faiss.similarity_search(state["user_message"], k=3)
    state["retrieved_context"] = "\n\n".join(d.page_content for d in docs)
    return state

#Summary flow
def summary_node(state: ChatState):
    summary_prompt = f"""
        You are updating a running conversation summary.

        Existing summary:
        {state['summary']}

        New interaction:
        User: {state['user_message']}
        Assistant: {state['response']}

        Update the summary using ONLY explicit information.
        - Preserve user goals, constraints, preferences, and unresolved questions
        - Remove redundancy
        - Do NOT infer or assume anything
        - Keep it under 120 words
        """

    result = LLM.invoke(summary_prompt)
    state["summary"] = result.content.strip()
    return state

def llm_node(state: ChatState):
    prompt = f"""
            You are a personalized nutrition assistant specialized in Indian dietary habits. 
            Use the user's health metrics, preferences, and health conditions to respond naturally.

            *User Profile*:
            {state["user_context"]}

            *Indian Nutrition Database*:
            {state["retrieved_context"]}

            *Conversation Summary*:
            {state["summary"]}

            *User's Current Message*:
            {state["user_message"]}

            Reply in a friendly, knowledgeable, and contextual way based on the above info.
            """
    

    result = LLM.invoke(prompt)
    state["response"] = result.content.strip()
    return state

# Build Graph
def build_chat_graph():
    """Build and compile the chat processing graph."""
    graph = StateGraph(ChatState)

    graph.add_node("user_retrieval", retrieve_user_node)
    graph.add_node("food_retrieval", retrieve_food_node)
    graph.add_node("summary", summary_node)
    graph.add_node("llm", llm_node)

    graph.set_entry_point("user_retrieval")
    graph.add_edge("user_retrieval", "food_retrieval")
    graph.add_edge("food_retrieval", "llm")
    graph.add_edge("llm", "summary")
    graph.add_edge("summary", END)

    return graph.compile()

# Build graph once at module load
chat_graph = build_chat_graph()

def execute_chat(user_message: str, summary: str = "") -> dict:
    """Execute chat processing pipeline."""
    result = chat_graph.invoke({
        "user_message": user_message,
        "user_context": "",
        "retrieved_context": "",
        "summary": summary,
        "response": "",
    })
    return result