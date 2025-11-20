
from typing import TypedDict, Optional, List, Dict, Any

class FinanceState(TypedDict):
    """
    Defines the central state for the LangGraph workflow, allowing nodes 
    to pass data and metadata seamlessly.
    
    Keys and their purpose:
    - query: The original user request string.
    - raw_data: Dictionary of mock price data.
    - asset: The classification mode: 'btc', 'eth', 'compare', or None (for simple queries).
    - stats: Dictionary of calculated statistical metrics.
    - visual: Markdown/text artifact for LLM grounding (used in comparison path).
    - final_answer: The final synthesized LLM response.
    """
    query: str
    raw_data: Optional[Dict[str, List[Dict[str, Any]]]]
    asset: Optional[str]
    stats: Optional[Dict[str, Dict[str, float]]]
    visual: Optional[str]
    final_answer: Optional[str]