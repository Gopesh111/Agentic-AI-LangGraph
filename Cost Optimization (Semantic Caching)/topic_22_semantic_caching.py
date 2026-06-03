import os
import time
from typing import TypedDict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import StateGraph, START, END

# Ensure your API keys are set before running
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# --- 1. Setup Semantic Cache (Vector Database) ---
embeddings = OpenAIEmbeddings()
semantic_cache = InMemoryVectorStore(embeddings)

# Similarity threshold (0.0 to 1.0)
CACHE_THRESHOLD = 0.90

# --- 2. Define the State ---
class CacheState(TypedDict):
    question: str
    response: str
    cache_hit: bool
    similarity_score: float

# --- 3. Define the Nodes ---
def cache_check_node(state: CacheState):
    print("\n[Cache_Node] Embedding query and checking semantic cache...")
    query = state["question"]

    # Search for similar past queries
    results = semantic_cache.similarity_search_with_score(query, k=1)

    if results:
        best_match, score = results[0]

        # In LangChain's InMemoryVectorStore, the score represents similarity/distance depending on the backend.
        # For simplicity in this demo, we assume lower distance = higher similarity.
        similarity = 1.0 - (score if score < 1 else score / 2)

        print(f"[Cache_Node] Top match similarity: {similarity:.2f}")

        if similarity >= CACHE_THRESHOLD:
            print("[Cache_Node] Semantic match found (Cache HIT). Bypassing LLM.")
            return {
                "cache_hit": True,
                "response": best_match.metadata["response"],
                "similarity_score": similarity
            }

    print("[Cache_Node] No strong match found (Cache MISS).")
    return {"cache_hit": False, "similarity_score": 0.0}


def llm_generation_node(state: CacheState):
    print("[Heavy_LLM] Generating new response via OpenAI API...")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

    start = time.time()
    result = llm.invoke([HumanMessage(content=state["question"])])
    latency = time.time() - start

    final_response = result.content
    print(f"[Heavy_LLM] Generation complete in {latency:.2f}s")

    print("[Cache_Node] Saving new query and response to VectorDB...")

    # Save the exact query as the document, and the response in the metadata
    semantic_cache.add_texts(
        texts=[state["question"]],
        metadatas=[{"response": final_response}]
    )

    return {"response": final_response}


# --- 4. Conditional Routing Logic ---
def route_after_cache(state: CacheState):
    if state["cache_hit"]:
        return END  # Fast path
    return "llm_generation"  # Slow path


# --- 5. Build the Graph ---
workflow = StateGraph(CacheState)

workflow.add_node("cache_check", cache_check_node)
workflow.add_node("llm_generation", llm_generation_node)

workflow.add_edge(START, "cache_check")

# Route based on whether we hit the cache or not
workflow.add_conditional_edges(
    "cache_check",
    route_after_cache,
    {
        END: END,
        "llm_generation": "llm_generation"
    }
)

workflow.add_edge("llm_generation", END)

app = workflow.compile()

# --- 6. Execution & Testing ---
if __name__ == "__main__":
    print("\nTOPIC 22: COST OPTIMIZATION (SEMANTIC CACHING)\n")

    # Pre-warm the cache for demonstration (optional)
    # semantic_cache.add_texts(
    #     ["How do I set up my AWS credentials?"],
    #     metadatas=[{"response": "Run 'aws configure' in your terminal."}]
    # )

    test_queries = [
        "How do I set up my AWS credentials?",
        "What is the command to setup aws locally?",
        "What is the weather in Bangalore today?"
    ]

    for i, query in enumerate(test_queries):
        print(f"User: '{query}'")

        initial_state = {
            "question": query,
            "response": "",
            "cache_hit": False,
            "similarity_score": 0.0
        }

        start_time = time.time()
        result = app.invoke(initial_state)
        total_time = time.time() - start_time

        path_taken = "Fast Path (Cache)" if result["cache_hit"] else "Slow Path (LLM)"

        print(f"System: {result['response']}")
        print(f"Path: {path_taken} | Total Latency: {total_time:.3f}s")
        print("-" * 70 + "\n")
