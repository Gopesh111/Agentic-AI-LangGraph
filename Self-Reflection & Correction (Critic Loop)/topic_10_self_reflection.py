import time
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# 1. State Memory
class AgentState(TypedDict):
    draft: str
    feedback: str
    iterations: int
    is_valid: bool

# 2. Generator Node
def generator(state: AgentState):
    current_iter = state.get("iterations", 0) + 1
    print(f"\033[94m[GENERATOR]\033[0m Writing draft (Attempt {current_iter})...")
    time.sleep(1)
    
    # Simulating a bad draft on the first try, good on the second
    if current_iter == 1:
        new_draft = "def hello() print('hi')" # Intentional syntax error
    else:
        new_draft = "def hello():\n    print('hi')" # Fixed
        
    return {"draft": new_draft, "iterations": current_iter}

# 3. Critic Node
def critic(state: AgentState):
    print("\033[93m[CRITIC]\033[0m Reviewing code...")
    time.sleep(1)
    
    if ":" not in state["draft"]:
        print("\033[91m[CRITIC]\033[0m Error found: Missing colon.")
        return {"is_valid": False, "feedback": "Add a colon after the function definition."}
    else:
        print("\033[92m[CRITIC]\033[0m Code looks good.")
        return {"is_valid": True, "feedback": "None"}

# 4. Routing Logic (The Loop)
def reflection_router(state: AgentState) -> Literal["generator", "__end__"]:
    if state["is_valid"]:
        return "__end__"
    
    # Prevent infinite loops
    if state["iterations"] >= 3:
        print("\033[91m[SYSTEM]\033[0m Max iterations reached. Forcing exit.")
        return "__end__"
        
    print("\033[96m[ROUTER]\033[0m Routing back to Generator.\n")
    return "generator"

# 5. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("generator", generator)
workflow.add_node("critic", critic)

workflow.set_entry_point("generator")
workflow.add_edge("generator", "critic")

# Conditional edge creates the cycle
workflow.add_conditional_edges("critic", reflection_router)

app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[95m--- STARTING SELF-REFLECTION GRAPH ---\033[0m\n")
    app.invoke({
        "draft": "", 
        "feedback": "", 
        "iterations": 0, 
        "is_valid": False
    })
