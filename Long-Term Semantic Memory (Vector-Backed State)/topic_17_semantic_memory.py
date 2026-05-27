
import os
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore


# Ensure your API key is set
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"


# =========================================================
# 1. LONG-TERM MEMORY SETUP
# =========================================================

# In production:
# Replace InMemoryVectorStore with FAISS, Chroma, or Pinecone

embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)


# =========================================================
# 2. MEMORY TOOL
# =========================================================

@tool
def save_to_memory(fact: str) -> str:
    """
    Save important user facts/preferences into long-term memory.
    """

    print(f"\n[VectorDB] Saving memory: '{fact}'")

    vector_store.add_texts([fact])

    return f"Saved memory: {fact}"


tools = [save_to_memory]
tool_node = ToolNode(tools)


# =========================================================
# 3. AGENT STATE
# =========================================================

class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]


# =========================================================
# 4. CHATBOT NODE
# =========================================================

def chatbot_node(state: MemoryState):

    # Latest user message
    last_user_message = state["messages"][-1].content

    print("\n[Retrieval] Searching long-term memory...")

    # Retrieve relevant memories
    docs = vector_store.similarity_search(last_user_message, k=2)

    retrieved_memories = "\n".join(
        [doc.page_content for doc in docs]
    )

    if retrieved_memories:
        print(f"[Context] Found memories:\n{retrieved_memories}")
    else:
        print("[Context] No relevant memories found.")

    # System prompt with retrieved memories
    system_prompt = (
        "You are a helpful AI assistant with long-term memory.\n\n"
        "Known user facts:\n"
        f"{retrieved_memories}\n\n"
        "Use these memories only if relevant.\n"
        "If the user shares a new lasting preference or fact, "
        "save it using the save_to_memory tool."
    )

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0
    )

    llm_with_tools = llm.bind_tools(tools)

    messages_to_pass = [
        SystemMessage(content=system_prompt)
    ] + state["messages"]

    response = llm_with_tools.invoke(messages_to_pass)

    return {"messages": [response]}


# =========================================================
# 5. BUILD GRAPH
# =========================================================

workflow = StateGraph(MemoryState)

workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "chatbot")

# Automatically route tool calls
workflow.add_conditional_edges(
    "chatbot",
    tools_condition
)

workflow.add_edge("tools", "chatbot")

app = workflow.compile()


# =========================================================
# 6. TEST RUN
# =========================================================

if __name__ == "__main__":

    print("\n================ LONG-TERM AI MEMORY =================\n")

    # -------------------------------------------------
    # DAY 1
    # -------------------------------------------------

    print("DAY 1\n")

    msg1 = (
        "Hi, I'm building a backend. "
        "I strictly prefer Python and FastAPI over Node.js."
    )

    print(f'User: "{msg1}"\n')

    result = app.invoke({
        "messages": [
            HumanMessage(content=msg1)
        ]
    })

    print(f'Agent: {result["messages"][-1].content}\n')

    # Simulate old chats disappearing
    print("DAY 45 (Chat history cleared)\n")

    msg2 = "Write a quick hello world API for me."

    print(f'User: "{msg2}"\n')

    result2 = app.invoke({
        "messages": [
            HumanMessage(content=msg2)
        ]
    })

    print(f'Agent:\n{result2["messages"][-1].content}\n')

    print("=" * 60)
