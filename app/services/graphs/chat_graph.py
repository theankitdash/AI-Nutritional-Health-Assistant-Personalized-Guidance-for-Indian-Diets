from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

from app.services.nodes.retrieval_nodes import fetch_context_node, search_food_node
from app.services.nodes.intent_nodes import classify_intent_node, route_by_intent
from app.services.nodes.handler_nodes import (
    handle_meal_plan_node,
    handle_nutrition_query_node,
    handle_health_advice_node,
    handle_general_node,
)

IntentType = Literal["meal_plan", "nutrition_query", "health_advice", "general"]

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
    meal_plan: str


def route_after_intent(state: dict) -> str:
    """
    Route to appropriate handler based on classified intent.

    nutrition_query, health_advice, meal_plan → search_food first
    general → skip food search entirely
    """
    intent = state.get("intent", "general")
    if intent in ("nutrition_query", "health_advice", "meal_plan"):
        return "search_food"
    else:
        return "handle_general"


def route_after_search(state: dict) -> str:
    """Route to the correct handler after food search completes."""
    intent = state.get("intent", "general")
    if intent == "nutrition_query":
        return "handle_nutrition_query"
    elif intent == "health_advice":
        return "handle_health_advice"
    elif intent == "meal_plan":
        return "handle_meal_plan"
    return "handle_general"


def build_chat_graph():
    """Build the optimized chat processing graph.

    Pipeline (2 LLM calls per message — intent classification is now local/instant):
        fetch_context(cached) → classify_intent(local rules) → [search_food] → handler(LLM) → END

    """
    graph = StateGraph(ChatState)

    # Nodes
    graph.add_node("fetch_context", fetch_context_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("search_food", search_food_node)
    graph.add_node("handle_meal_plan", handle_meal_plan_node)
    graph.add_node("handle_nutrition_query", handle_nutrition_query_node)
    graph.add_node("handle_health_advice", handle_health_advice_node)
    graph.add_node("handle_general", handle_general_node)

    # Flow: Entry → fetch cached context → classify intent (instant, local)
    graph.set_entry_point("fetch_context")
    graph.add_edge("fetch_context", "classify_intent")

    # After intent: route to food search or directly to general handler
    graph.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "search_food": "search_food",
            "handle_general": "handle_general",
        },
    )

    # After food search: route to the correct handler
    graph.add_conditional_edges(
        "search_food",
        route_after_search,
        {
            "handle_nutrition_query": "handle_nutrition_query",
            "handle_health_advice": "handle_health_advice",
            "handle_meal_plan": "handle_meal_plan",
            "handle_general": "handle_general",
        },
    )

    # All handlers go to END (summary runs as background task in the router)
    graph.add_edge("handle_meal_plan", END)
    graph.add_edge("handle_nutrition_query", END)
    graph.add_edge("handle_health_advice", END)
    graph.add_edge("handle_general", END)

    return graph.compile()


chat_graph = build_chat_graph()


async def execute_chat(user_message: str, user_email: str, session_id: str, summary: str = "") -> dict:
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
