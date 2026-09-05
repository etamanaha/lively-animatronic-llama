from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages

from datetime import datetime, timezone
date_str = datetime.now(timezone.utc).date().isoformat()

from helper_functions import upsert_file, page_specific_references, reference_files, llm

UPSERT_TOOL_NAME = upsert_file.name

class PagePlan(BaseModel):
    title: str = Field(description="Title of the page")
    path: str = Field(description="Relative path to the file")
    page_type: Literal["index", "governance", "agent_operation", "workflow"]
    category: Literal["00-system", "11-workflows", "12-agent_operations", "14-quality-and-governance", "15-glossary"]
    reasoning: str = Field(description="Reasoning for why this page should be created")

class PagePlanList(BaseModel):
    pages: list[PagePlan]

class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    info_pages: list[dict]
    info_created: list[dict]
    active_page: dict | None
    done: bool

write_tools = [upsert_file]
llm_info_write = llm.bind_tools(write_tools)
llm_force_write = llm.bind_tools([upsert_file], tool_choice="required")

tool_node = ToolNode(write_tools)

planner_llm = llm.with_structured_output(PagePlanList, include_raw=False)

def planner_context() -> list[SystemMessage]:
    return [
        SystemMessage(content=f"CATEGORY DESCRIPTIONS:\n{reference_files['categories']}"),
        SystemMessage(content=f"OUTLINE:\n{reference_files['outline']}")
    ]

def writer_context(page: dict) -> list[SystemMessage]:
    category_text, template_text = page_specific_references(page)
    return [
        SystemMessage(content=reference_files["info_prompt"]),
        SystemMessage(content=f"CATEGORY GUIDANCE FOR THIS PAGE:\n{category_text or '(No matching category section found.)'}"),
        SystemMessage(content=f"TEMPLATE EXAMPLE FOR THIS PAGE TYPE:\n{template_text or '(No matching page-type template found.)'}"),
        SystemMessage(content=f"SPECS:\n{reference_files['specs']}"),        
        SystemMessage(content=f"OUTLINE:\n{reference_files['outline']}"),
    ]

def page_prompt(page: dict, pages: list[dict]) -> HumanMessage:
    page_titles = "\n".join(
        f"  Title: {p['title']}\n"
        f"  Path: {p['path']}"
        for p in pages
        if p["path"] != page["path"]
    )
    return HumanMessage(content=f"""
Create exactly one wiki page. Do not create or research any other page.
Title: {page['title']}
Path: {page['path']}
Page type: {page['page_type']}
Category: {page['category']}
Reasoning: {page['reasoning']}

Create a comprehensive wiki page that explains the wiki structure, governance, or agent operations.
Focus on providing clear, actionable information about how the wiki is organized and how agents interact with it.

You must call upsert_file before considering this page complete. Do not respond with
just a draft or explanation. Include properly formatted frontmatter and a completed
citation schema. Follow the provided specifications, page templates, and checklist.

PAGE TITLES AVAILABLE FOR CROSS-LINKING:
{page_titles}

EXAMPLE OF HOW TO FORMAT RELATED PAGE
- [Evidence Standards](../00-system/evidence-standards)
- [Human Review Checkpoints](../14-quality-and-governance/human-review-checkpoints)

Use the available page titles when creating links. Format each link as:
[Page Title](../category/page-title-in-kebab-case)

Use this date for frontmatter: {date_str}
""")

def remove_all_messages(state: State) -> list[RemoveMessage]:
    return [
        RemoveMessage(id=message.id)
        for message in state.get("messages", [])
        if getattr(message, "id", None)
    ]

def plan_pages() -> list[dict]:
    plan = planner_llm.invoke(
        planner_context()
        + [HumanMessage(content=f"""
    INFO PAGES: inform users on wiki structure
    - page type: `index`, `workflow`, `governance`, and `agent_operation`
    - category: `00-system`, `11-workflows`, `12-agent-operations`, `14-quality-and-governance`, and `15-glossary`

    Determine the pages that need to be created under the above list of categories to complete the wiki-seeding process.
    A completed wiki-seeding would create ALL the pages in `## D7. Core Page Families and Seed Lists` of the `OUTLINE`.
        """)]
    )

    unique = {}
    for page in plan.pages:
        unique[page.path] = page.model_dump()
    print(unique)
    return list(unique.values())

def llm_node(state: State):
    """Plan once, then write exactly one page at a time."""
    if state.get("done"):
        return {"done": True}

    pages = state.get("info_pages", []) or plan_pages()
    created = state.get("info_created", [])
    active = state.get("active_page")
    messages = state.get("messages", [])

    created_paths = {page["path"] for page in created}
    remaining = [page for page in pages if page["path"] not in created_paths]

    if not remaining and active is None:
        return {"info_pages": pages, "info_created": created, "done": True}

    page = active or remaining[0]
    request = writer_context(page) + [page_prompt(page, pages)]
    if active:
        request += messages

    return {
        "messages": [llm_info_write.invoke(request)],
        "info_pages": pages,
        "info_created": created,
        "active_page": page,
        "done": False,
    }

def force_write_node(state: State):
    """Recover when the writer stops without calling upsert_file."""
    page = state.get("active_page")
    if not page:
        raise RuntimeError("Cannot force a write without an active page.")

    response = llm_force_write.invoke(
        writer_context(page)
        + [page_prompt(page), *state.get("messages", [])]
        + [HumanMessage(content="Use the available research and call upsert_file now. Do not answer with prose.")]
    )
    return {"messages": [response]}

def page_was_written(state: State) -> bool:
    return any(isinstance(m, ToolMessage) and m.name == UPSERT_TOOL_NAME for m in state.get("messages", []))

def complete_page(state: State):
    """Mark the page complete immediately after upsert_file succeeds."""
    page = state.get("active_page")
    pages = state.get("info_pages", [])
    created = state.get("info_created", [])

    if not page or not page_was_written(state):
        raise RuntimeError("complete_page reached before a successful upsert_file call.")

    if page["path"] not in {item["path"] for item in created}:
        created = [*created, page]

    done = len({item["path"] for item in created}) >= len({item["path"] for item in pages})

    return {
        "messages": remove_all_messages(state),
        "info_pages": pages,
        "info_created": created,
        "active_page": None,
        "done": done,
    }

def should_continue(state: State):
    if state.get("done"):
        return "end"

    last = (state.get("messages") or [])[-1:]
    last = last[0] if last else None

    if getattr(last, "tool_calls", None):
        return "tools"

    if state.get("active_page"):
        return "force_write"

    return "end"

def after_tool(state: State):
    for message in reversed(state.get("messages", [])):
        if isinstance(message, ToolMessage):
            if message.name == UPSERT_TOOL_NAME:
                return "complete_page"
            return "llm"
    return "llm"

graph = StateGraph(State)
graph.add_node("llm", llm_node)
graph.add_node("force_write", force_write_node)
graph.add_node("tools", tool_node)
graph.add_node("complete_page", complete_page)

graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", should_continue, {"tools": "tools", "force_write": "force_write", "end": END})
graph.add_edge("force_write", "tools")
graph.add_conditional_edges("tools", after_tool, {"complete_page": "complete_page", "llm": "llm"})
graph.add_edge("complete_page", "llm")

app = graph.compile()

initial_state = {
    "messages": [HumanMessage(content=(
        "Create the initial info pages for the wiki. Make sure they are properly "
        "formatted according to the specs and relevant to the overview."
    ))],
    "info_pages": [],
    "info_created": [],
    "active_page": None,
    "done": False,
}

app.invoke(initial_state)