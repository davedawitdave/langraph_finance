import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from typing import Dict, Any
from ..memory.state import FinanceState

def visualize_prices(state: FinanceState) -> Dict[str, Any]:
    """
    Generates a Matplotlib chart and returns the Base64 string in 'visual'.
    """
    print("\n--- Node: 3/4 - VISUALIZE ---")
    
    raw_data = state.get("raw_data", {})
    btc_data = raw_data.get("btc", [])
    eth_data = raw_data.get("eth", [])

    if not btc_data or not eth_data:
        return {"visual": ""}

    # Data Preparation
    df_btc = pd.DataFrame(btc_data)
    df_eth = pd.DataFrame(eth_data)

    # Normalize to % change for comparison
    df_btc['norm'] = (df_btc['price'] - df_btc['price'].iloc[0]) / df_btc['price'].iloc[0] * 100
    df_eth['norm'] = (df_eth['price'] - df_eth['price'].iloc[0]) / df_eth['price'].iloc[0] * 100

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df_btc['date'], df_btc['norm'], label='BTC', color='#F7931A', linewidth=2)
    plt.plot(df_eth['date'], df_eth['norm'], label='ETH', color='#627EEA', linewidth=2)
    
    plt.title("7-Day Relative Performance (Normalized %)")
    plt.ylabel("Change (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Encode to Base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    print("-> Chart generated and encoded.")
    return {"visual": img_str}