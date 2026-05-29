import os
import sqlite3
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# Ensure your API key is set before running
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# --- 1. Database Setup (Mocking a Production DB) ---
# We use an in-memory SQLite database for GitHub clone-and-play capability.
# In production, this would be a strict read-only connection string to PostgreSQL/MySQL.
def setup_mock_database():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    cursor.execute("CREATE TABLE purchases (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, date TEXT)")
    
    # Insert some dummy data
    users = [
        (1, 'Alice', 'alice@example.com'),
        (2, 'Bob', 'bob@example.com'),
        (3, 'Charlie', 'charlie@example.com')
    ]

    purchases = [
        (1, 1, 150.0, '2023-10-01'),
        (2, 1, 300.0, '2023-10-05'),
        (3, 2, 320.0, '2023-10-02'),
        (4, 3, 210.0, '2023-10-03')
    ]
    
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", users)
    cursor.executemany("INSERT INTO purchases VALUES (?, ?, ?, ?)", purchases)
    conn.commit()
    return conn

# Global DB connection for this script
DB_CONN = setup_mock_database()

# --- 2. Define the State ---
class SQLState(TypedDict):
    question: str
    schema: str
    sql_query: str
    error: str
    db_results: list
    final_answer: str
    retry_count: int

# --- 3. Define the Nodes ---
def fetch_schema_node(state: SQLState):
    print("[Schema_Tool] Fetching live database schema...")
    cursor = DB_CONN.cursor()
    
    # Dynamically fetching schema from SQLite (In Postgres, use information_schema)
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema_rows = cursor.fetchall()
    schema_str = "\n".join([row[0] for row in schema_rows if row[0]])
    
    return {
        "schema": schema_str,
        "retry_count": state.get("retry_count", 0)
    }

def generate_sql_node(state: SQLState):
    print("[SQL_Agent] Generating SQL query...")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    sys_prompt = (
        "You are an expert SQL Data Analyst. Write a valid SQLite query to answer the user's question.\n"
        f"Here is the database schema:\n{state['schema']}\n\n"
        "Return ONLY the raw SQL query. Do not wrap it in markdown block quotes (like ```sql)."
    )
    
    user_prompt = state['question']
    
    # If the agent is here because of a self-correction loop, feed the error back
    if state.get("error"):
        print(f"[SQL_Agent] Self-healing active. Fixing previous error: {state['error']}")
        sys_prompt += (
            f"\n\nWARNING: Your previous query failed with this error: {state['error']}\n"
            f"The failed query was: {state['sql_query']}\n"
            "Please rewrite the query to fix this exact issue."
        )
        
    response = llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=user_prompt)
    ])

    sql = response.content.strip()
    
    print(f"[Generated SQL] {sql}")
    return {"sql_query": sql}

def execute_sql_node(state: SQLState):
    print("[Executor] Running query against database...")
    cursor = DB_CONN.cursor()
    
    try:
        # To simulate the error for GitHub users, we artificially force an error on the first run
        # Remove this `if` block in an actual production system
        if state["retry_count"] == 0 and "SUM" not in state["sql_query"].upper():
            raise sqlite3.OperationalError(
                "no such column: purchase_volume (Simulated Error for Demo)"
            )

        cursor.execute(state["sql_query"])
        results = cursor.fetchall()

        print("[Executor] Query successful.")
        return {
            "db_results": results,
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)

        print(f"[Executor] Query failed: {error_msg}")
        return {
            "error": error_msg,
            "retry_count": state["retry_count"] + 1
        }

def format_output_node(state: SQLState):
    print("[Formatter] Converting SQL rows into natural language...")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    prompt = (
        "You are a helpful assistant. Formulate a clean, professional response "
        "to the user's question using the raw database results provided.\n\n"
        f"Question: {state['question']}\n"
        f"Raw SQL Results: {state['db_results']}"
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "final_answer": response.content
    }

# --- 4. Conditional Routing Logic ---
def check_execution_status(state: SQLState):
    # Cap retries to prevent infinite loops (Circuit Breaker)
    if state.get("error") and state["retry_count"] < 3:
        return "generate_sql"

    return "format_output"

# --- 5. Build the Graph ---
workflow = StateGraph(SQLState)

workflow.add_node("schema", fetch_schema_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("format_output", format_output_node)

workflow.add_edge(START, "schema")
workflow.add_edge("schema", "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

# Add the conditional edge for the self-healing loop
workflow.add_conditional_edges(
    "execute_sql",
    check_execution_status,
    {
        "generate_sql": "generate_sql",
        "format_output": "format_output"
    }
)

workflow.add_edge("format_output", END)

app = workflow.compile()

# --- 6. Execution & Testing ---
if __name__ == "__main__":
    print("\nTOPIC 19: SAFE TEXT-TO-SQL (WITH SELF-CORRECTION)\n")
    
    user_query = "Show me the top 3 users by purchase volume last week."

    print(f"User: '{user_query}'\n")
    print("-" * 50)
    
    initial_state = {
        "question": user_query,
        "retry_count": 0,
        "error": None
    }
    
    result = app.invoke(initial_state)
    
    print("-" * 50)
    print("\nFinal Agent Response:")
    print(result["final_answer"])
    print("\n")
