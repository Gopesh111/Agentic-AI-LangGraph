import time
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

# 1. State Memory
# Holds the user query, the tool selected by the agent, and the result from the tool.
class AgentState(TypedDict):
    query: str
    tool_name: str
    tool_output: str

# 2. Node: The Brain (Decision Maker)
# Analyzes the query and decides if external computation or tools are needed.
def agent_brain(state: AgentState):
    print(f"\033[94m[AGENT BRAIN]\033[0m Analyzing query: '{state['query']}'")
    time.sleep(1)
    
    # Logic to detect if a math tool is required
    if "calculate" in state['query'].lower() or "power" in state['query'].lower():
        print("\033[93m[ROUTING]\033[0m Math operation detected. Forwarding to Calculator Tool.")
        return {"tool_name": "calculator"}
    else:
        print("\033[92m[ROUTING]\033[0m General query. Answering directly from internal knowledge.")
        return {"tool_name": "none"}

# 3. Node: Tool Execution
# Simulates an external API or calculator taking over the execution.
def calculator_tool(state: AgentState):
    print("\033[96m[TOOL EXECUTION]\033[0m Booting up Math Engine...")
    time.sleep(1.5)
    
    # Simulating backend calculation
    result = "1048576 (Computed via Tool API)"
    print(f"\033[92m[TOOL SUCCESS]\033[0m Output generated: {result}")
    
    return {"tool_output": result}

# 4. Conditional Router Logic
# Directs the graph flow based on the brain's decision.
def tool_router(state: AgentState) -> Literal["calculator_tool", "__end__"]:
    if state["tool_name"] == "calculator":
        return "calculator_tool"
    return "__end__"

# 5. Build Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent_brain", agent_brain)
workflow.add_node("calculator_tool", calculator_tool)

# Set the start of the graph
workflow.set_entry_point("agent_brain")

# The brain decides where to go next using the conditional router
workflow.add_conditional_edges("agent_brain", tool_router)

# After the tool finishes its execution, the flow ends
# (In a more advanced setup, this would loop back to the brain to formulate a final answer)
workflow.add_edge("calculator_tool", END)

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[95m--- STARTING TOOL INTEGRATION GRAPH ---\033[0m\n")
    
    # Test case that forces the agent to use the tool
    test_query = "Calculate the precise value of 4 raised to the power of 10."
    app.invoke({
        "query": test_query, 
        "tool_name": "", 
        "tool_output": ""
    })
    
    print("\n\033[95m--- PROCESS COMPLETED ---\033[0m")
