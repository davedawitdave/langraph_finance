from langgraph.graph import StateGraph, END
from ..memory.state import FinanceState
from ..nodes.fetch_data import fetch_node
from ..nodes.transform import transform_node
from .visual import visualize_prices
from .model import call_gemini_api

def router_data(state: FinanceState) -> str:
    return "model_api" if state.get('asset') is None else "transform"

def router_visual(state: FinanceState) -> str:
    return "visualize" if state.get('asset') == 'compare' else "model_api"

def create_finance_graph():
    workflow = StateGraph(FinanceState)
    workflow.add_node("fetch_data", fetch_node)
    workflow.add_node("transform", transform_node)
    workflow.add_node("visualize", visualize_prices)
    workflow.add_node("model_api", call_gemini_api)

    workflow.set_entry_point("fetch_data")
    
    workflow.add_conditional_edges("fetch_data", router_data, {"model_api": "model_api", "transform": "transform"})
    workflow.add_conditional_edges("transform", router_visual, {"visualize": "visualize", "model_api": "model_api"})
    
    workflow.add_edge("visualize", "model_api")
    workflow.add_edge("model_api", END)

    return workflow.compile()