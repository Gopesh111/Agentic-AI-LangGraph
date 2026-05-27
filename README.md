# Agentic AI and LangGraph Series

A practical, 30 part build series documenting my transition from standard text-generation LLMs to autonomous, stateful agents using LangGraph.

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
| 07 | Parallel Execution (Fan-out/Fan-in) | topic_07_parallel_execution.py | Done |
| 08 | Sub-Graphs & Multi-Agent Systems | topic_08_multi_agent.py | Done |
| 09 | Time Travel (State Rewind) | topic_09_time_travel.py | Done |
| 10 | Self-Reflection & Correction (Critic Loop) | topic_10_self_reflection.py | Done |
| 11 | Context Management (Memory Summarization) | topic_11_memory_manager.py | Done |
| 12 | Structured Outputs (Pydantic Enforced JSON) | topic_12_structured_output.py | Done |
| 13 | Reliability (Circuit Breaker Pattern) | topic_13_circuit_breaker.py | Done |
| 14 | Human-in-the-Loop & Self-Healing Execution | topic_14_code_interpreter.py | Done |
| 15 | Real-Time State Streaming & UX | topic_15_state_streaming.py | Done |
| 16 | Agentic RAG (Dynamic Retrieval Routing) | topic_16_agentic_rag.py | Done |
| 17 | Long-Term Semantic Memory (Vector-Backed State) | topic_17_semantic_memory.py | Done |

---

### Topic 16: Agentic RAG (Dynamic Retrieval Routing)
Standard RAG pipelines treat every user query like a document search problem. If you ask a standard RAG system for specific database metrics or live internet data, it will blindly search its text vectors, find nothing useful, and likely hallucinate an answer.

To fix this, I engineered an Agentic RAG workflow with a dedicated "Router Node". Instead of immediately retrieving data, the graph first routes the user's prompt to an LLM bound with strict Pydantic structured outputs. This router acts as a traffic cop, classifying the intent and dynamically directing the flow to either a Vector Database (for unstructured docs), a SQL tool (for structured numbers), or a Web Search API (for real-time info). Giving the AI the ability to choose its tools drastically reduces hallucinations and makes the system reliable across varied domains.

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

### Topic 07: Parallel Execution - Multi-tasking for Performance
Sequential tool calling is the biggest bottleneck in agentic workflows. If an agent needs to perform a web search, query a database, and scan a PDF one by one, the latency becomes unacceptable for production.

I implemented a Parallel Execution (Fan-out / Fan-in) architecture in LangGraph. The system now triggers multiple worker nodes simultaneously across different threads. Once all parallel processes resolve, an aggregator node merges the shared State and synthesizes the final output. This architectural shift dropped my execution time by almost 60%, moving the system from a sluggish script to a production-grade backend.

### Topic 08: Multi-Agent Systems - The Supervisor Pattern
Putting all logic into a single "God Agent" leads to bloated context windows and high hallucination rates. It is similar to writing an entire backend in one file. 

I restructured my architecture to use a Multi-Agent Supervisor pattern. I built a central Supervisor node that delegates specific sub-tasks to specialized micro-agents (e.g., a Researcher and a Coder). The sub-agents execute their narrow tasks and report back to the Supervisor, which then decides the next route. Applying the "Separation of Concerns" principle to AI agents made the system modular and significantly more accurate.

### Topic 09: Time Travel - State Rewind & Modification
When a standard AI agent makes a mistake halfway through a task, you usually have to restart the entire prompt, wasting compute and API tokens. 

Because LangGraph uses checkpointing, I implemented a "Time Travel" feature. If the agent makes a hallucination at step 2, I can pause the graph, fetch the exact state from that specific node, manually correct the variables (e.g., fix a typo), and resume execution from step 3. It acts like a "Ctrl+Z" for AI workflows and makes debugging multi-step logic incredibly efficient.

### Topic 10: Self-Reflection & Correction (The Critic Loop)
Zero-shot AI generation is risky; LLMs frequently hallucinate or write buggy code on the first attempt. To solve this, I moved away from linear execution and built a cyclic graph. 

I implemented a Self-Reflection loop where a "Generator" node creates an initial draft, and a "Critic" node evaluates it. If the Critic finds an error, the graph dynamically routes backward, feeding the error logs back to the Generator to force a rewrite. The loop only terminates when the Critic approves the output or a maximum iteration limit is reached. This drastically improves the reliability of the final output.

