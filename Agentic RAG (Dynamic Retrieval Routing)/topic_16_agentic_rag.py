import os
from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Ensure your API key is set
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# --- 1. Define the State ---
class RAGState(TypedDict):
    question: str
    intent: str
    context: str
    answer: str

# --- 2. Structured Output Schema for the Router ---
class RouteQuery(BaseModel):
    """Route the user query to the most relevant data source."""
    datasource: Literal["vector_db", "sql_db", "web_search"] = Field(
        description="Route the query to vector DB (docs), SQL DB (analytics), or web search (live data)."
    )

# --- 3. Graph Nodes ---
def router_node(state: RAGState):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    structured_llm = llm.with_structured_output(RouteQuery)

    print("[Router] Analyzing prompt intent via LLM...")
    routing_decision = structured_llm.invoke(state["question"])

    return {"intent": routing_decision.datasource}

def vector_search_node(state: RAGState):
    print("[VectorDB] Executing semantic search...")
    simulated_docs = "Company policy states remote work is allowed 2 days a week."
    return {"context": simulated_docs}

def sql_search_node(state: RAGState):
    print("[SQL] Querying database...")
    simulated_data = "Result: 420 new premium users signed up last month."
    return {"context": simulated_data}

def web_search_node(state: RAGState):
    print("[WebSearch] Fetching live data...")
    simulated_web = "Live News: Tesla stock price is currently $214.50."
    return {"context": simulated_web}

def generate_answer_node(state: RAGState):
    print("[LLM] Generating final answer...")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

    prompt = (
        "Answer the question ONLY using the context below.\n\n"
        f"Context: {state['context']}\n\n"
        f"Question: {state['question']}"
    )

    response = llm.invoke(prompt)
    return {"answer": response.content}

# --- 4. Conditional Routing ---
def route_to_tool(state: RAGState):
    return state["intent"]

# --- 5. Build Graph ---
workflow = StateGraph(RAGState)

workflow.add_node("router", router_node)
workflow.add_node("vector_db", vector_search_node)
workflow.add_node("sql_db", sql_search_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate_answer_node)

workflow.add_edge(START, "router")

workflow.add_conditional_edges(
    "router",
    route_to_tool,
    {
        "vector_db": "vector_db",
        "sql_db": "sql_db",
        "web_search": "web_search"
    }
)

workflow.add_edge("vector_db", "generate")
workflow.add_edge("sql_db", "generate")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

# --- 6. Execution ---
if __name__ == "__main__":
    questions = [
        "What is our company policy on remote work?",
        "How many premium users signed up last month?",
        "What is the current stock price of Tesla?"
    ]

    print("TOPIC 16: AGENTIC RAG (REAL LLM ROUTING)\n")

    for q in questions:
        print(f"User: {q}")
        result = app.invoke({
            "question": q,
            "context": "",
            "intent": "",
            "answer": ""
        })
        print(f"Answer: {result['answer']}")
        print("-" * 60)
