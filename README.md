LangGraph Financial/Crypto Signal Generator
=========================================

This project implements a cyclical think-act LangGraph agent that fetches live market data, computes indicators, and generates a buy/sell/hold style narrative report.

Features
- Cyclical graph: executor (think) -> tool_caller (act) -> loop_check (decide) -> executor or final_report
- Pluggable tools: live data (Coingecko), indicators (RSI, SMA) using pandas/ta
- Structured state with memory of past steps
- Deterministic router bootstrap from the goal

Quickstart
1) Create and activate a Python 3.10+ venv
   - Windows PowerShell:  
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1

2) Install deps
   pip install -r requirements.txt

3) Run
   python -m app.main --goal "Analyze BTC price for the last 24h and generate a buy/sell signal" --ticker BTC --indicator RSI --period 24

Notes
- Coingecko is used for crypto OHLC data (no API key required for basic endpoints).
- You can switch/extend data sources (e.g., Binance) by updating tools/data.py.
- For stocks, integrate a stock API and map into the same OHLC schema.
