import os
import re
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

# Ensure your API key is set before running
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# --- 1. Define the State ---
class RouterState(TypedDict):
    question: str
    route: str
    response: str

# --- 2. Deterministic Rules (Regex / Keywords) ---
GREETING_PATTERN = re.compile(r"^(hi|hello|hey|greetings)\b", re.IGNORECASE)
HELP_PATTERN = re.compile(r"^(help|support|menu)\b", re.IGNORECASE)

# --- 3. Define the Nodes ---
def fast_router_node(state: RouterState):
    """Checks if the query can be solved without an LLM."""
    query = state["question"].strip()

    print("[Router] Checking deterministic rules...")

    if GREETING_PATTERN.search(query):
        print("[Router] Match found: GREETING. Fast-pathing...")
        return {
            "route": "fast_path",
            "response": "Hello! I am ready to help you with complex tasks."
        }

    elif HELP_PATTERN.search(query):
        print("[Router] Match found: HELP. Fast-pathing...")
        return {
            "route": "fast_path",
            "response": "Sure, I can help you code, analyze data, or debug."
        }

    else:
        print("[Router] Complex query detected. Routing to Heavy LLM...")
        return {"route": "llm_path"}

def llm_reasoning_node(state: RouterState):
    """The heavy node for complex tasks."""
    print("[Heavy_LLM] Generating response via OpenAI API...")

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

    result = llm.invoke([HumanMessage(content=state["question"])])
    return {"response": result.content}

# --- 4. Conditional Routing Logic ---
def choose_execution_path(state: RouterState):
    if state["route"] == "fast_path":
        # Skip the LLM entirely
        return END
    return "llm_path"

# --- 5. Build the Graph ---
workflow = StateGraph(RouterState)

# Notice we don't even add a node for the fast path.
# The router node populates the state and the graph just ends.
workflow.add_node("router", fast_router_node)
workflow.add_node("llm_path", llm_reasoning_node)

workflow.add_edge(START, "router")

workflow.add_conditional_edges(
    "router",
    choose_execution_path,
    {
        "llm_path": "llm_path",
        END: END
    }
)

workflow.add_edge("llm_path", END)

app = workflow.compile()

# --- 6. Execution & Testing ---
if __name__ == "__main__":
    print("\nTOPIC 20: DETERMINISTIC FALLBACKS (FAST-PATHING)\n")

    test_queries = [
        "Hey there!",
        "Help me with this.",
        "Write a Python script to reverse a linked list."
    ]

    for query in test_queries:
        print(f"User: '{query}'")

        initial_state = {
            "question": query,
            "route": "",
            "response": ""
        }

        result = app.invoke(initial_state)

        print(f"System: {result['response']}")
        print("-" * 60)
