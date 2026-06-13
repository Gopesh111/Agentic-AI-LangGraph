import uvicorn
from fastapi import FastAPI, Header
from pydantic import BaseModel
from typing import TypedDict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. Define LangGraph State
# ============================================================

class AgentState(TypedDict):
    issue_title: str
    issue_body: str
    author: str
    analysis: str
    action_taken: str


# ============================================================
# 2. LangGraph Nodes
# ============================================================

def analyze_issue_node(state: AgentState):
    print(f"[Agent] Analyzing issue: {state['issue_title']}")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2
    )

    prompt = f"""
You are a software engineering triage assistant.

Issue Title:
{state['issue_title']}

Issue Description:
{state['issue_body']}

Provide:
1. A short technical analysis
2. A possible next step
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "analysis": response.content
    }


def review_node(state: AgentState):
    print("[Review Queue] Draft analysis awaiting approval")

    # Demo approval step
    # In production, this could be a human review workflow.
    return {}


def take_action_node(state: AgentState):
    print("[GitHub Tool] Preparing response")

    comment = f"""
Hello @{state['author']},

Automated Analysis:

{state['analysis']}

Please review before taking action.
"""

    print(comment)

    # Demo implementation.
    # In production this could post a GitHub comment,
    # create a ticket, send a notification, etc.

    return {
        "action_taken": "Draft response generated"
    }


# ============================================================
# 3. Build LangGraph Workflow
# ============================================================

workflow = StateGraph(AgentState)

workflow.add_node("analyze", analyze_issue_node)
workflow.add_node("review", review_node)
workflow.add_node("action", take_action_node)

workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", "review")
workflow.add_edge("review", "action")
workflow.add_edge("action", END)

agent_app = workflow.compile()


# ============================================================
# 4. FastAPI Setup
# ============================================================

app = FastAPI(
    title="Event-Driven LangGraph Agent"
)


class IssuePayload(BaseModel):
    action: str
    issue: dict


@app.post("/webhook/github")
async def github_webhook(
    payload: IssuePayload,
    x_hub_signature: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint.

    In production, verify the webhook signature before
    processing the payload.
    """

    print("\n" + "=" * 60)
    print("[FastAPI] Webhook received")

    if payload.action != "opened":
        return {
            "status": "ignored",
            "reason": "Not a new issue"
        }

    issue_data = payload.issue

    title = issue_data.get(
        "title",
        "Unknown"
    )

    body = issue_data.get(
        "body",
        "No description provided"
    )

    author = issue_data.get(
        "user",
        {}
    ).get(
        "login",
        "Unknown"
    )

    initial_state = {
        "issue_title": title,
        "issue_body": body,
        "author": author,
        "analysis": "",
        "action_taken": ""
    }

    print("[FastAPI] Triggering LangGraph workflow")

    result = agent_app.invoke(
        initial_state
    )

    print("[FastAPI] Workflow execution complete")
    print("=" * 60 + "\n")

    return {
        "status": "success",
        "action": result["action_taken"]
    }


# ============================================================
# 5. Run Server
# ============================================================

if __name__ == "__main__":

    print("\nTOPIC 24: EVENT-DRIVEN AGENTS (WEBHOOKS)\n")

    print("Starting FastAPI server...")
    print("Webhook Endpoint:")
    print("http://127.0.0.1:8000/webhook/github")

    print("\nExample Payload:")
    print(
        '{"action":"opened","issue":{"title":"Bug in Auth","body":"Login fails randomly.","user":{"login":"johndoe"}}}'
    )

    print("-" * 60)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
