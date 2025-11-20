# src/nodes/fetch_data.py

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..memory.state import FinanceState

# CoinPaprika uses specific IDs (e.g., 'btc-bitcoin')
COIN_MAP = {
    'btc': 'btc-bitcoin',
    'eth': 'eth-ethereum',
    'sol': 'sol-solana',
    'bitcoin': 'btc-bitcoin',
    'ethereum': 'eth-ethereum',
    'solana': 'sol-solana'
}

def fetch_coinpaprika_history(coin_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Fetches historical OHLCV data from CoinPaprika for the given coin_id.
    """
    # Calculate start date (CoinPaprika expects YYYY-MM-DD or ISO format)
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}/historical"
    params = {
        "start": start_date,
        "interval": "24h"
    }
    
    print(f"   -> HTTP GET: {url} (start={start_date})")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse and format the response to our standard structure
        # CoinPaprika returns a list of dicts with 'timestamp' and 'price'
        formatted_data = []
        for entry in data:
            formatted_data.append({
                "date": entry.get("timestamp", "")[:10], # Extract YYYY-MM-DD
                "price": entry.get("price")
            })
            
        # Sort by date just in case
        formatted_data.sort(key=lambda x: x['date'])
        
        # Ensure we return exactly the requested number of days (or available amount)
        return formatted_data[-days:]
        
    except requests.exceptions.RequestException as e:
        print(f"   [Error] API Request failed for {coin_id}: {e}")
        return []

def fetch_node(state: FinanceState) -> Dict[str, Any]:
    """
    Node 1/4: Extracts asset intent and fetches REAL historical data from CoinPaprika.
    """
    query = state.get("query", "").lower()
    print(f"\n--- Node: 1/4 - FETCH_DATA (Real API) ---")
    
    # --- 1. Intent Parsing ---
    asset_mode = None
    if 'bitcoin' in query or 'btc' in query:
        asset_mode = 'btc'
    if 'ethereum' in query or 'eth' in query:
        # If 'btc' was already set, or 'compare' keyword is present, switch to compare
        if asset_mode == 'btc' or 'compare' in query or 'vs' in query:
            asset_mode = 'compare'
        else:
            asset_mode = 'eth'
            
    # Default to None if no asset found (Simple Query Path)
    if not asset_mode:
        print(f"-> Query: '{state.get('query')}'")
        print("-> Result: No specific asset identified. Routing to Simple Query path.")
        return {"asset": None, "raw_data": None}

    print(f"-> Asset Detected: {asset_mode.upper()}")

    # --- 2. Real API Fetching ---
    raw_data = {}
    
    if asset_mode == 'compare':
        # Fetch both BTC and ETH
        print("-> Status: Fetching comparison data (BTC & ETH)...")
        btc_data = fetch_coinpaprika_history(COIN_MAP['btc'])
        eth_data = fetch_coinpaprika_history(COIN_MAP['eth'])
        
        if btc_data: raw_data['btc'] = btc_data
        if eth_data: raw_data['eth'] = eth_data
        
    elif asset_mode in COIN_MAP:
        # Fetch single asset
        print(f"-> Status: Fetching data for {asset_mode.upper()}...")
        data = fetch_coinpaprika_history(COIN_MAP[asset_mode])
        if data:
            raw_data[asset_mode] = data

    # Check if we successfully got data
    if not raw_data:
        print("-> Warning: API calls failed or returned no data.")
        # Optionally handle as an error or fallback to simple query
        # For now, we return asset as is, but raw_data is empty, which transform_node should handle.
    
    return {"raw_data": raw_data, "asset": asset_mode}