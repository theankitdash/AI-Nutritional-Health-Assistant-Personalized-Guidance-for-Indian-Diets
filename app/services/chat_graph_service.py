from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.services.faiss_service import get_food_faiss
from app.db_connect import connect_db
from app.services.cache import user_profile_cache
from app.services.nvidia_api_service import call_nvidia_api
from app.services.health_metrics_graph import compute_health_metrics
from app.services.meal_planning_graph import generate_meal_plan

# Intent types
IntentType = Literal["meal_plan", "nutrition_query", "health_advice", "general"]

# LangGraph State
class ChatState(TypedDict):
    user_message: str
    user_email: str
    session_id: str
    user_context: str
    health_metrics_context: str
    retrieved_context: str
    summary: str
    response: str
    intent: IntentType
    meal_plan: str  # For meal planning responses


# ============ RETRIEVAL NODES ============

async def retrieve_user_node(state: ChatState):
    """Fetch user profile from cache or database."""
    email = state.get("user_email", "")
    session_id = state.get("session_id", "")
    
    if not email:
        return {"user_context": "No user email provided"}
    
    # Check cache first
    if session_id in user_profile_cache and user_profile_cache[session_id] is not None:
        return {"user_context": user_profile_cache[session_id]}
    
    # Cache miss - fetch from database
    try:
        conn = await connect_db()
        try:
            personal = await conn.fetchrow("SELECT * FROM personal_details WHERE email=$1", email)
            preferences = await conn.fetchrow("SELECT * FROM preferences WHERE email=$1", email)
            health = await conn.fetchrow("SELECT * FROM health_conditions WHERE email=$1", email)
            
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
            
            user_context_parts.append("")
            
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
            
            user_context_parts.append("")
             
            # Health Conditions
            if health:
                user_context_parts.append("HEALTH CONDITIONS:")
                try:
                    health_dict = dict(health)
                    health_dict.pop('email', None)
                    
                    important_conditions = []
                    for key, value in health_dict.items():
                        if value and str(value).lower() not in ['none', 'no', '']:
                            formatted_key = key.replace('_', ' ').title()
                            important_conditions.append(f"- {formatted_key}: {value}")
                    
                    if important_conditions:
                        user_context_parts.extend(important_conditions)
                    else:
                        user_context_parts.append("- No specific health conditions reported")
                except Exception:
                    user_context_parts.append("- No specific health conditions reported")
            else:
                user_context_parts.append("HEALTH CONDITIONS: Not provided")
            
            user_context = "\n".join(user_context_parts)
            
            # Cache for future requests
            user_profile_cache[session_id] = user_context
            return {"user_context": user_context}
        finally:
            await conn.close()
    except Exception as e:
        return {"user_context": f"Error fetching user profile: {str(e)}"}


async def compute_health_metrics_node(state: ChatState):
    """Compute health metrics on-demand using LangGraph."""
    email = state.get("user_email", "")
    
    if not email:
        return {"health_metrics_context": "No user email provided"}
    
    try:
        result = await compute_health_metrics(email)
        metrics_context = result.get("metrics_context", "Health metrics unavailable")
        return {"health_metrics_context": metrics_context}
    except Exception as e:
        return {"health_metrics_context": f"Could not compute health metrics: {str(e)}"}


def retrieve_food_node(state: ChatState):
    """Retrieve relevant food information from FAISS index."""
    try:
        food_faiss = get_food_faiss()
        if food_faiss is None:
            return {"retrieved_context": "Food database not available"}
        
        user_message = state.get("user_message", "")
        if not user_message:
            return {"retrieved_context": ""}
            
        docs = food_faiss.similarity_search(user_message, k=3)
        retrieved = "\n\n".join(d.page_content for d in docs)
        return {"retrieved_context": retrieved}
    except Exception as e:
        return {"retrieved_context": f"Error retrieving food data: {str(e)}"}


# ============ INTENT CLASSIFICATION ============

def classify_intent_node(state: ChatState):
    """Classify the user's intent to route to appropriate handler."""
    user_message = state.get("user_message", "")
    
    if not user_message:
        return {"intent": "general"}
    
    # Use LLM for intent classification
    classify_prompt = f"""Classify the following user message into ONE of these categories:
- meal_plan: User wants a meal plan, diet schedule, or food recommendations for a day/week
- nutrition_query: User is asking about calories, nutrients, or specific food information
- health_advice: User is asking for health-related advice based on their conditions
- general: General conversation, greetings, or other topics

User message: "{user_message}"

Respond with ONLY the category name (meal_plan, nutrition_query, health_advice, or general). Nothing else."""

    try:
        messages = [{"role": "user", "content": classify_prompt}]
        result = call_nvidia_api(messages).strip().lower()
        
        # Validate and assign intent
        valid_intents = ["meal_plan", "nutrition_query", "health_advice", "general"]
        if result in valid_intents:
            return {"intent": result}
        else:
            return {"intent": "general"}
    except Exception:
        return {"intent": "general"}


# ============ INTENT HANDLERS ============

async def handle_meal_plan_node(state: ChatState):
    """Handle meal planning requests using the dedicated meal planning graph."""
    try:
        # Use the dedicated meal planning agent for sophisticated meal plans
        result = await generate_meal_plan(
            email=state.get("user_email", ""),
            user_request=state.get("user_message", "")
        )
        
        # Get the formatted meal plan from the result
        meal_plan = result.get("final_meal_plan", "")
        
        if meal_plan:
            return {"response": meal_plan, "meal_plan": meal_plan}
        else:
            return {
                "response": "I apologize, but I couldn't generate a meal plan at this time. Please try again.",
                "meal_plan": ""
            }
    except Exception as e:
        return {
            "response": f"I encountered an issue creating your meal plan. Please try again. Error: {str(e)}",
            "meal_plan": ""
        }


