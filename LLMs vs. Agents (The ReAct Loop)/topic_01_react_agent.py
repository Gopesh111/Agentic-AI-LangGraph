import time
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 1. Define the State (The shared memory of the graph)
# This dictionary will be passed around and updated by every node in the graph.
class AgentState(TypedDict):
    task: str
    processed_count: int

# 2. Define a Worker Node
# A node is just a python function that takes the current state, does some work,
# and returns an updated state.
def worker_node(state: AgentState):
    print("\033[94m[NODE EXECUTION]\033[0m Entering Worker Node...")
    time.sleep(1) # Simulating processing time
    
    print(f"\033[92m[STATE LOG]\033[0m Current task: {state['task']}")
    print(f"\033[92m[STATE LOG]\033[0m Current count: {state['processed_count']}")
    
    # Update the state values
    new_task = state["task"] + " -> [DONE]"
    new_count = state["processed_count"] + 1
    
    print("\033[94m[SYSTEM]\033[0m Updating Global State Graph...")
    time.sleep(1)
    
    # Return the dictionary with updated values
    return {"task": new_task, "processed_count": new_count}

# 3. Build and Compile the Graph
workflow = StateGraph(AgentState)

# Add our worker node to the workflow
workflow.add_node("worker", worker_node)

# Define the flow (Entry -> Worker -> End)
workflow.set_entry_point("worker")
workflow.add_edge("worker", END)

# Compile the graph into an executable application
app = workflow.compile()

# 4. Execute the Graph
if __name__ == "__main__":
    print("\n\033[95m--- INITIALIZING LANGGRAPH STATE MACHINE ---\033[0m")
    
    # We pass the initial state to start the process
    initial_input = {"task": "Init_System_V2", "processed_count": 0}
    result = app.invoke(initial_input)
    
    print("\n\033[95m--- FINAL GRAPH STATE ---\033[0m")
    print(f"Result: {result}")
