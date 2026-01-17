from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os
from app.services.faiss_service import get_food_faiss
from app.db_connect import connect_db
from app.services.cache import user_profile_cache

load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

LLM = ChatNVIDIA(
  model="google/gemma-7b",
  api_key=NVIDIA_API_KEY, 
  temperature=0.5,
  top_p=1,
  max_tokens=4096,
)

# LangGraph State
class ChatState(TypedDict):
    user_message: str
    user_email: str
    session_id: str
    user_context: str
    retrieved_context: str
    summary: str
    response: str

# LangGraph Nodes
async def retrieve_user_node(state: ChatState):
    """Fetch user profile from cache or database."""
    email = state["user_email"]
    session_id = state["session_id"]
    
    # Check cache first
    if session_id in user_profile_cache and user_profile_cache[session_id] is not None:
        state["user_context"] = user_profile_cache[session_id]
        return state
    
    # Cache miss - fetch from database
    conn = await connect_db()
    try:
        personal = await conn.fetchrow("SELECT * FROM personal_details WHERE email=$1", email)
        preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email=$1", email)
        health = await conn.fetchrow("SELECT * FROM health_conditions WHERE email=$1", email)
        metrics = await conn.fetchrow("SELECT * FROM health_metrics WHERE email=$1", email)
        
        # Format as human-readable context
        user_context_parts = []
        
        # Personal Information
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
        
        user_context_parts.append("")  # Blank line
        
        # Dietary Preferences
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
        
        user_context_parts.append("")  # Blank line
        
        # Health Conditions
        if health:
            user_context_parts.append("HEALTH CONDITIONS:")
            # Only show health fields that are actually set
            health_dict = dict(health)
            health_dict.pop('email', None)  # Remove email field
            
            important_conditions = []
            for key, value in health_dict.items():
                if value and value != 'none' and value != '':
                    # Format key from snake_case to Title Case
                    formatted_key = key.replace('_', ' ').title()
                    important_conditions.append(f"- {formatted_key}: {value}")
            
            if important_conditions:
                user_context_parts.extend(important_conditions)
            else:
                user_context_parts.append("- No specific health conditions reported")
        else:
            user_context_parts.append("HEALTH CONDITIONS: Not provided")
        
        user_context_parts.append("")  # Blank line
        
        # Health Metrics
        if metrics:
            user_context_parts.append("HEALTH METRICS:")
            user_context_parts.append(f"- BMI: {metrics.get('bmi', 'N/A'):.1f}")
            user_context_parts.append(f"- BMR: {metrics.get('bmr', 'N/A'):.0f} kcal/day")
            user_context_parts.append(f"- TDEE: {metrics.get('tdee', 'N/A'):.0f} kcal/day")
            user_context_parts.append(f"- Body Fat %: {metrics.get('bfp', 'N/A'):.1f}%")
            user_context_parts.append(f"- Lean Body Mass: {metrics.get('lbm', 'N/A'):.1f} kg")
            user_context_parts.append(f"- Muscle Mass: {metrics.get('muscle_mass', 'N/A'):.1f} kg")
            user_context_parts.append(f"- Protein Intake: {metrics.get('protein_intake', 'N/A'):.0f}g/day")
            user_context_parts.append(f"- Recommended Macros: {metrics.get('macro_nutrients', 'N/A')}")
            user_context_parts.append(f"- Daily Fiber: {metrics.get('fiber', 'N/A')}")
        else:
            user_context_parts.append("HEALTH METRICS: Not calculated yet")
        
        user_context = "\n".join(user_context_parts)
        
        # Cache for future requests in this session
        user_profile_cache[session_id] = user_context
        state["user_context"] = user_context
    finally:
        await conn.close()
    
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

            Reply in a friendly, knowledgeable, and contextual way based on the above info. Be concise unless they ask for details.
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

async def execute_chat(user_message: str, user_email: str, session_id: str, summary: str = "") -> dict:
    """Execute chat processing pipeline."""
    result = await chat_graph.ainvoke({
        "user_message": user_message,
        "user_email": user_email,
        "session_id": session_id,
        "user_context": "",
        "retrieved_context": "",
        "summary": summary,
        "response": "",
    })
    return result