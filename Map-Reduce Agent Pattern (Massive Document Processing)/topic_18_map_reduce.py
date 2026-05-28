import operator
import time
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

# Ensure your API key is set
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# --- 1. Define the States ---
# Overall graph state
class MapReduceState(TypedDict):
    document: str
    chunks: list[str]
    # operator.add ensures that parallel worker outputs are appended to this list
    worker_summaries: Annotated[list[str], operator.add] 
    final_report: str

# State for individual parallel workers
class WorkerState(TypedDict):
    chunk: str
    worker_id: int

# --- 2. Define the Nodes ---
def chunking_node(state: MapReduceState):
    print("\n\033[93m[CHUNKER] Splitting document into processing chunks...\033[0m")
    time.sleep(1)
    # Simulating a split of a massive document into 5 chunks for demonstration
    # In production, use LangChain's RecursiveCharacterTextSplitter
    chunks = [
        "Log chunk 1: Normal traffic. No issues.",
        "Log chunk 2: Failed login attempt from IP 192.168.1.50.",
        "Log chunk 3: Normal database query execution.",
        "Log chunk 4: Suspicious privilege escalation attempt detected.",
        "Log chunk 5: Routine backup completed successfully."
    ]
    return {"chunks": chunks}

# The Map Edge: This dynamically spawns a worker node for each chunk
def map_to_workers(state: MapReduceState):
    print("\n\033[92m--- MAP PHASE | PARALLEL WORKERS ---\033[0m\n")
    time.sleep(0.5)
    
    # LangGraph's 'Send' API routes specific data to parallel nodes
    return [
        Send("worker_node", {"chunk": chunk, "worker_id": i + 1}) 
        for i, chunk in enumerate(state["chunks"])
    ]

def worker_node(state: WorkerState):
    worker_id = state["worker_id"]
    chunk_data = state["chunk"]
    
    print(f"\033[94m[WORKER] Worker-0{worker_id} scanning chunk for anomalies...\033[0m")
    time.sleep(0.5) # Simulating API latency
    
    # In a real app, you would call your LLM here to analyze 'chunk_data'
    # llm = ChatOpenAI(model="gpt-3.5-turbo")
    # response = llm.invoke(f"Extract anomalies from this log: {chunk_data}")
    # summary = response.content
    
    # Simulating LLM extraction to save tokens for the demo
    summary = f"Summary from worker {worker_id}: {chunk_data}"
    
    # Return as a list so operator.add can append it to 'worker_summaries'
    return {"worker_summaries": [summary]}

def master_node(state: MapReduceState):
    print("\n\033[92m[SYSTEM] All worker nodes completed successfully.\033[0m")
    print("\n\033[95m--- REDUCE PHASE | FINAL SYNTHESIS ---\033[0m\n")
    time.sleep(1)
    
    print("\033[95m[MASTER] Aggregating summaries from worker nodes...\033[0m")
    print("\033[95m[MASTER] Generating consolidated threat analysis report...\033[0m")
    
    all_summaries = "\n".join(state["worker_summaries"])
    
    # Real LLM call for the final reduce step
    # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # prompt = f"Synthesize these log summaries into a final security report:\n{all_summaries}"
    # final_report = llm.invoke(prompt).content
    
    time.sleep(1.5)
    # Mocked final report based on our simulated chunks
    final_report = (
        "• 1 suspicious login attempt identified (IP 192.168.1.50)\n"
        "• 1 privilege escalation attempt flagged\n"
        "• Consolidated security report generated successfully."
    )
    
    return {"final_report": final_report}

# --- 3. Build the Graph ---
workflow = StateGraph(MapReduceState)

workflow.add_node("chunker", chunking_node)
workflow.add_node("worker_node", worker_node)
workflow.add_node("master_node", master_node)

workflow.add_edge(START, "chunker")
# The chunker node conditionally maps to multiple worker nodes
workflow.add_conditional_edges("chunker", map_to_workers, ["worker_node"])
# All worker nodes funnel back to the master node (Fan-in)
workflow.add_edge("worker_node", "master_node")
workflow.add_edge("master_node", END)

app = workflow.compile()

# --- 4. Execution & Testing ---
if __name__ == "__main__":
    print("\nMAP-REDUCE WORKFLOW | LANGGRAPH DEMO\n")
    print("\033[96mUser Query:\nAnalyze this 48,201-line server log file for suspicious activity.\033[0m\n")
    
    print("\033[90m[SYSTEM] Ingested file: production_logs_Q3.txt (48,201 lines)\033[0m")
    
    # Initialize state with the massive document
    initial_state = {
        "document": "MASSIVE_LOG_FILE_CONTENT",
        "worker_summaries": []
    }
    
    result = app.invoke(initial_state)
    
    print("\n\033[92m--- FINAL OUTPUT ---\033[0m\n")
    print(result["final_report"])
    print("\n")
