import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..memory.state import FinanceState

COIN_MAP = {
    'btc': 'btc-bitcoin',
    'eth': 'eth-ethereum',
    'bitcoin': 'btc-bitcoin',
    'ethereum': 'eth-ethereum',
}

def fetch_coinpaprika_history(coin_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Fetches historical data from CoinPaprika."""
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}/historical"
    params = {"start": start_date, "interval": "24h"}
    
    print(f"   -> HTTP GET: {url} (start={start_date})")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        formatted_data = []
        for entry in data:
            formatted_data.append({
                "date": entry.get("timestamp", "")[:10],
                "price": entry.get("price")
            })
        
        formatted_data.sort(key=lambda x: x['date'])
        return formatted_data[-days:]
    except Exception as e:
        print(f"   [Error] API Request failed for {coin_id}: {e}")
        return []

def fetch_node(state: FinanceState) -> Dict[str, Any]:
    query = state.get("query", "").lower()
    print(f"\n--- Node: 1/4 - FETCH_DATA ---")
    
    asset_mode = None
    if 'bitcoin' in query or 'btc' in query:
        asset_mode = 'btc'
    if 'ethereum' in query or 'eth' in query:
        if asset_mode == 'btc' or 'compare' in query or 'vs' in query:
            asset_mode = 'compare'
        else:
            asset_mode = 'eth'
            
    if not asset_mode:
        print("-> Result: No specific asset. Routing to Simple Query.")
        return {"asset": None, "raw_data": None}

    print(f"-> Asset Detected: {asset_mode.upper()}")

    raw_data = {}
    if asset_mode == 'compare':
        btc_data = fetch_coinpaprika_history(COIN_MAP['btc'])
        eth_data = fetch_coinpaprika_history(COIN_MAP['eth'])
        if btc_data: raw_data['btc'] = btc_data
        if eth_data: raw_data['eth'] = eth_data
        
    elif asset_mode in COIN_MAP:
        data = fetch_coinpaprika_history(COIN_MAP[asset_mode])
        if data: raw_data[asset_mode] = data
    
    return {"raw_data": raw_data, "asset": asset_mode}