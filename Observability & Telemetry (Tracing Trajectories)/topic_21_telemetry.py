import os
import time
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# --- 1. LangSmith Observability Configuration ---
# Setting these environment variables automatically instruments LangGraph and LangChain.
# You don't need to change your core code to get full tracing!

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "Agentic_AI_Series_T21"

# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# --- 2. Define the State ---
class TraceState(TypedDict):
    input_text: str
    context: str
    summary: str

# --- 3. Define the Nodes ---
def retrieve_node(state: TraceState):
    print(" [Retriever] Fetching context (This step is being traced)...")
    time.sleep(0.5)

    # Mocking a database fetch
    mock_db_context = "Q3 Revenue grew by 15%. Server costs decreased by 5%."

    return {"context": mock_db_context}


def synthesize_node(state: TraceState):
    print(" [Synthesizer] Generating summary via LLM (Tokens will be tracked)...")

    # We add 'tags' here. In the LangSmith dashboard, we can filter runs by these tags.
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        tags=["summarization_model"]
    )

    prompt = (
        "You are a financial analyst. Summarize the user's request based ONLY on this context: "
        f"{state['context']}"
    )

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state['input_text'])
    ])

    return {"summary": response.content}


# --- 4. Build the Graph ---
workflow = StateGraph(TraceState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("synthesize", synthesize_node)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "synthesize")
workflow.add_edge("synthesize", END)

app = workflow.compile()

# --- 5. Execution & Testing ---
if __name__ == "__main__":
    print("\nTOPIC 21: OBSERVABILITY & TELEMETRY (LANGSMITH)\n")
    print("Make sure you have set LANGCHAIN_API_KEY in your environment to see traces online.\n")

    user_input = "Give me a quick overview of our Q3 performance."
    print(f"User: '{user_input}'\n")

    initial_state = {
        "input_text": user_input,
        "context": "",
        "summary": ""
    }

    # We can pass run_name and metadata during invocation.
    # This makes finding this specific run in the LangSmith dashboard incredibly easy.
    config = {
        "run_name": "Q3_Report_Trace",
        "metadata": {
            "environment": "development",
            "user_tier": "premium"
        }
    }

    # Running the app with the config pushes all telemetry to the cloud
    result = app.invoke(initial_state, config=config)

    print("-" * 60)
    print("\nFinal Agent Response:")
    print(result["summary"])
    print("\nCheck your LangSmith dashboard to see the execution graph, latency, and token cost!")
    print()
