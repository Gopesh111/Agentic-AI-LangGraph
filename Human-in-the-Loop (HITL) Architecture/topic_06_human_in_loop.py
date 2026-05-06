import time
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# 1. State Memory
class AgentState(TypedDict):
    task: str
    human_approved: bool
    status: str

# 2. Node: Task Preparation
def prepare_task(state: AgentState):
    print("\033[94m[AGENT]\033[0m Drafting email to client...")
    time.sleep(1)
    print("\033[93m[ROUTER]\033[0m External action required. Requesting manual review.")
    return {"status": "needs_review"}

# 3. Node: Manual Review Simulation
# In a real app, this would use LangGraph's native 'interrupt' with checkpointers.
def human_node(state: AgentState):
    print("\n\033[91m[SYSTEM INTERRUPT]\033[0m Graph paused.")
    # We simulate a human saying 'yes'
    approval = True 
    print(f"\033[93m[HUMAN INPUT]\033[0m Approved: {approval}")
    return {"human_approved": approval, "status": "reviewed"}

# 4. Node: Final Execution
def execute_node(state: AgentState):
    if state["human_approved"]:
        print("\033[92m[ACTION]\033[0m Firing email API. Done.")
    else:
        print("\033[91m[ACTION]\033[0m Aborted by user.")
    return state

# 5. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("prepare_task", prepare_task)
workflow.add_node("human_node", human_node)
workflow.add_node("execute_node", execute_node)

workflow.set_entry_point("prepare_task")
workflow.add_edge("prepare_task", "human_node")
workflow.add_edge("human_node", "execute_node")
workflow.add_edge("execute_node", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[96m--- STARTING HITL WORKFLOW ---\033[0m\n")
    app.invoke({"task": "Send Client Update", "human_approved": False, "status": ""})