### Topic 11: Context Management (Memory Summarization)
Saving chat history (Topic 05) is necessary, but passing the entire raw history into every new LLM prompt quickly leads to token limit crashes. 

To solve this, I added a dynamic Memory Manager. The system uses a conditional entry point to check the `chat_history` length. If it exceeds a threshold, it routes to a `Summarizer` node that compresses older conversations into a dense string. This approach **reduced token consumption by ~80%** in long-running sessions, ensuring the agent remains cost-effective and responsive without "forgetting" the user's intent.

### Topic 12: Structured Outputs (Pydantic Enforced JSON)
LLMs natively output unstructured text. If a backend system expects JSON and the AI includes extra conversational text (e.g., "Here is your JSON:"), the JSON parser crashes. 

To guarantee type safety, I implemented Structured Outputs in LangGraph. By defining a strict Pydantic `BaseModel` and binding it to the LLM node using `.with_structured_output()`, the agent is mathematically forced to adhere to the exact database schema. This eliminates the need for messy string manipulation or prompt engineering to get clean, reliable JSON data.

### Topic 13: Reliability (Circuit Breaker Pattern)
When an external tool fails, AI agents tend to panic and retry the same step repeatedly. In an automated workflow, this results in an infinite loop that rapidly drains API credits and crashes the system.

To fix this, I implemented a Circuit Breaker pattern directly into the LangGraph state. By adding a `retry_count` tracker and a conditional routing edge, the graph monitors its own failures. If a node fails three consecutive times, the router cuts the connection and forces a graceful exit. This basic architectural addition is crucial for preventing runaway token consumption during local testing and deployment.

### Topic 14: Human-in-the-Loop & Self-Healing Execution (The Code Sandbox)
To safely allow an LLM to execute local code without risking system security or runaway API billing, I built a multi-node LangGraph architecture combining a human-in-the-loop safety gateway with an automated self-healing loop. The graph first routes the task to an AI Coder node to generate the Python script, then completely pauses state progression to await explicit human approval (`y/n`) in the terminal. Once cleared, the code runs locally inside an isolated subprocess environment protected by a strict 10-second timeout. If the script crashes, the architecture captures the exact traceback error (`stderr`), updates the graph state, and automatically routes it back to the coder node for autonomous patching and rewrite, creating a secure and reliable runtime circuit breaker.

### Topic 15: Real-Time State Streaming & UX (Solving the Spinner Problem)
Standard LLMs stream text fast, but agentic workflows (like LangGraph) execute heavy background tasks—writing code, accessing databases, and running self-correction loops. Waiting for a single final API response freezes the frontend, leading to a terrible user experience where users often refresh the page and waste API credits.

To solve this, I moved away from static execution and engineered a real-time state streaming setup. By using LangGraph's streaming capabilities, the graph yields its internal state after every single node execution. This allows the backend to stream live logs (e.g., tool triggers, syntax error patches) directly to the client. I also integrated the human-in-the-loop safety gate from Topic 14, allowing the system to pause mid-flight for user approval. This visibility completely removes the "is it stuck?" anxiety and provides a manual kill switch if the agent goes off-track, bridging the gap between a local script and a production-ready product.

### Topic 16: Agentic RAG (Dynamic Retrieval Routing)
Standard RAG pipelines treat every user query like a document search problem. If you ask a standard RAG system for specific database metrics or live internet data, it will blindly search its text vectors, find nothing useful, and likely hallucinate an answer.

To fix this, I engineered an Agentic RAG workflow with a dedicated "Router Node". Instead of immediately retrieving data, the graph first routes the user's prompt to an LLM bound with strict Pydantic structured outputs. This router acts as a traffic cop, classifying the intent and dynamically directing the flow to either a Vector Database (for unstructured docs), a SQL tool (for structured numbers), or a Web Search API (for real-time info). Giving the AI the ability to choose its tools drastically reduces hallucinations and makes the system reliable across varied domains.

### Topic 17: Long-Term Semantic Memory (Vector-Backed State)
Standard chat summarization works fine for a few days, but over months of conversation, the context window still overflows. Eventually, the agent drops older messages and completely forgets important user preferences.

To fix this, I engineered a long-term semantic memory layer using a Vector Database. Instead of stuffing a massive chat history into every prompt, I gave the agent a specific "Save to Memory" tool. When a user states a preference, the agent autonomously extracts and saves it to the vector store. On future queries, the system runs a background semantic search and injects only the highly relevant past memories into the context. This keeps API token usage low, maintains fast response times, and allows the agent to retain personalized context indefinitely.

---

