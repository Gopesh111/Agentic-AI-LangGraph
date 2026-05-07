import time
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. State Definition
# Shared memory that collects results from parallel branches
class AgentState(TypedDict):
    query: str
    web_result: str
    db_result: str
    final_output: str

# 2. Parallel Node A: External Search
def web_search(state: AgentState):
    print("\033[94m[NODE A]\033[0m Fetching live web data...")
    time.sleep(2) # Simulating latency
    return {"web_result": "Current Market Trends"}

# 3. Parallel Node B: Internal Database
def db_query(state: AgentState):
    print("\033[93m[NODE B]\033[0m Querying SQL database...")
    time.sleep(1.5) # Simulating latency
    return {"db_result": "User Transaction History"}

# 4. Aggregator Node: Synthesis
# This node runs only after both A and B are finished
def synthesizer(state: AgentState):
    print("\n\033[95m[SYNTHESIZER]\033[0m Merging parallel data streams...")
    combined = f"Report based on {state['web_result']} and {state['db_result']}"
    print(f"\033[92m[SUCCESS]\033[0m Optimization complete. Final data: {combined}")
    return {"final_output": combined}

# 5. Build Graph with Fan-out/Fan-in
workflow = StateGraph(AgentState)

workflow.add_node("web_search", web_search)
workflow.add_node("db_query", db_query)
workflow.add_node("synthesizer", synthesizer)

# Fan-out: Starting multiple nodes from the entry point
workflow.set_entry_point("web_search")
workflow.set_entry_point("db_query")

# Fan-in: Directing parallel branches to a single join node
workflow.add_edge("web_search", "synthesizer")
workflow.add_edge("db_query", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[96m--- STARTING PARALLEL PERFORMANCE TEST ---\033[0m\n")
    start_time = time.time()
    
    app.invoke({"query": "Analyze my account", "web_result": "", "db_result": "", "final_output": ""})
    
    end_time = time.time()
    print(f"\n\033[97mTotal Execution Time: {round(end_time - start_time, 2)}s\033[0m")
