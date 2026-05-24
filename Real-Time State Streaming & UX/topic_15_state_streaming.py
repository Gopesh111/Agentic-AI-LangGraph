import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages

# Ensure your API key is set
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 1. Define the State
class AgentState(TypedDict):
    task: str
    messages: Annotated[list, add_messages]
    code_approved: bool

# 2. Define Nodes
def coder_node(state: AgentState):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = f"Write a secure 1-line Python print statement to solve this task: {state['task']}. Return ONLY the code."
    response = llm.invoke(prompt)
    return {"messages": [response], "code_approved": False}

def human_gate_node(state: AgentState):
    # This node acts as an explicit boundary. 
    # The graph will physically pause BEFORE entering this node due to 'interrupt_before'
    pass

def execute_node(state: AgentState):
    if not state.get("code_approved"):
        return {"messages": [AIMessage(content="[SYSTEM] Execution aborted. Human denied permission.")]}
    
    # In a real app, this would run the code in a sandbox (like topic 14)
    code_to_run = state["messages"][-1].content
    simulated_output = f"Executed successfully: {code_to_run}"
    return {"messages": [AIMessage(content=f"[SANDBOX] {simulated_output}")]}

# 3. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("coder", coder_node)
workflow.add_node("human_gate", human_gate_node)
workflow.add_node("execute", execute_node)

workflow.add_edge(START, "coder")
workflow.add_edge("coder", "human_gate")
workflow.add_edge("human_gate", "execute")
workflow.add_edge("execute", END)

# 4. Compile with Checkpointer (Crucial for time-travel and interrupts)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["human_gate"])

# --- Terminal UI and Real Streaming Execution ---
if __name__ == "__main__":
    # Terminal colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

    print(f"\n{GREEN}✅ TOPIC 15: REAL-TIME STREAMING & HUMAN INTERRUPT{RESET}\n")
    
    # Thread ID is mandatory for memory/interrupts
    config = {"configurable": {"thread_id": "user_session_001"}}
    initial_input = {"task": "Fetch database logs", "messages": []}

    print(f" ⏳ {CYAN}[Agent]{RESET} Starting workflow and generating code...")

    # PHASE 1: Stream until the interrupt (Human Gate)
    for output in app.stream(initial_input, config, stream_mode="updates"):
        for node_name, state_data in output.items():
            if node_name == "coder":
                generated_code = state_data["messages"][-1].content
                print(f" ⏳ {YELLOW}[Coder]{RESET} Drafted code: {generated_code}")

    # Check if graph is paused
    graph_state = app.get_state(config)
    if graph_state.next and graph_state.next[0] == "human_gate":
        print(f"\n 🚨 {RED}[Safety Gate]{RESET} Graph execution paused!")
        user_input = input(f" 👤 {GREEN}[Human]{RESET} Approve code execution? (y/n): ").strip().lower()
        
        if user_input == 'y':
            # Update state with human approval
            app.update_state(config, {"code_approved": True})
            print(f" ⏳ {CYAN}[System]{RESET} Approval granted. Resuming execution...")
        else:
            app.update_state(config, {"code_approved": False})
            print(f" ⏳ {RED}[System]{RESET} Approval denied. Resuming execution to safely abort...")

        # PHASE 2: Stream the rest of the graph
        for output in app.stream(None, config, stream_mode="updates"):
            for node_name, state_data in output.items():
                if node_name == "execute":
                    final_msg = state_data["messages"][-1].content
                    print(f" ⏳ {GREEN}[Execution]{RESET} {final_msg}")

    print(f"\n 🏁 {CYAN}[System]{RESET} Workflow complete.\n")
