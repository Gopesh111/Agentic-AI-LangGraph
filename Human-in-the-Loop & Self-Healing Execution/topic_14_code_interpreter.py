import os
import re
import subprocess
from typing import TypedDict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# Define the state for the LangGraph execution loop
class AgentState(TypedDict):
    task: str
    code: str
    error: Optional[str]
    iteration: int
    approval: str

def write_code(state: AgentState):
    """
    Node 1: The AI Coder.
    Generates initial Python code or fixes existing code based on traceback logs.
    """
    print(f"\n[AGENT] Iteration {state['iteration'] + 1}: Thinking...")
    
    # Initialize LLM. Make sure OPENAI_API_KEY is set in your environment variables.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Dynamic prompting based on current state
    if state["iteration"] == 0:
        prompt = f"Write a Python script to solve this: {state['task']}. Return ONLY code inside ```python ``` blocks."
    else:
        prompt = f"The code failed with this error:\n{state['error']}\n\nFix it and return ONLY the corrected code inside ```python ``` blocks."
        
    messages = [
        SystemMessage(content="You are an autonomous Python developer. You write clean, bug-free code."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages).content
    
    # Regex to extract pure Python code from LLM's markdown output
    code_match = re.search(r"```python(.*?)```", response, re.DOTALL)
    clean_code = code_match.group(1).strip() if code_match else response.strip()
    
    return {"code": clean_code, "iteration": state["iteration"] + 1}

def human_approval(state: AgentState):
    """
    Node 2: The Safety Check (Human-in-the-Loop).
    Pauses execution to allow a human to review the AI-generated code.
    """
    print("\n[SAFETY CHECK] Code generated. Review before execution:")
    print("-" * 30)
    print(state["code"])
    print("-" * 30)
    
    # Wait for user input in the terminal
    choice = input("Allow Sandbox execution? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("[DENIED] Execution blocked by user.")
        return {"approval": "denied"}
        
    print("[APPROVED] Execution approved.")
    return {"approval": "granted"}

def execute_code(state: AgentState):
    """
    Node 3: The Sandbox.
    Saves the code to a temporary file and runs it in an isolated subprocess.
    """
    print("\n[SANDBOX] Executing code...")
    temp_file = "workspace_script.py"
    
    # Write the AI code to a physical file
    with open(temp_file, "w") as f:
        f.write(state["code"])
        
    try:
        # Run the script with a 10-second timeout to prevent infinite loops (like while True)
        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        print(f"[SUCCESS] Output:\n{result.stdout.strip()}")
        return {"error": None}
        
    except subprocess.CalledProcessError as e:
        # If the code crashes, capture the error traceback
        print(f"[CRASH] Sending logs back to agent:\n{e.stderr.strip()}")
        return {"error": e.stderr}
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] Script took too long. Force killed.")
        return {"error": "Execution timed out after 10 seconds."}

def route_human(state: AgentState):
    """Router: Halts the graph if the human denies execution."""
    if state.get("approval") == "denied":
        return END
    return "execute_code"

def route_execution(state: AgentState):
    """Router: Checks for success or triggers the circuit breaker on max retries."""
    if state.get("error") is None:
        return END
    
    # Circuit Breaker: Prevent infinite API billing loops
    if state["iteration"] >= 3:
        print("\n[CIRCUIT BREAKER] Max retries reached. Stopping loop.")
        return END
        
    return "write_code"

# --- Graph Compilation ---
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("write_code", write_code)
workflow.add_node("human_approval", human_approval)
workflow.add_node("execute_code", execute_code)

# Define the flow
workflow.set_entry_point("write_code")
workflow.add_edge("write_code", "human_approval")
workflow.add_conditional_edges("human_approval", route_human)
workflow.add_conditional_edges("execute_code", route_execution)

# Compile into a runnable app
app = workflow.compile()

if __name__ == "__main__":
    print("[SYSTEM] Starting Local Agent Workflow...")
    
    # Example task for the agent
    task_desc = "Fetch a random user from https://jsonplaceholder.typicode.com/users and print their name and email."
    
    app.invoke({
        "task": task_desc,
        "code": "",
        "error": None,
        "iteration": 0,
        "approval": "pending"
    })
