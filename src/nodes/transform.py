# src/nodes/transform.py

import numpy as np
import time
from typing import Dict, Any, List
from ..memory.state import FinanceState

def calculate_stats(prices: List[float], days_analyzed: int) -> Dict[str, Any]:
    """Helper to calculate average, volatility, and min/max."""
    if not prices:
        return {}
    
    prices_array = np.array(prices)
    avg_price = np.mean(prices_array)
    std_dev = np.std(prices_array)
    
    # Volatility is calculated as Standard Deviation as a percentage of the Mean
    volatility_percent = round((std_dev / avg_price) * 100, 2)
    
    return {
        "days_analyzed": days_analyzed,
        "average_price": round(avg_price, 2),
        "min_price": round(np.min(prices_array), 2),
        "max_price": round(np.max(prices_array), 2),
        "volatility_percent": volatility_percent,
    }

def transform_node(state: FinanceState) -> Dict[str, Any]:
    """
    Node 2/4: Calculates core financial statistics from the raw data.
    """
    raw_data = state.get("raw_data")
    
    if not raw_data:
        print("\n--- Node: 2/4 - TRANSFORM_NODE (Skipped) ---")
        return {} # No data to transform, should not happen for data paths
    
    print("\n--- Node: 2/4 - TRANSFORM_NODE (Calculating Statistics) ---")
    time.sleep(0.5) # Simulate latency
    
    stats: Dict[str, Any] = {}
    
    for asset, data in raw_data.items():
        prices = [d['price'] for d in data]
        days_analyzed = len(data)
        
        stats[asset] = calculate_stats(prices, days_analyzed)

    print(f"-> Stats Calculated for: {list(stats.keys())}")
    
    return {"stats": stats}