import time
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. State Definition
class AgentState(TypedDict):
    user_input: str
    memory_bank: list[str]

# 2. Memory Node
def memory_manager(state: AgentState):
    print("\033[95m[SYSTEM]\033[0m Scanning persistent checkpointer...")
    time.sleep(1)
    
    if "my name" in state["user_input"].lower():
        retrieved_data = state["memory_bank"][-1] if state["memory_bank"] else "UNKNOWN"
        print(f"\033[92m[MEMORY HIT]\033[0m Found context: '{retrieved_data}'")
        return state
    else:
        print("\033[93m[MEMORY WRITE]\033[0m Saving to persistent storage.")
        return {"user_input": state["user_input"], "memory_bank": state["memory_bank"] + ["Gopesh"]}

# 3. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("memory_manager", memory_manager)
workflow.set_entry_point("memory_manager")
workflow.add_edge("memory_manager", END)
app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[96m--- SIMULATING PERSISTENT THREADS ---\033[0m\n")
    app.invoke({"user_input": "Hi, I am Gopesh.", "memory_bank": []})
    time.sleep(1)
    app.invoke({"user_input": "What is my name?", "memory_bank": ["Gopesh"]})
