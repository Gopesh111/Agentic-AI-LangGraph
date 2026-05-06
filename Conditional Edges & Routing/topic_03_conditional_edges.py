import time
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# 1. Define the State Memory
# Tracking the draft content, its approval status, and how many times we revised it.
class AgentState(TypedDict):
    draft: str
    status: str
    revisions: int

# 2. Worker Node 1: The Writer
# This node simulates an LLM writing code or text.
def writer_node(state: AgentState):
    print(f"\033[94m[NODE: Writer]\033[0m Drafting content... (Current Revisions: {state['revisions']})")
    time.sleep(1.2)
    
    # Update the draft and increment the revision counter
    return {
        "draft": f"System Architecture V{state['revisions'] + 1}", 
        "revisions": state['revisions'] + 1
    }

# 3. Worker Node 2: The Reviewer
# This node simulates an evaluation step.
def reviewer_node(state: AgentState):
    print("\033[93m[NODE: Reviewer]\033[0m Analyzing draft quality...")
    time.sleep(1.5)
    
    # Simulate logic: Reject the first draft, approve the second.
    if state['revisions'] < 2:
        print("\033[91m[ALERT]\033[0m Quality Failed. Flagged for revision.")
        return {"status": "rejected"}
    else:
        print("\033[92m[SUCCESS]\033[0m Quality Passed. Ready for deployment.")
        return {"status": "approved"}

# 4. The Brain: Conditional Router
# This function decides where the graph goes next based on the state.
def router_logic(state: AgentState) -> Literal["writer_node", "__end__"]:
    if state["status"] == "rejected":
        return "writer_node" # Loop back to the writer
    return "__end__"         # Exit the graph

# 5. Build and Compile the Graph
workflow = StateGraph(AgentState)

# Add both nodes
workflow.add_node("writer_node", writer_node)
workflow.add_node("reviewer_node", reviewer_node)

# Set the standard linear flow from entry to writer, then to reviewer
workflow.set_entry_point("writer_node")
workflow.add_edge("writer_node", "reviewer_node")

# Add the conditional magic: After Reviewer, use 'router_logic' to decide the next step
workflow.add_conditional_edges("reviewer_node", router_logic)

# Compile
app = workflow.compile()

# 6. Execute the Graph
if __name__ == "__main__":
    print("\n\033[95m--- STARTING CONDITIONAL GRAPH LOOP ---\033[0m\n")
    
    # Provide the initial blank state
    app.invoke({"draft": "", "status": "pending", "revisions": 0})
    
    print("\n\033[95m--- PROCESS COMPLETED ---\033[0m")
