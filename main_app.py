import sys
import os
sys.path.append(os.path.abspath(os.getcwd()))

from src.graph.graph_defination import create_finance_graph
from IPython.display import display, Markdown

app = create_finance_graph()

def run_query(q):
    print(f"Running: {q}")
    res = app.invoke({"query": q})
    if res.get("final_answer"):
        display(Markdown(res["final_answer"]))

if __name__ == "__main__":
    # Run the comparison prompt to see the graph
    run_query("Compare BTC and ETH volatility")