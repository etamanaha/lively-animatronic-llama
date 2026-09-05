
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages

from europepmc import get_fulltext, search_europepmc
from helper_functions import upsert_file, page_specific_references, reference_files, llm

from datetime import datetime, timezone
date_str = datetime.now(timezone.utc).date().isoformat()

class PagePlan(BaseModel):
    title: str = Field(description="Title of the page")
    path: str = Field(description="Relative path to the file")
    page_type: Literal[
        "concept", "chemical", "biology", "endpoint", "assay", "dataset",
        "model", "literature", "evidence"
    ]
    category: Literal[
        "02-concepts", "03-chemicals", "04-biology", "04-toxicological-endpoints", 
        "06-assays", "07-datasets", "08-models-and-methods", "09-literature", 
        "10-evidence","13-projects"
    ]
    reasoning: str = Field(description="Reasoning for why this page should be created")


class PagePlanList(BaseModel):
    pages: list[PagePlan]


class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    core_pages: list[dict]
    core_created: list[dict]
    active_page: dict | None
    done: bool

SEARCH_TOOL_NAME = search_europepmc.name
FULLTEXT_TOOL_NAME = get_fulltext.name
UPSERT_TOOL_NAME = upsert_file.name

research_tools = [get_fulltext, search_europepmc, upsert_file]

# Tool permissions narrow as research progresses. This prevents a second search.
llm_core_write = llm.bind_tools(research_tools)
llm_after_search = llm.bind_tools([get_fulltext, upsert_file])
llm_after_fulltext = llm.bind_tools([upsert_file])
llm_force_write = llm.bind_tools([upsert_file], tool_choice="required")

tool_node = ToolNode(research_tools)

planner_llm = llm.with_structured_output(PagePlanList, include_raw=False)

def planner_context() -> list[SystemMessage]:
    return [
        SystemMessage(content=f"CATEGORY DESCRIPTIONS:\n{reference_files['categories']}"),
        SystemMessage(content=f"OVERVIEW:\n{reference_files['overview']}")
        #SystemMessage(content=f"OUTLINE:\n{reference_files['outline']}")
    ]

def writer_context(page: dict) -> list[SystemMessage]:
    category_text, template_text = page_specific_references(page)
    return [
        SystemMessage(content=reference_files["core_prompt"]),
        SystemMessage(content=f"SPECS:\n{reference_files['specs']}"),
        SystemMessage(content=f"CATEGORY GUIDANCE FOR THIS PAGE:\n{category_text or '(No matching category section found.)'}"),
        SystemMessage(content=f"TEMPLATE EXAMPLE FOR THIS PAGE TYPE:\n{template_text or '(No matching page-type template found.)'}"),
    ]

def page_prompt(page: dict, pages: list[dict]) -> HumanMessage:
    page_titles = "\n".join(
        f"  Path: {p['path']}"
        for p in pages
        if p["path"] != page["path"]
    )

    return HumanMessage(content=f"""
Create exactly one wiki page. Do not create, research, or modify any other page.

- Title: {page['title']}
- Path: {page['path']}
- Page type: {page['page_type']}
- Category: {page['category']}
- Reasoning: {page['reasoning']}

## OBJECTIVE

Seed one structurally complete, ingestion-ready wiki page for this topic. This is an initial wiki-seeding task, not a comprehensive literature review or final content-ingestion task.

The primary goal is to create a page that follows the required specifications, has valid frontmatter, includes the required sections and citation schema, and provides a small amount of accurate, useful starting context. Later ingestion will expand the page using additional articles and evidence.

A concise page with correct structure and one well-supported claim is better than a more detailed page with missing sections, invalid formatting, weak citations, or unsupported claims.

## RESEARCH AND TOOL LIMITS

1. Research only this page topic using the available tools.
2. Call `search_europepmc` at most once, with `max_result` set to 15.
3. After `search_europepmc` has been called, do not call it again.
4. Select at most one relevant article from the search results.
5. If the selected article has a full-text identifier, call `get_fulltext` once for that article.
6. After `get_fulltext` returns—or after determining that no relevant article is available—call `upsert_file` immediately.
7. Do not perform additional research after `get_fulltext`.
8. You must call `upsert_file` before considering the task complete. Do not respond with only a draft or explanation.

## ARTICLE SELECTION

Choose one article that is relevant to the page topic and can provide initial operational context, especially:

- how {page['title']} is used in computational toxicology;
- its scope, purpose, or role;
- clear methodology or practical applications;
- important limitations or interpretation considerations.

Prefer relevance and usefulness for page seeding over article completeness, prestige, recency, or the amount of extractable text. The article only needs to support a concise starting page; it does not need to support comprehensive coverage.

Do not force an article into the page merely because it appears in the search results. Do not invent details, citations, or claims that are not supported by the selected article or the provided specifications.

## IF NO RELEVANT ARTICLE EXISTS

If none of the search results is relevant to the page topic and purpose, call `upsert_file` without calling `get_fulltext`.

Create the page with the required structure, frontmatter, headings, and citation schema. Include only accurate topic information available from the page definition, specifications, or search results. Do not include an example citation, placeholder citation presented as real, or irrelevant article.

## WRITING PRIORITY

Follow this priority order:

1. Use exactly the requested path and create exactly one page.
2. Follow the provided specifications, page templates, checklist, and required headers.
3. Produce valid, properly formatted frontmatter.
4. Include a completed citation schema using only verified article metadata.
5. Create all required sections, even when some sections contain concise initial content.
6. Use the selected article to provide a modest amount of accurate, operational context.
7. Provide a MAX of 1 claim schema with the `claim_type`: `definition` or `fact`
8. Avoid  unnecessary detail and exhaustive article summaries.
9. Leave the page ready for later ingestion and expansion.

Do not omit required sections because the article lacks enough information. Use concise wording and clearly indicate limits where appropriate. Do not pad the page with generic prose simply to make it appear complete.

Cite ALL information using citation id (cit-001)

## FILE CREATION REQUIREMENTS

Call `upsert_file` with the completed page content and exactly this path:
{page['path']}

Include properly formatted frontmatter and the completed citation schema. Follow the provided specifications, page templates, and checklist.

## PAGE TITLES AVAILABLE FOR CROSS-LINKING

{page_titles}

Use available page titles when creating links. Format each link as:

[Page Title](../category/page-title-in-kebab-case)

Example:

- [Adverse Outcome Pathways](../02-concepts/adverse-outcome-pathways)
- [Micronucleus Assay](../06-assay/micronucleus-assay)

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
        CORE PAGES: inform users on topics important to computational toxicology
        - page type: `concept`, `chemical`, `biology`, `endpoint`, `assay`, `dataset`, `model`, `literature`, `evidence`
        - category: `02-concepts`, `03-chemicals`, `04-biology`, `05-toxicological-endpoints`, `06-assays`, `07-datasets`, `08-models-and-methods`, `09-literature`, `10-evidence`, `13-projects`

        Determine the pages that need to be created under the above list of categories to complete the wiki-seeding process.
        Do NOT list pages for other categories.
        The parent folder and category MUST be the SAME.
        A completed wiki-seeding would create ALL the pages in `## D7. Core Page Families and Seed Lists` of the `OUTLINE`.
        """)]
    )

    # A path is the page identity. This prevents duplicate planned pages.
    unique = {}
    for page in plan.pages:
        unique[page.path] = page.model_dump()
    print(unique)
    return list(unique.values())

