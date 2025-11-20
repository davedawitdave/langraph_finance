from typing import TypedDict, Optional, List, Dict, Any

class FinanceState(TypedDict):
    """
    Defines the central state for the LangGraph workflow.
    """
    query: str
    
    # 'btc', 'eth', 'compare', or None
    asset: Optional[str]
    
    # Raw price data: { "btc": [{"time":..., "price":...}], ... }
    raw_data: Optional[Dict[str, List[Dict[str, Any]]]]
    
    # Statistics: { "btc": {"min_price":..., "volatility_percent":...} }
    stats: Optional[Dict[str, Any]]
    
    # Base64 encoded image string of the plot (if generated)
    visual: Optional[str]
    
    # Final LLM response
    final_answer: Optional[str]
    llm_output: Optional[str]