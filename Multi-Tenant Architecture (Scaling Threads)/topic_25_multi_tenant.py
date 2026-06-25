import os
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Ensure your API key is set before running
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 1. Define the State
class TenantState(TypedDict):
    # add_messages appends new messages to the existing list
    # for the specific thread
    messages: Annotated[list, add_messages]


# 2. Define the Agent Node
def isolated_agent_node(state: TenantState):
    print("[Agent] Processing state...")

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.5
    )

    # The LLM only sees messages from this specific user's thread
    response = llm.invoke(state["messages"])

    return {"messages": [response]}


# 3. Build the Graph with a Checkpointer
workflow = StateGraph(TenantState)

workflow.add_node("agent", isolated_agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# Initialize the Checkpointer
# In production, use PostgresSaver or RedisSaver
memory = MemorySaver()

# Compile the app and attach the checkpointer
app = workflow.compile(checkpointer=memory)


# 4. Execution & Testing (Simulating Concurrency)
if __name__ == "__main__":
    print("\nTOPIC 25: MULTI-TENANT ARCHITECTURE (THREAD ISOLATION)\n")

    # Two different users/threads using the same compiled app
    config_alice = {
        "configurable": {
            "thread_id": "session_alice_001"
        }
    }

    config_bob = {
        "configurable": {
            "thread_id": "session_bob_999"
        }
    }

    print("-" * 60)

    print("Alice: Hi, my name is Alice and I love Python.")
    app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Hi, my name is Alice and I love Python."
                )
            ]
        },
        config=config_alice,
    )

    print("Bob: Hey, I am Bob and I code in Rust.")
    app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Hey, I am Bob and I code in Rust."
                )
            ]
        },
        config=config_bob,
    )

    print("-" * 60)

    print("\nTESTING ISOLATION...\n")

    print("Alice asks: What is my name and my favorite language?")
    result_alice = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is my name and my favorite language?"
                )
            ]
        },
        config=config_alice,
    )

    print(
        f"Agent (Thread Alice): "
        f"{result_alice['messages'][-1].content}"
    )

    print()

    print("Bob asks: What is my name and what do I code in?")
    result_bob = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="What is my name and what do I code in?"
                )
            ]
        },
        config=config_bob,
    )

    print(
        f"Agent (Thread Bob): "
        f"{result_bob['messages'][-1].content}"
    )

    print("-" * 60)
