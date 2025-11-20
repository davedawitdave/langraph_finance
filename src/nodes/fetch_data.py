# src/nodes/fetch_data.py

import time
from typing import Dict, Any
from ..memory.state import FinanceState

# Mock Data Source
MOCK_PRICES = {
    'btc': [
        {'time': i, 'price': 60000 + i * 10 + (i % 5) * 500} for i in range(7)
    ],
    'eth': [
        {'time': i, 'price': 3000 + i * 5 + (i % 3) * 150} for i in range(7)
    ]
}

# -----------------------------------------
# Helper: Detect if user wants a visual
# -----------------------------------------
def detect_visual_intent(query: str) -> bool:
    visual_keywords = [
        "visual", "plot", "chart", "graph", "show me",
        "illustrate", "diagram", "figure", "visualize"
    ]
    q = query.lower()
    return any(k in q for k in visual_keywords)


# -----------------------------------------
# MAIN FETCH NODE
# -----------------------------------------
def fetch_node(state: FinanceState) -> Dict[str, Any]:
    """
    Node 1/4 - Extracts intent, detects asset, fetches mock data,
    and detects whether the user wants a visual output.
    """
    query = state.get("query", "")

    # -------- Detect Asset Intent --------
    asset_mode = None
    q = query.lower()

    if "btc" in q or "bitcoin" in q:
        asset_mode = "btc"
    if "eth" in q or "ethereum" in q:
        if asset_mode == "btc" or "compare" in q:
            asset_mode = "compare"
        else:
            asset_mode = "eth"

    # -------- Detect Visual Intent --------
    visual_flag = detect_visual_intent(query)

    print("\n--- Node: 1/4 - FETCH_DATA (Intent & Mock Fetch) ---")
    print(f"-> Query: '{query}' | Extracted Asset Mode: '{asset_mode}' | Visual Flag: {visual_flag}")
    time.sleep(0.4)

    # -------- Update State --------
    new_state = {
        "asset": asset_mode,
        "visual_requested": visual_flag
    }

    # -------- Fetch Mock Data --------
    if asset_mode == "compare":
        new_state["raw_data"] = {
            "btc": MOCK_PRICES["btc"],
            "eth": MOCK_PRICES["eth"]
        }

    elif asset_mode in MOCK_PRICES:
        new_state["raw_data"] = {asset_mode: MOCK_PRICES[asset_mode]}

    else:
        # Simple conceptual question → no data needed
        new_state["raw_data"] = None

    return new_state