def handle_nutrition_query_node(state: ChatState):
    """Handle nutrition-related queries about food and nutrients."""
    prompt = f"""You are a nutrition expert specializing in Indian foods.

*User Profile*:
{state.get("user_context", "Not available")}

*Health Metrics*:
{state.get("health_metrics_context", "Not available")}

*Indian Food Database*:
{state.get("retrieved_context", "Not available")}

*User Question*:
{state.get("user_message", "")}

Provide accurate nutrition information. Be specific about key nutrients.
Keep your response concise and under 100 words unless the user asks for details."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = call_nvidia_api(messages)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing nutrition query: {str(e)}"}


def handle_health_advice_node(state: ChatState):
    """Handle health-related advice requests."""
    prompt = f"""You are a health-aware nutrition advisor for Indian diets.

*User Profile*:
{state.get("user_context", "Not available")}

*Health Metrics*:
{state.get("health_metrics_context", "Not available")}

*User's Health Conditions*:
Check their profile for conditions like diabetes, hypertension, cholesterol, etc.

*Indian Food Database*:
{state.get("retrieved_context", "Not available")}

*User Question*:
{state.get("user_message", "")}

Give brief, practical health advice. Keep your response concise and under 100 words unless the user asks for details.
Note: This is general nutrition guidance, not medical advice."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = call_nvidia_api(messages)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing health advice: {str(e)}"}


def handle_general_node(state: ChatState):
    """Handle general conversation and other queries."""
    prompt = f"""You are a friendly Indian nutrition assistant.

*User Profile*:
{state.get("user_context", "Not available")}

*Health Metrics*:
{state.get("health_metrics_context", "Not available")}

*Indian Food Database*:
{state.get("retrieved_context", "Not available")}

*Conversation Summary*:
{state.get("summary", "")}

*User Message*:
{state.get("user_message", "")}

Keep your response friendly and concise (under 100 words). Only elaborate if the user asks for details."""

    try:
        messages = [{"role": "user", "content": prompt}]
        result = call_nvidia_api(messages)
        return {"response": result.strip()}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}


# ============ SUMMARY NODE ============

def summary_node(state: ChatState):
    """Update conversation summary."""
    summary_prompt = f"""You are updating a running conversation summary.

Existing summary:
{state.get('summary', '')}

New interaction:
User: {state.get('user_message', '')}
Assistant: {state.get('response', '')}

Update the summary using ONLY explicit information.
- Preserve user goals, constraints, preferences, and unresolved questions
- Remove redundancy
- Do NOT infer or assume anything
- Keep it under 120 words"""

    try:
        messages = [{"role": "user", "content": summary_prompt}]
        result = call_nvidia_api(messages)
        return {"summary": result.strip()}
    except Exception:
        return {"summary": state.get('summary', '')}


# ============ ROUTING LOGIC ============

def route_by_intent(state: ChatState) -> str:
    """Route to appropriate handler based on classified intent."""
    intent = state.get("intent", "general")
    
    intent_to_handler = {
        "meal_plan": "handle_meal_plan",
        "nutrition_query": "handle_nutrition_query",
        "health_advice": "handle_health_advice",
        "general": "handle_general",
    }
    
    return intent_to_handler.get(intent, "handle_general")


# ============ BUILD GRAPH ============

def build_chat_graph():
    """Build and compile the chat processing graph with intent routing."""
    graph = StateGraph(ChatState)

    # Add all nodes
    graph.add_node("user_retrieval", retrieve_user_node)
    graph.add_node("health_metrics", compute_health_metrics_node)
    graph.add_node("food_retrieval", retrieve_food_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("handle_meal_plan", handle_meal_plan_node)
    graph.add_node("handle_nutrition_query", handle_nutrition_query_node)
    graph.add_node("handle_health_advice", handle_health_advice_node)
    graph.add_node("handle_general", handle_general_node)
    graph.add_node("summary", summary_node)

    # Define flow
    # Entry: user_retrieval -> health_metrics -> food_retrieval -> classify_intent
    graph.set_entry_point("user_retrieval")
    graph.add_edge("user_retrieval", "health_metrics")
    graph.add_edge("health_metrics", "food_retrieval")
    graph.add_edge("food_retrieval", "classify_intent")
    
    # Conditional routing based on intent
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "handle_meal_plan": "handle_meal_plan",
            "handle_nutrition_query": "handle_nutrition_query",
            "handle_health_advice": "handle_health_advice",
            "handle_general": "handle_general",
        }
    )
    
    # All handlers converge to summary
    graph.add_edge("handle_meal_plan", "summary")
    graph.add_edge("handle_nutrition_query", "summary")
    graph.add_edge("handle_health_advice", "summary")
    graph.add_edge("handle_general", "summary")
    
    # Summary to END
    graph.add_edge("summary", END)

    return graph.compile()


# Build graph once at module load
chat_graph = build_chat_graph()


async def execute_chat(user_message: str, user_email: str, session_id: str, summary: str = "") -> dict:
    """Execute chat processing pipeline with intent routing."""
    result = await chat_graph.ainvoke({
        "user_message": user_message,
        "user_email": user_email,
        "session_id": session_id,
        "user_context": "",
        "health_metrics_context": "",
        "retrieved_context": "",
        "summary": summary,
        "response": "",
        "intent": "general",
        "meal_plan": "",
    })
    return result