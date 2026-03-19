import asyncio
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

from app.services.nodes.retrieval_nodes import (
    retrieve_user_node,
    compute_health_metrics_node,
    tool_decision_node
)
from app.services.nodes.intent_nodes import classify_intent_node, route_by_intent
from app.services.nodes.handler_nodes import (
    handle_meal_plan_node,
    handle_nutrition_query_node,
    handle_health_advice_node,
    handle_general_node,
    summary_node
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


async def parallel_retrieval_node(state: dict):
    """Run user profile and health metrics retrieval in parallel.
    Food retrieval is now handled by the agentic tool_decision_node later."""
    user_task = retrieve_user_node(state)
    health_task = compute_health_metrics_node(state)

    # Run both in parallel (food retrieval is deferred to tool_decision_node)
    user_result, health_result = await asyncio.gather(
        user_task, health_task
    )

    return {
        **user_result,
        **health_result,
    }

def route_after_intent(state: dict) -> str:
    """Route to appropriate handler based on classified intent.
    meal_plan and general skip the tool_decision_node entirely."""
    intent = state.get("intent", "general")
    if intent == "meal_plan":
        return "handle_meal_plan"
    elif intent == "general":
        return "handle_general"
    else:
        # nutrition_query and health_advice go through tool decision first
        return "tool_decision"


def build_chat_graph():
    """Build and compile the chat processing graph with agentic tool calling."""
    graph = StateGraph(ChatState)

    # Add nodes
    graph.add_node("parallel_retrieval", parallel_retrieval_node)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("tool_decision", tool_decision_node)
    graph.add_node("handle_meal_plan", handle_meal_plan_node)
    graph.add_node("handle_nutrition_query", handle_nutrition_query_node)
    graph.add_node("handle_health_advice", handle_health_advice_node)
    graph.add_node("handle_general", handle_general_node)
    graph.add_node("summary", summary_node)

    # Flow: Entry → parallel retrieval (user + health only) → classify intent
    graph.set_entry_point("parallel_retrieval")
    graph.add_edge("parallel_retrieval", "classify_intent")

    # Conditional routing after intent classification
    graph.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "handle_meal_plan": "handle_meal_plan",
            "handle_general": "handle_general",
            "tool_decision": "tool_decision",
        }
    )

    # After tool_decision, route to the specific handler based on intent
    graph.add_conditional_edges(
        "tool_decision",
        route_by_intent,
        {
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
    graph.add_edge("summary", END)

    return graph.compile()


chat_graph = build_chat_graph()


async def execute_chat(user_message: str, user_email: str, session_id: str, summary: str = "") -> dict:
    """Execute chat processing pipeline with agentic tool calling."""
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
