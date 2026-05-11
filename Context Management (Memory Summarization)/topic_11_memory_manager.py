from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import time

# 1. State Memory
class AgentState(TypedDict):
    chat_history: List[str]
    summary: str
    latest_query: str

# 2. Summarizer Node
def summarize_memory(state: AgentState):
    print("\033[95m[SUMMARIZER]\033[0m Compressing old messages...")
    time.sleep(1)
    
    # Fake summarization logic for example
    new_summary = "User was asking about Python loops and functions."
    
    # Keep only the last 2 messages, drop the rest
    trimmed_history = state["chat_history"][-2:]
    
    return {"summary": new_summary, "chat_history": trimmed_history}

# 3. Agent Node
def generate_response(state: AgentState):
    print("\033[94m[AGENT]\033[0m Generating response using summary and recent messages.")
    time.sleep(1)
    return state

# 4. Routing Logic
def check_memory_limit(state: AgentState):
    # If history is getting too long, summarize it first
    if len(state["chat_history"]) > 5:
        print("\033[93m[TRACKER]\033[0m Memory limit exceeded. Routing to Summarizer.")
        return "summarizer"
    
    print("\033[92m[TRACKER]\033[0m Memory under limit. Routing directly to Agent.")
    return "agent"

# 5. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("summarizer", summarize_memory)
workflow.add_node("agent", generate_response)

workflow.set_entry_point("agent") # Start by checking route

# Add conditional edge from START
workflow.set_conditional_entry_point(
    check_memory_limit,
    {
        "summarizer": "summarizer",
        "agent": "agent"
    }
)

# After summarizing, go to agent
workflow.add_edge("summarizer", "agent")
workflow.add_edge("agent", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n\033[1;96m--- STARTING MEMORY MANAGER GRAPH ---\033[0m\n")
    
    # Simulating a bloated state
    app.invoke({
        "chat_history": ["msg1", "msg2", "msg3", "msg4", "msg5", "msg6", "msg7"],
        "summary": "",
        "latest_query": "How do I write a while loop?"
    })
