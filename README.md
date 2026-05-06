# Agentic AI and LangGraph Series

A practical, 15-part build series documenting my transition from standard text-generation LLMs to autonomous, stateful agents using LangGraph.

The goal isn't just to build wrappers, but to understand the core engine of agency: tools, state machines, cyclic graphs, and reasoning loops.

## Track Record

| # | Topic | Script | Status |
|---|---|---|---|
| 01 | LLMs vs. Agents (The ReAct Loop) | `topic_01_react_agent.py` | Done |
| 02 | Intro to LangGraph (Chains vs Graphs) | `topic_02_langgraph_basics.py` | Done |
| 03 | Conditional Edges & Routing | `topic_03_conditional_edges.py` | Done |
| 04 | Tool Integration (Giving Agents Hands) | `topic_04_tool_integration.py` | Done |
| 05 | Persistent Checkpointing (Memory) | `topic_05_memory.py` | Done |
| 06 | Human-in-the-Loop (HITL) Architecture | `topic_06_human_in_loop.py` | Done |
| 07 | *... (Remaining topics will unlock here)* | - | Pending |

---

## Topics Covered

### Topic 01: LLMs vs. Agents - Moving from "Talking" to "Doing"
Standard LLMs struggle with deterministic tasks (like complex math) and often hallucinate. 

Instead of treating the model like a database, I used it as a Reasoning Engine. I implemented a basic ReAct (Reasoning + Acting) pattern. The script forces the model to stop, think about the steps, define the exact math action required, and then output the final answer. It is the first step away from static generation and towards true agentic execution.

### Topic 02: Intro to LangGraph - Moving from Chains to Graphs
Standard LangChain sequences are linear (A -> B -> C). If one step fails, the whole chain breaks. 

I moved my logic to LangGraph to solve this. LangGraph treats workflows as State Machines. I built a basic graph to understand how to define a shared `State` and route data through `Nodes`. This sets the base for building agents that can actually loop back and fix their own mistakes.

### Topic 03: Conditional Edges - Adding Decision-Making
An agent needs to make its own decisions to be truly autonomous. 

I moved away from fixed paths and added Conditional Edges. I built a flow with a Writer node and a Reviewer node. If the Reviewer flags an issue, the graph dynamically routes the data back to the Writer for a revision. If it passes, it moves to the end. This is how you build self-correcting loops.

### Topic 04: Tool Integration - Giving the Agent Hands
An LLM alone cannot calculate exact math or fetch live data. 

I built a graph that acts as a router. The agent checks if it needs external compute, routes the State to a specialized "Tool Node" (like a calculator or API), and injects the exact data back into the memory.

### Topic 05: Persistent Checkpointing - Giving the Agent Memory
Standard APIs are stateless. To fix this, I implemented LangGraph Checkpointing. 

The graph uses "Threads" to save its State to a backend after every execution. When invoked again with the same Thread ID, it pulls the previous context. It stops wasting tokens by not needing the full chat history pasted into every prompt.

### Topic 06: Human-in-the-Loop (HITL) - The Emergency Brake
Autonomous agents need boundaries. Giving an AI access to external tools without a pause button is a major risk. 

I implemented a Human-in-the-Loop (HITL) architecture. The state machine pauses execution before triggering a critical action (like sending an email). It waits for a human to review the drafted state and explicitly approve it. If approved, the graph resumes and fires the tool. If denied, it aborts. This ensures we build safe and controllable systems.

---

