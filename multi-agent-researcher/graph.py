from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from typing import Any, TypedDict, Literal
from agents import (
    create_supervisor_chain,
    create_researcher_agent,
    create_writer_agent,
    create_summarizer_agent
)

class ResearchState(TypedDict, total=False):
    query: str
    output_dir: str
    target_articles: int

    research_findings: list[dict[str, Any]]
    article_summaries: list[dict[str, Any]]
    draft: str
    report_path: str

    researcher_complete: bool
    summarizer_complete: bool
    writer_complete: bool

    next_step: Literal["researcher", "summarizer", "writer", "END"]
    current_sub_task: str


supervisor_chain = create_supervisor_chain()
researcher_agent = create_researcher_agent()
summarizer_agent = create_summarizer_agent()
writer_agent = create_writer_agent()


def supervisor_node(state: ResearchState) -> dict[str, Any]:
    print("\n=== SUPERVISOR ===")

    decision = supervisor_chain(state)
    next_step = str(decision.get("next_step", "")).strip()
    task = str(decision.get("task_description", "Continue workflow.")).strip()

    allowed = {"researcher", "summarizer", "writer", "END"}
    if next_step not in allowed:
        raise ValueError(f"Invalid supervisor decision: {next_step!r}")

    print(f"Decision: {next_step}")
    print(f"Task: {task}")

    return {
        "next_step": next_step,
        "current_sub_task": task,
    }


def research_node(state: ResearchState) -> dict[str, Any]:
    print("\n=== RESEARCHER ===")
    result = researcher_agent(state)
    findings = result.get("research_findings", [])
    print(f"Downloaded {len(findings)} article(s).")
    return {
        "research_findings": findings,
        "researcher_complete": result.get("researcher_complete", True),
    }

def summarize_node(state: ResearchState) -> dict[str, Any]:
    print("\n=== SUMMARIZER ===")
    result = summarizer_agent(state)
    summaries = result.get("article_summaries", [])
    print(f"Created {len(summaries)} article summary/ies.")
    return {
        "article_summaries": summaries,
        "summarizer_complete": result.get("summarizer_complete", True),
    }


def write_node(state: ResearchState) -> dict[str, Any]:
    print("\n=== WRITER ===")
    result = writer_agent(state)
    return {
        "draft": result.get("draft", ""),
        "report_path": result.get("report_path", ""),
        "writer_complete": result.get("writer_complete", True),
    }


def route_from_supervisor(state: ResearchState) -> str:
    step = str(state.get("next_step", "")).strip()

    routes = {
        "researcher": "researcher",
        "summarizer": "summarizer",
        "writer": "writer",
        "END": "__end__",
    }

    if step not in routes:
        raise ValueError(
            f"Cannot route invalid next_step: {step!r}. "
            f"State keys: {list(state.keys())}"
        )

    return routes[step]


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", research_node)
    graph.add_node("summarizer", summarize_node)
    graph.add_node("writer", write_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "summarizer": "summarizer",
            "writer": "writer",
            "__end__": END,
        },
    )
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("summarizer", "supervisor")
    graph.add_edge("writer", "supervisor")
    return graph.compile()


app = build_graph()