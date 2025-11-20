import json
import requests
import time
from typing import Dict, Any, TypedDict, Optional


# ------------------------------------------------------------------------------
# 0. Finance State Type (minimal)
# ------------------------------------------------------------------------------
class FinanceState(TypedDict, total=False):
    query: str
    asset: Optional[str]        # None | "BTC" | "ETH" | "COMPARE"
    stats: Optional[Dict[str, Any]]
    visual: str
    final_answer: str
    llm_output: str


# ------------------------------------------------------------------------------
# 1. Gemini Config
# ------------------------------------------------------------------------------
GEMINI_API_KEY = "AIzaSyDdEHNUD9XB18xWO0lqX_La1MIXgiOFB58"

# Stable 2025 model
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)


# ------------------------------------------------------------------------------
# 2. Low-Level API Caller (Fully Correct)
# ------------------------------------------------------------------------------
def _call_gemini_api(prompt: str,
                     system_instruction: str,
                     use_grounding: bool = False) -> Dict[str, Any]:
    """
    Correct v1beta API call.
    - Uses systemInstruction field (legal)
    - Uses only valid roles: 'user', 'model'
    - Supports optional grounding
    """

    # ----- Build Request Body -----
    payload = {
        "systemInstruction": {
            "role": "user",
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {"temperature": 0.2}
    }

    if use_grounding:
        payload["tools"] = [{"google_search": {}}]

    headers = {"Content-Type": "application/json"}

    # ----- Retry w/ Exponential Backoff -----
    for attempt in range(5):
        try:
            response = requests.post(
                GEMINI_API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=25
            )
            response.raise_for_status()

            data = response.json()
            cand = data.get("candidates", [{}])[0]

            # Extract model text
            text = cand.get("content", {}).get("parts", [{}])[0].get("text", "")

            # Extract grounding sources
            sources = []
            meta = cand.get("groundingMetadata")
            if use_grounding and meta:
                for a in meta.get("groundingAttributions", []):
                    w = a.get("web", {})
                    if w.get("title") and w.get("uri"):
                        sources.append({"title": w["title"], "uri": w["uri"]})

            return {"text": text, "sources": sources}

        except requests.exceptions.HTTPError:
            status = response.status_code

            if status in (429, 500, 503) and attempt < 4:
                time.sleep(2 ** attempt)
                continue

            return {"text": f"HTTP {status} Error: {response.text}", "sources": []}

        except Exception as e:
            return {"text": f"Unexpected Error: {e}", "sources": []}

    return {"text": "API failed after maximum retries.", "sources": []}


# ------------------------------------------------------------------------------
# 3. Main LangGraph Node: MODEL
# ------------------------------------------------------------------------------
def call_gemini_api(state: FinanceState) -> Dict[str, Any]:
    """
    Final step in the analysis graph.
    Produces final_answer + llm_output.
    """

    query = state.get("query")
    asset = state.get("asset")
    stats = state.get("stats")
    visual = state.get("visual", "")

    print("\n--- Node 4/4 – MODEL ---")

    # ==========================================================================
    # CASE 1 — Simple Query (no BTC/ETH selected)
    # ==========================================================================
    if asset is None:
        print("-> Simple Query Mode (using grounding)")

        api = _call_gemini_api(
            prompt=query,
            system_instruction="You explain financial topics clearly and accurately.",
            use_grounding=True
        )

        # Build answer
        sources = api["sources"]
        citation = ""
        if sources:
            citation = "\n\n---\n### Sources\n" + "\n".join(
                f"- [{s['title']}]({s['uri']})" for s in sources
            )

        final = (
            "## Simple Query Answer\n"
            f"**Query:** {query}\n\n"
            f"{api['text']}{citation}"
        )

        return {"final_answer": final, "llm_output": final}

    # ==========================================================================
    # CASE 2 — Compare Mode (BTC vs ETH)
    # ==========================================================================
    if asset == "COMPARE":
        print("-> Comparison Mode")

        try:
            btc_vol = stats["btc"]["volatility_percent"]
            eth_vol = stats["eth"]["volatility_percent"]
        except Exception:
            return {"final_answer": "Compare mode error: missing volatility data.",
                    "llm_output": "Compare mode error."}

        prompt = (
            f"Comparison data:\n"
            f"- BTC vol: {btc_vol}%\n"
            f"- ETH vol: {eth_vol}%\n\n"
            f"Chart (base64): {visual[:40]}...\n\n"
            f"Respond to: {query}"
        )

        api = _call_gemini_api(
            prompt=prompt,
            system_instruction="You are a professional quantitative analyst.",
            use_grounding=False
        )

        final = (
            "## BTC vs ETH – Expert Comparison\n\n"
            f"![Chart](data:image/png;base64,{visual})\n\n"
            f"### Analyst Summary\n{api['text']}"
        )

        return {"final_answer": final, "llm_output": final}

    # ==========================================================================
    # CASE 3 — Single Asset: BTC or ETH
    # ==========================================================================
    if asset in ("BTC", "ETH"):
        print(f"-> Single Asset Mode: {asset}")

        s = stats.get(asset.lower(), {})
        table = (
            "| Metric | Value |\n"
            "|--------|-------|\n"
            f"| Average Price | ${s.get('average_price', 0):,.2f} |\n"
            f"| Volatility | {s.get('volatility_percent', 0)}% |\n"
            f"| Range | ${s.get('min_price', 0):,.2f} → ${s.get('max_price', 0):,.2f} |\n"
        )

        prompt = (
            f"Stats for {asset}:\n{table}\n\n"
            f"Write a short expert interpretation answering: {query}"
        )

        api = _call_gemini_api(
            prompt=prompt,
            system_instruction="You are a seasoned financial analyst.",
            use_grounding=False
        )

        final = (
            f"## {asset} – Expert Analysis\n\n"
            f"![Chart](data:image/png;base64,{visual})\n\n"
            f"### Stats\n{table}\n"
            f"### Analyst Notes\n{api['text']}"
        )

        return {"final_answer": final, "llm_output": final}

    # ==========================================================================
    # FALLBACK
    # ==========================================================================
    return {
        "final_answer": "Model node reached without valid asset mode.",
        "llm_output": "Model node reached without valid asset mode."
    }
