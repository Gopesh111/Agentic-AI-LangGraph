import time
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. State Memory
class AgentState(TypedDict):
    data: str
    draft: str
    status: str

# 2. Node 1: Fetch Data
def fetch_node(state: AgentState):
    print("\033[94m[FETCH NODE]\033[0m Getting correct data: 500.")
    return {"data": "500", "status": "fetched"}

# 3. Node 2: Draft (Simulating a mistake)
def draft_node(state: AgentState):
    print("\033[93m[DRAFT NODE]\033[0m Making a mistake in draft...")
    # Oops, agent wrote 5000 instead of 500
    return {"draft": "Revenue is 5000.", "status": "drafted"}

# 4. Node 3: Final Output
def send_node(state: AgentState):
    print(f"\033[92m[SEND NODE]\033[0m Final output sent: '{state['draft']}'")
    return {"status": "sent"}

# 5. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("fetch_node", fetch_node)
workflow.add_node("draft_node", draft_node)
workflow.add_node("send_node", send_node)

workflow.set_entry_point("fetch_node")
workflow.add_edge("fetch_node", "draft_node")
workflow.add_edge("draft_node", "send_node")
workflow.add_edge("send_node", END)

app = workflow.compile()

# NOTE FOR GITHUB: 
# In a real setup, you pass a 'checkpointer' to compile().
# Then you use app.get_state(config) to fetch the past draft, 
# app.update_state(config, {"draft": "Revenue is 500."}) to fix it,
# and app.invoke(None, config) to resume from the updated state.
