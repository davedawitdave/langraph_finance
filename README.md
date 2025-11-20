# **Finance-LLM LangGraph Workflow**

## **Project Overview**

This project implements a stateful, modular financial analytics engine built using **LangGraph** for workflow orchestration and the **Gemini API** for intent detection, grounding, and final synthesis.  
Its purpose is to take complex financial or crypto-related user queries and intelligently route them through multiple computational stages—data loading, statistical analysis, visualization generation—before producing a grounded, high-quality academic or investment-focused answer.

---

## **Objectives**

- **Dynamic Routing:** Execute different workflow paths depending on query intent (simple, asset-specific, comparison, visual).
- **Statistical Analysis:** Use mock BTC/ETH data to compute volatility, average price, and price ranges.
- **Visualization Descriptions:** Generate mock chart artifacts and textual summaries for LLM-assisted reasoning.
- **Gemini-Optimized Synthesis:** Feed clean, structured artifacts (stats, visuals, system prompts) into `gemini-2.5-flash-preview-09-2025` for accurate final outputs.

---

## **Tasks**

### **Task 1 – Intent Detection & Mock Data Loading (Node 1)**  
**File:** `fetch_data.py`

- **Intent Extraction:** Classify query as  
  *Simple*, *Single Asset*, *Comparison*, or *Visual Request*.  
- **Asset Identification:** Detect crypto assets mentioned (BTC, ETH, both).  
- **Mock Data Loading:** Load pre-generated price data into the shared LangGraph state.

---

### **Task 2 – Statistical Transformation (Node 2)**  
**File:** `transform.py`

- Compute:
  - Average price  
  - Min & max price  
  - Volatility percentage (`std / mean * 100`)  
- Store the computed metrics in the LangGraph state for downstream processing.

---

### **Task 3 – Visualization Artifact Generation (Node 3)**  
**File:** `visualize.py`

- Produce a **mock base64 chart** for single-asset or comparison queries.
- Create a **text description** of the visual artifact to help the LLM reason over it during final synthesis.

---

### **Task 4 – Final LLM Synthesis (Node 4)**  
**File:** `model.py`

- **Simple queries:** answer using Gemini + optional Google Search grounding.
- **Asset analysis or comparison:** integrate:
  - Statistical metrics  
  - Visual descriptions  
  - System prompt  
- Output a clean, academic, or investor-oriented final response.

---
## 2. Intelligent Routing Breakdown

| Query Type             | Example                          | Workflow Path                                  |
| ---------------------- | -------------------------------- | ---------------------------------------------- |
| **Simple Question**    | "Explain crypto volatility"      | fetch_data → model_api                         |
| **Single Asset Query** | "Analyze BTC last week"          | fetch_data → transform → model_api             |
| **Comparison Query**   | "Compare BTC and ETH volatility" | fetch_data → transform → visualize → model_api |
| **Visual Request**     | "Show me a visual of BTC risk"   | fetch_data → visualize → model_api             |

src/
 ├─ memory/
 │    └─ state.py                # Shared LangGraph state model (FinanceState)
 │
 ├─ nodes/
 │    ├─ fetch_data.py           # Task 1: Intent Detection
 │    ├─ transform.py            # Task 2: Statistical Calculation
 │    └─ visualize.py            # Task 3: Visual Artifact Description
 │
 ├─ graph/
 │    ├─ model.py                # Task 4: Final LLM Synthesis
 │    └─ graph_definition.py     # Routers + workflow builder
 │
notebooks/
 └─ finance_workflow.ipynb       # Minimal usage interface


## **Methods and Routing Logic**

### **1. LangGraph Flow Diagram**

```mermaid
flowchart TD

    A[fetch_data] --> B{Router 1<br>Asset Detected?}

    B -- No --> M[model_api]

    B -- Yes --> T[transform]

    T --> C{Router 2<br>Compare or Visual Request?}

    C -- Yes --> V[visualize]
    C -- No --> M[model_api]

    V --> M

    M --> E((END))


