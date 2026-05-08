import time
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# 1. State Memory
class MultiAgentState(TypedDict):
    objective: str
    next_step: str
    data_collected: bool
    code_written: bool

# 2. Supervisor Node
def supervisor(state: MultiAgentState):
    print("\033[96m[SUPERVISOR]\033[0m Reviewing state...")
    time.sleep(1)
    
    if not state.get("data_collected"):
        print("\033[96m[SUPERVISOR]\033[0m Routing to Researcher.")
        return {"next_step": "researcher"}
    elif not state.get("code_written"):
        print("\033[96m[SUPERVISOR]\033[0m Routing to Developer.")
        return {"next_step": "developer"}
    else:
        print("\033[96m[SUPERVISOR]\033[0m Workflow complete.")
        return {"next_step": "finish"}

# 3. Sub-Agents
def researcher(state: MultiAgentState):
    print("\033[93m[RESEARCHER]\033[0m Fetching requirements...")
    time.sleep(1)
    return {"data_collected": True}

def developer(state: MultiAgentState):
    print("\033[92m[DEVELOPER]\033[0m Writing code blocks...")
    time.sleep(1)
    return {"code_written": True}

# 4. Router Logic
def assign_task(state: MultiAgentState) -> Literal["researcher", "developer", "__end__"]:
    if state["next_step"] == "researcher":
        return "researcher"
    elif state["next_step"] == "developer":
        return "developer"
    return "__end__"

# 5. Build Graph
workflow = StateGraph(MultiAgentState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("developer", developer)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges("supervisor", assign_task)
workflow.add_edge("researcher", "supervisor")
workflow.add_edge("developer", "supervisor")

app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[95m--- MULTI-AGENT EXECUTION ---\033[0m\n")
    app.invoke({
        "objective": "Setup server", 
        "next_step": "", 
        "data_collected": False, 
        "code_written": False
    })
