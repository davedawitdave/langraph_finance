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
GEMINI_API_KEY = "AIzaSyArvYuzYtdxnN05T_gMYwuAiUvribAShdQ"

# Stable 2025 model
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)


def _call_gemini_api(prompt: str, system_instruction: str, use_grounding: bool = False) -> Dict[str, Any]:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"temperature": 0.2}
    }

    if use_grounding:
        payload["tools"] = [{"google_search": {}}]

    headers = {"Content-Type": "application/json"}

    for attempt in range(5):
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload), timeout=25)
            response.raise_for_status()
            data = response.json()
            cand = data.get("candidates", [{}])[0]
            text = cand.get("content", {}).get("parts", [{}])[0].get("text", "")
            
            sources = []
            meta = cand.get("groundingMetadata")
            if use_grounding and meta:
                for a in meta.get("groundingAttributions", []):
                    w = a.get("web", {})
                    if w.get("title") and w.get("uri"):
                        sources.append({"title": w["title"], "uri": w["uri"]})

            return {"text": text, "sources": sources}

        except Exception as e:
            time.sleep(2 ** attempt)
            continue

    return {"text": "API Failed", "sources": []}

def call_gemini_api(state: FinanceState) -> Dict[str, Any]:
    query = state.get("query")
    asset = state.get("asset")
    stats = state.get("stats")
    visual = state.get("visual", "")

    print("\n--- Node: 4/4 - MODEL ---")

    # CASE 1: Simple Query
    if asset is None:
        print("-> Simple Query Mode")
        api = _call_gemini_api(query, "You explain financial topics clearly.", use_grounding=True)
        
        citation = ""
        if api["sources"]:
            citation = "\n\n### Sources\n" + "\n".join(f"- [{s['title']}]({s['uri']})" for s in api["sources"])
            
        final = f"## Simple Query Answer\n**Query:** {query}\n\n{api['text']}{citation}"
        return {"final_answer": final, "llm_output": final}

    # CASE 2: Comparison
    if asset == "compare":
        print("-> Comparison Mode")
        try:
            btc_vol = stats["btc"]["volatility_percent"]
            eth_vol = stats["eth"]["volatility_percent"]
            prompt = f"Compare BTC (Vol: {btc_vol}%) vs ETH (Vol: {eth_vol}%). Query: {query}"
            
            api = _call_gemini_api(prompt, "You are a quantitative analyst.", use_grounding=False)
            
            # EMBEDDING THE VISUAL HERE
            final = (
                f"## BTC vs ETH Analysis\n\n"
                f"![Chart](data:image/png;base64,{visual})\n\n"
                f"### Analyst Summary\n{api['text']}"
            )
            return {"final_answer": final, "llm_output": final}
        except Exception as e:
            return {"final_answer": f"Error in comparison: {e}", "llm_output": ""}

    # CASE 3: Single Asset
    if asset in ["btc", "eth"]:
        print(f"-> Single Asset Mode: {asset}")
        s = stats.get(asset, {})
        table = f"| Metric | Value |\n|---|---|\n| Avg | ${s.get('average_price')} |\n| Volatility | {s.get('volatility_percent')}% |"
        
        prompt = f"Analyze this data for {asset}:\n{table}\nQuery: {query}"
        api = _call_gemini_api(prompt, "You are a financial analyst.", use_grounding=False)
        
        final = f"## {asset.upper()} Analysis\n\n### Stats\n{table}\n\n### Report\n{api['text']}"
        return {"final_answer": final, "llm_output": final}

    return {"final_answer": "Error", "llm_output": "Error"}