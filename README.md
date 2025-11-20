# **Finance-LLM LangGraph Workflow**

## **Project Overview**

This project implements a stateful, modular financial analytics engine built using **LangGraph** for workflow orchestration and the **Gemini API** for intent detection, grounding, and final synthesis.

Its purpose is to take complex financial or crypto-related user queries and intelligently route them through multiple computational stages—data loading, statistical analysis, visualization generation—before producing a grounded, high-quality academic or investment-focused answer.

---

## **Objectives**

### **1. Dynamic Routing**
Execute different workflow paths depending on query intent:
- `simple`
- `single_asset`
- `compare`
- `visual_request`

### **2. Statistical Analysis**
Use mock BTC/ETH data to compute:
- Volatility  
- Average price  
- Price ranges  

### **3. Visualization Artifacts**
Generate:
- Mock chart artifacts (Base64 strings)  
- Text summaries to support LLM reasoning  

### **4. Gemini-Optimized Synthesis**
Feed structured artifacts into **gemini-2.5-flash-preview-09-2025** for accurate final outputs.

---

## **Tasks**

### **Task 1 – Intent Detection, Asset Mode, & Mock Data Loading (`fetch_data.py`)**

**Intent/Mode Detection**
- Classify the query and set `asset_mode` to:
  - `simple`
  - `single_asset`
  - `compare`
  - `visual_request`

**Asset Identification**
- Detect crypto assets (BTC, ETH).

**Mock Data Loading**
- Load pre-generated price data into shared LangGraph state.

---

### **Task 2 – Statistical Transformation (`transform.py`)**

Perform computations using the loaded data:
- Average price  
- Min & max price  
- Volatility (`std / mean * 100`)

Store results in the shared state under `stats`.

---

### **Task 3 – Visualization Artifact Generation (`visualize.py`)**

**Base64 Chart Generation**
- Produce mock Base64 charts for single-asset or comparison queries.

**Textual Description**
- Create a detailed explanation of the visual to help the LLM during final reasoning.

Artifacts stored:
- `chart_base64`
- `chart_description`

---

### **Task 4 – Final LLM Synthesis (`model.py`)**

**Simple Queries**
- Answer using Gemini + optional Google Search grounding.

**Asset Analysis & Comparison**
Integrate:
- Statistical metrics  
- Visual descriptions  
- Base64 charts  
- Academic/investor system prompt  

Output written to:
- `final_answer`

---
# ** src/
 ├─ memory/
 │   └─ state.py              # Shared LangGraph state model (FinanceState)
 │
 ├─ nodes/
 │   ├─ fetch_data.py         # Task 1: Intent Detection (Sets asset_mode)
 │   ├─ transform.py          # Task 2: Statistical Calculation
 │   └─ visualize.py          # Task 3: Visual Artifact Description & Chart Generation
 │
 ├─ graph/
 │   ├─ model.py              # Task 4: Final LLM Synthesis
 │   └─ graph_definition.py   # Routers + workflow builder (Defines the Graph)
 │
notebooks/
 └─ finance_workflow.ipynb    # Minimal usage interface


# **2. Intelligent Routing Breakdown**

Routing uses two routers that depend on `asset_mode` determined in `fetch_data`.

| **Asset Mode**   | **Example Query**                   | **Workflow Path**                                      |
|------------------|--------------------------------------|---------------------------------------------------------|
| `simple`         | “Explain crypto volatility”          | fetch_data → model_api                                 |
| `single_asset`   | “Analyze BTC last week”              | fetch_data → transform → model_api                     |
| `compare`        | “Compare BTC and ETH volatility”     | fetch_data → transform → visualize → model_api         |
| `visual_request` | “Show me a visual of BTC risk”       | fetch_data → visualize → model_api                     |

---

# **1. LangGraph Flow Diagram**

```mermaid
flowchart TD

    A[fetch_data] --> B{Router 1<br>Asset Mode?};

    B -- simple --> M[model_api];
    B -- single_asset --> T[transform];
    B -- visual_request --> V[visualize];
    B -- compare --> T;

    T --> C{Router 2<br>Compare Mode?};

    C -- compare --> V;
    C -- single_asset --> M;

    V --> M;

    M --> E((END));
