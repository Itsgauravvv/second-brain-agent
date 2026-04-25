from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

from agents.ingestion_agent import run_ingestion
from agents.query_agent import run_query
from agents.insight_agent import run_insights

# Define standard state
class AgentState(TypedDict):
    mode: str
    query: str
    files: list
    response: str
    insights: dict
    
def router_node(state: AgentState):
    """
    A dummy node that acts as the entry point before conditional routing.
    In LangGraph, we can just use conditional edges, but we add this for explicit structure.
    """
    return state

def ingestion_node(state: AgentState):
    """Processes uploaded files and updates state."""
    results = run_ingestion()
    return {"files": list(results.keys()), "response": "Ingestion complete."}

def query_node(state: AgentState):
    """Executes a query and updates state."""
    query = state.get("query", "")
    result = run_query(query)
    # result contains {"answer": ..., "sources": ...}
    # We will format this into the response string
    
    answer = result.get("answer", "")
    sources = result.get("sources", [])
    
    response_text = answer
    if sources:
        response_text += "\n\nSources:\n" + "\n".join([f"- {s}" for s in sources])
        
    return {"response": response_text}

def insight_node(state: AgentState):
    """Generates insights and updates state."""
    insights = run_insights()
    return {"insights": insights}

def route_based_on_mode(state: AgentState) -> str:
    """Routing logic determining which agent to run."""
    mode = state.get("mode")
    if mode == "ingest":
        return "ingest"
    elif mode == "query":
        return "query"
    elif mode == "insight":
        return "insight"
    else:
        # Default fallback
        return END

def build_pipeline():
    """Builds and compiles the StateGraph pipeline."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("ingest", ingestion_node)
    workflow.add_node("query", query_node)
    workflow.add_node("insight", insight_node)
    
    # Path: START -> router
    workflow.add_edge(START, "router")
    
    # Conditional Edges from router
    workflow.add_conditional_edges(
        "router",
        route_based_on_mode,
        {
            "ingest": "ingest",
            "query": "query",
            "insight": "insight",
            END: END
        }
    )
    
    # Finish each agent path by pointing to END
    workflow.add_edge("ingest", END)
    workflow.add_edge("query", END)
    workflow.add_edge("insight", END)
    
    # Compile
    return workflow.compile()

# Instantiate pipeline singleton
app_pipeline = build_pipeline()
