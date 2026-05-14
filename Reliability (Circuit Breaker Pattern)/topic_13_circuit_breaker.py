from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. State Definition (Adding a tracker)
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    retry_count: int 

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Nodes
def agent_node(state: AgentState):
    """The main reasoning engine."""
    return {"messages": [llm.invoke(state["messages"])]}

def faulty_tool(state: AgentState):
    """Simulates a broken API endpoint or tool failure."""
    # Increment the failure counter in the state
    count = state.get("retry_count", 0) + 1
    error_msg = HumanMessage(content="Error: Database timeout. Failed to fetch records.")
    
    return {"messages": [error_msg], "retry_count": count}

def safety_exit(state: AgentState):
    """Graceful shutdown node when things go wrong."""
    exit_message = AIMessage(content="System halted: Circuit breaker triggered after 3 failed attempts. API credits saved.")
    return {"messages": [exit_message]}

# 3. Routing Logic (The Circuit Breaker)
def check_breaker(state: AgentState):
    """Monitors the retry count and decides the next step."""
    failures = state.get("retry_count", 0)
    
    # Hard stop after 3 consecutive failures
    if failures >= 3:
        print("\n[SYSTEM] Circuit breaker triggered. Routing to safe exit.")
        return "halt"
        
    print(f"\n[SYSTEM] Tool failed. Retry attempt {failures + 1}/3")
    return "retry"

# 4. Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tool", faulty_tool)
workflow.add_node("exit", safety_exit)

workflow.add_edge(START, "agent")
workflow.add_edge("agent", "tool") # Forcing the tool call to simulate the issue

# The router acts as a gatekeeper after the tool runs
workflow.add_conditional_edges(
    "tool",
    check_breaker,
    {
        "halt": "exit",
        "retry": "agent"
    }
)

workflow.add_edge("exit", END)

# Compile the graph
app = workflow.compile()

# --- Example Execution ---
if __name__ == "__main__":
    print("Starting LangGraph execution with Circuit Breaker enabled...\n")
    
    inputs = {
        "messages": [HumanMessage(content="Fetch the user records from the database.")], 
        "retry_count": 0
    }
    
    for event in app.stream(inputs):
        for node_name, data in event.items():
            if node_name == "exit":
                print(f"\nFinal Output: {data['messages'][-1].content}")
