import time
import base64
import io
from typing import Dict, Any
import matplotlib.pyplot as plt
from ..memory.state import FinanceState


def visualize_prices(state: FinanceState) -> Dict[str, Any]:
    """
    Node 3/4: Generates a real BTC/ETH price plot + visual description.
    """
    stats = state.get("stats")
    prices = state.get("prices")

    if not stats or "btc" not in stats or "eth" not in stats:
        print("\n--- Node: 3/4 - VISUALIZE (Skipped: missing stats) ---")
        return {}

    if not prices or "btc" not in prices or "eth" not in prices:
        print("\n--- Node: 3/4 - VISUALIZE (Skipped: missing price series) ---")
        return {}

    btc_prices = prices["btc"]
    eth_prices = prices["eth"]

    if len(btc_prices) != 7 or len(eth_prices) != 7:
        print("\n--- Node: 3/4 - VISUALIZE (Skipped: expected 7-day series) ---")
        return {}

    print("\n--- Node: 3/4 - VISUALIZE (Generating Plot) ---")
    time.sleep(0.4)

    # -----------------------------
    # 🔹 Generate Matplotlib figure
    # -----------------------------
    days = list(range(1, 8))
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(days, btc_prices, label="Bitcoin (BTC)", linewidth=2)
    ax.plot(days, eth_prices, label="Ethereum (ETH)", linewidth=2)

    ax.set_title("BTC vs ETH - 7 Day Price Comparison")
    ax.set_xlabel("Day")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Save figure → base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    encoded_image = base64.b64encode(buf.read()).decode("utf-8")

    # -----------------------------
    # 🔹 Create Natural Language description
    # -----------------------------
    btc_v = stats["btc"]["volatility_percent"]
    eth_v = stats["eth"]["volatility_percent"]

    visual_description = (
        f"A line chart comparing Bitcoin (BTC) and Ethereum (ETH) over 7 days. "
        f"BTC's volatility is {btc_v}%, and ETH's volatility is {eth_v}%. "
        f"The chart visualizes how the higher-volatility asset shows steeper changes, "
        f"confirming the statistical findings."
    )

    return {
        "visual": visual_description,
        "plot_base64": encoded_image
    }
