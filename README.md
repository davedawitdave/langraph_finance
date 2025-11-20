Finance-LLM LangGraph Workflow

A modular, LLM-driven financial analytics engine powered by LangGraph + Gemini.

🧩 Overview

This project implements a stateful LangGraph pipeline that processes financial and cryptocurrency queries using:

Dynamic routing

Intent extraction

BTC/ETH statistical analysis

Comparison workflows

Visualization-aware reasoning

Gemini API synthesis

A single user prompt is enough — the workflow decides whether to:

Provide a conceptual academic answer

Compute cryptocurrency statistics

Compare BTC vs ETH

Generate a visualization description

Or combine all of the above

Your notebook stays minimal, while all logic lives inside src/.

📁 Project Structure
src/
 ├─ memory/
 │    └─ state.py                # Shared LangGraph state model
 │
 ├─ nodes/
 │    ├─ fetch_data.py           # Node 1 → intent detection + mock data
 │    ├─ transform.py            # Node 2 → compute BTC/ETH stats
 │    └─ visualize.py            # Node 3 → visual artifact description
 │
 ├─ graph/
 │    ├─ model.py                # Node 4 → Gemini API caller
 │    └─ graph_definition.py     # Routers + workflow builder
 │
notebooks/
 └─ finance_workflow.ipynb       # Minimal notebook interface

⚡ Features
✔ Intelligent Routing

The system auto-detects whether the query is:

Query Type	Example	Path
Simple Question	"Explain crypto volatility"	→ LLM
Single Asset Query	"Analyze BTC last week"	→ Transform → LLM
Comparison Query	"Compare BTC & ETH volatility"	→ Transform → Visual → LLM
Visual Request	"Show me a visual of BTC risk"	→ Visual → LLM
✔ Modular Node Architecture
Node	File	Description
1. fetch_node	nodes/fetch_data.py	Intent extraction + mock data
2. transform_node	nodes/transform.py	Compute stats / percent change
3. visualize_prices	graph/visual.py	Generate chart descriptions
4. call_gemini_api	graph/model.py	Final LLM synthesis via Gemini
✔ Gemini-Optimized Prompting

The model receives:

System prompt

Query

Stats (if available)

Visualization artifacts (if available)

Then returns a clean academic answer.

🔀 Workflow Diagram
LangGraph Flow (Mermaid)
flowchart TD

    A[fetch_data] --> B{Router 1<br>Asset Detected?}

    B -- No --> M[model_api]

    B -- Yes --> T[transform]

    T --> C{Router 2<br>Compare or Visual Request?}

    C -- Yes --> V[visualize]

    C -- No --> M[model_api]

    V --> M

    M --> E((END))

📦 Installation
1. Clone repository
git clone <repo-url>
cd <repo-folder>

2. Create virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

3. Install requirements
pip install -r requirements.txt

4. Add Gemini API key

Create .env:

GEMINI_API_KEY=your_key_here

🧠 Usage (Notebook)

Your notebook stays minimal, only 2–3 lines needed per query.

Example
from src.graph.graph_definition import run_workflow

query = "What are the risks of buying BTC? Provide a visual summary."

response = run_workflow(query)
response

Another example:
queries = [
    "Explain crypto volatility in simple terms",
    "Give me BTC stats for the last 7 days",
    "Compare BTC and ETH volatility visually"
]

for q in queries:
    print(run_workflow(q))
    print("\n" + "="*80 + "\n")

🧪 Example Behaviors
User Query	Workflow Behavior
“What is crypto volatility?”	→ Simple conceptual answer
“Analyze BTC 7-day trend”	→ Transform → Gemini
“compare btc and eth volatility”	→ Transform → Visual → Gemini
“Show me a visual of BTC risks”	→ Visual → Gemini
“plot ethereum performance academically”	→ Visual → Gemini
📈 Extending the System
Add new assets

Update:

MOCK_PRICES

fetch_node intent logic

Add real APIs

Replace mock datasets with REST calls (Binance, AlphaVantage, Coinbase, Kaiko).

Add more visualization types

Modify:

src/graph/visual.py

Add sentiment analysis

Create a new node and route conditionally.

🛠 Recommended Improvements

Add unit tests for node outputs

Replace mock data with real price feeds

Add temporal indicators (SMA, EMA, RSI)

Add caching layer for API calls

Add Streamlit dashboard version

If you want, I can generate these files too.

🏁 Final Notes

This project gives you:

Professional LangGraph architecture

Clean routing

Visualization-aware LLM reasoning

Minimal notebook usage

Full modularity for research & production
