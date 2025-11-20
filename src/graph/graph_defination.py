# src/graph/graph_definition.py

from langgraph.graph import StateGraph, END
from typing import Dict, Any

# Import the shared state definition
from ..memory.state import FinanceState

# Imports for functional nodes
from ..nodes.fetch_data import fetch_node
from ..nodes.transform import transform_node
from .visual import visualize_prices
from .model import call_gemini_api

# ---------------------------------------------------
# Router 1 (Decision Node): router_data_check
# Routes the flow based on whether data analysis is needed.
# ---------------------------------------------------

def router_data_check(state: FinanceState) -> str:
    asset = state.get("asset")
    visual_flag = state.get("visual_requested", False)

    print(f"\n--- ROUTER 1 (Data Check): Asset={asset}, VisualFlag={visual_flag} ---")

    # NEW: User explicitly asked for visual → go directly to visualize
    if visual_flag and asset is None:
        return "visualize"

    # Standard logic
    if asset is None:
        return "model_api"
    else:
        return "transform"


# ---------------------------------------------------
# Router 2:  we visualize before LLM
# ---------------------------------------------------

def router_visualize(state: FinanceState) -> str:
    asset = state.get("asset")
    visual_flag = state.get("visual_requested", False)

    print(f"\n--- ROUTER 2 (Visualization): Asset={asset}, VisualFlag={visual_flag} ---")

    # NEW: visual requested but not a comparison
    if visual_flag and asset is None:
        return "visualize"

    # Existing comparison rule
    if asset == "compare":
        return "visualize"

    return "model_api"


# ---------------------------------------------------
# LangGraph Workflow Definition
# ---------------------------------------------------

def create_finance_graph():
    """
    Creates and compiles the financial analysis workflow graph using LangGraph.
    The graph enforces three distinct, conditional execution paths.
    """
    
    # 1. Initialize the StateGraph
    workflow = StateGraph(FinanceState)

    # 2. Add the nodes
    workflow.add_node("fetch_data", fetch_node)
    workflow.add_node("transform", transform_node)
    workflow.add_node("visualize", visualize_prices)
    workflow.add_node("model_api", call_gemini_api)

    # 3. Define the entry point
    # Note: fetch_data now includes the initial parsing logic
    workflow.set_entry_point("fetch_data")

    # 4. Define conditional and direct edges
    
    # Edge A: Router 1 (from Fetch)
    workflow.add_conditional_edges(
        "fetch_data",      
        router_data_check, 
        {
            "model_api": "model_api", # Simple Query path
            "transform": "transform", # Data Query paths
        }
    )

    # Edge B: Router 2 (from Transform)
    workflow.add_conditional_edges(
        "transform",        
        router_visualize,   
        {
            "visualize": "visualize", # Comparison path
            "model_api": "model_api", # Single Stats path
        }
    )

    # Edge C: Direct Edge (after Visualization, always go to the model)
    workflow.add_edge("visualize", "model_api")

    # Edge D: Final node always leads to the end state
    workflow.add_edge("model_api", END)

    # Compile the graph
    app = workflow.compile()
    
    return app