"""
LinkedIn Content Agent - LangGraph Multi-Agent Pipeline
Orchestrates: Research → Draft → Review → Publish
"""

import json
import sys
import os
from datetime import datetime
from typing import TypedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from langgraph.graph import StateGraph, END
from research import run_research
from draft import run_draft
from review import run_review


# ─── Shared State ────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    topic: str                        # Input topic/keyword
    research_insights: str            # Output from research agent
    draft_post: str                   # Output from draft agent
    final_post: str                   # Output from review agent
    review_feedback: str              # Critique from review agent
    approved: bool                    # Did review agent approve?
    iteration: int                    # Rewrite count
    trace: dict                       # Cost & timing metadata


# ─── Node Functions ───────────────────────────────────────────────────────────

def research_node(state: AgentState) -> AgentState:
    print(f"\n🔍 [RESEARCH AGENT] Scanning trends for: '{state['topic']}'...")
    start = datetime.now()

    insights = run_research(state["topic"])

    elapsed = (datetime.now() - start).total_seconds()
    state["research_insights"] = insights
    state["trace"]["research"] = {"duration_s": round(elapsed, 2)}
    print(f"   ✅ Research done in {elapsed:.1f}s")
    return state


def draft_node(state: AgentState) -> AgentState:
    print(f"\n✍️  [DRAFT AGENT] Writing LinkedIn post (iteration {state['iteration'] + 1})...")
    start = datetime.now()

    post = run_draft(
        topic=state["topic"],
        insights=state["research_insights"],
        feedback=state.get("review_feedback", ""),
        iteration=state["iteration"]
    )

    elapsed = (datetime.now() - start).total_seconds()
    state["draft_post"] = post
    state["trace"].setdefault("drafts", []).append({
        "iteration": state["iteration"] + 1,
        "duration_s": round(elapsed, 2)
    })
    print(f"   ✅ Draft done in {elapsed:.1f}s")
    return state


def review_node(state: AgentState) -> AgentState:
    print(f"\n🎯 [REVIEW AGENT] Stress-testing the post...")
    start = datetime.now()

    approved, feedback, final_post = run_review(state["draft_post"])

    elapsed = (datetime.now() - start).total_seconds()
    state["approved"] = approved
    state["review_feedback"] = feedback
    state["final_post"] = final_post if approved else state["draft_post"]
    state["trace"]["review"] = {"duration_s": round(elapsed, 2), "approved": approved}

    status = "✅ APPROVED" if approved else "🔄 NEEDS REWRITE"
    print(f"   {status} in {elapsed:.1f}s")
    if not approved:
        print(f"   Feedback: {feedback[:120]}...")
    return state


def save_output_node(state: AgentState) -> AgentState:
    print(f"\n💾 [OUTPUT] Saving post and traces...")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = state["topic"].lower().replace(" ", "_")[:30]

    os.makedirs("output/posts", exist_ok=True)
    os.makedirs("output/traces", exist_ok=True)

    # Save post
    post_path = f"output/posts/{ts}_{slug}.md"
    with open(post_path, "w") as f:
        f.write(f"# LinkedIn Post — {state['topic']}\n")
        f.write(f"*Generated: {datetime.now().isoformat()}*\n\n---\n\n")
        f.write(state["final_post"])

    # Save trace
    trace_path = f"output/traces/{ts}_{slug}.json"
    with open(trace_path, "w") as f:
        json.dump({
            "topic": state["topic"],
            "iterations": state["iteration"] + 1,
            "approved": state["approved"],
            "trace": state["trace"],
            "generated_at": datetime.now().isoformat()
        }, f, indent=2)

    print(f"   📄 Post saved: {post_path}")
    print(f"   📊 Trace saved: {trace_path}")
    return state


# ─── Routing Logic ────────────────────────────────────────────────────────────

def should_rewrite(state: AgentState) -> str:
    MAX_ITERATIONS = 2
    if state["approved"]:
        return "save"
    if state["iteration"] >= MAX_ITERATIONS:
        print(f"\n⚠️  Max iterations ({MAX_ITERATIONS}) reached. Publishing best draft.")
        state["final_post"] = state["draft_post"]
        return "save"
    state["iteration"] += 1
    return "draft"  # Loop back to draft


# ─── Build LangGraph ──────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("research", research_node)
    graph.add_node("draft",    draft_node)
    graph.add_node("review",   review_node)
    graph.add_node("save",     save_output_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "draft")
    graph.add_edge("draft",    "review")
    graph.add_conditional_edges("review", should_rewrite, {
        "draft": "draft",
        "save":  "save"
    })
    graph.add_edge("save", END)

    return graph.compile()


# ─── Entry Point ─────────────────────────────────────────────────────────────

def run(topic: str):
    print(f"\n{'='*55}")
    print(f"  🚀 LinkedIn Content Agent — LangGraph")
    print(f"  Topic: {topic}")
    print(f"{'='*55}")

    app = build_graph()

    initial_state: AgentState = {
        "topic": topic,
        "research_insights": "",
        "draft_post": "",
        "final_post": "",
        "review_feedback": "",
        "approved": False,
        "iteration": 0,
        "trace": {}
    }

    final_state = app.invoke(initial_state)

    print(f"\n{'='*55}")
    print(f"  ✨ FINAL POST")
    print(f"{'='*55}")
    print(final_state["final_post"])
    print(f"\n  Iterations: {final_state['iteration'] + 1}")
    return final_state


if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI agents in production 2025"
    run(topic)