def llm_node(state: State):
    """Plan once, then research/write exactly one page at a time."""
    if state.get("done"):
        return {"done": True}

    pages = state.get("core_pages", []) or plan_pages()
    created = state.get("core_created", [])
    active = state.get("active_page")
    messages = state.get("messages", [])

    created_paths = {page["path"] for page in created}
    remaining = [page for page in pages if page["path"] not in created_paths]

    if not remaining and active is None:
        return {"core_pages": pages, "core_created": created, "done": True}

    page = active or remaining[0]
    request = writer_context(page) + [page_prompt(page, pages)]
    if active:
        request += messages

    if any(isinstance(m, ToolMessage) and m.name == FULLTEXT_TOOL_NAME for m in messages):
        writer = llm_after_fulltext
    elif any(isinstance(m, ToolMessage) and m.name == SEARCH_TOOL_NAME for m in messages):
        writer = llm_after_search
    else:
        writer = llm_core_write

    return {
        "messages": [writer.invoke(request)],
        "core_pages": pages,
        "core_created": created,
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
    pages = state.get("core_pages", [])
    created = state.get("core_created", [])

    if not page or not page_was_written(state):
        raise RuntimeError("complete_page reached before a successful upsert_file call.")

    if page["path"] not in {item["path"] for item in created}:
        created = [*created, page]

    done = len({item["path"] for item in created}) >= len({item["path"] for item in pages})

    return {
        "messages": remove_all_messages(state),
        "core_pages": pages,
        "core_created": created,
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


def remove_search_results(state: State):
    """Delete the search ToolMessage and its matching AI tool-call message."""
    messages = state.get("messages", [])
    search_call_ids = set()
    ids_to_remove = set()

    for message in messages:
        if isinstance(message, ToolMessage) and message.name == SEARCH_TOOL_NAME:
            ids_to_remove.add(message.id)
            if message.tool_call_id:
                search_call_ids.add(message.tool_call_id)

    for message in messages:
        calls = getattr(message, "tool_calls", []) or []
        if any(call.get("id") in search_call_ids for call in calls):
            ids_to_remove.add(message.id)

    return {"messages": [RemoveMessage(id=i) for i in ids_to_remove]}

def after_tool(state: State):
    for message in reversed(state.get("messages", [])):
        if isinstance(message, ToolMessage):
            if message.name == UPSERT_TOOL_NAME:
                return "complete_page"
            if message.name == FULLTEXT_TOOL_NAME:
                return "filter_search_results"
            return "llm"
    return "llm"

graph = StateGraph(State)
graph.add_node("llm", llm_node)
graph.add_node("force_write", force_write_node)
graph.add_node("tools", tool_node)
graph.add_node("filter_search_results", remove_search_results)
graph.add_node("complete_page", complete_page)

graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", should_continue, {"tools": "tools", "force_write": "force_write", "end": END})
graph.add_edge("force_write", "tools")
graph.add_conditional_edges("tools", after_tool, {"complete_page": "complete_page", "filter_search_results": "filter_search_results", "llm": "llm"})
graph.add_edge("filter_search_results", "llm")
graph.add_edge("complete_page", "llm")

from langgraph.checkpoint.memory import InMemorySaver
app = graph.compile()#checkpointer=InMemorySaver())

initial_state = {
        "messages": [HumanMessage(content=(
            "Create the initial core pages for the wiki. Make sure they are properly "
            "formatted according to the specs and relevant to the overview."
        ))],
        "core_pages": [],
        "core_created": [],
        "active_page": None,
        "done": False,
    }

#config = {"configurable": {"thread_id": "core-page-build-1"}},

app.invoke(initial_state)#, config=config)
#app.invoke(None, config=config)


