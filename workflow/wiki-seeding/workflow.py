from typing import Literal, TypedDict, Annotated
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from langgraph.types import Command
import json
from langgraph.graph import END, START, StateGraph

from datetime import datetime, timezone
date_str = datetime.now(timezone.utc).date().isoformat()

from helper_functions import (upsert_file, reference_files, llm)
from info_node import app as info_workflow_node
from core_node import app as core_workflow_node

class WikiSeedState(TypedDict):
    messages: Annotated[list, add_messages]

    docusaurus_created: list[dict]
    info_created: list[dict]
    core_created: list[dict]
    index_created: list[dict] 

    node_checklist: dict
    task_description: str

class WorkerSummary(BaseModel):
    """Structured summary from worker nodes."""
    status: str  # "completed", "partial", "error"
    details: str  # Concise human-readable summary
    files_created: list = []  # List of created files
    next_suggestion: str = ""  # Optional suggestion for next step

class SupervisorDecision(TypedDict):
    next_step: Literal["docusaurus", "info_pages", "core_pages", "index_pages", "END"]
    task_description: str

def supervisor_node(state: WikiSeedState) -> Command:
    checklist = state.get("node_checklist", {})

    return initial_creation(state)


def initial_creation(state: WikiSeedState):
    supervisor_model = llm.with_structured_output(SupervisorDecision)

    # Get only human messages (not system/tool messages)
    human_messages = [
        msg for msg in state.get("messages", [])
        if getattr(msg, "type", None) == "human"
    ]

    # Show only initial message + summaries to supervisor
    context_for_supervisor = [
        msg for msg in human_messages
        if "WorkerSummary" in msg.content or  # Summaries
        msg.content == "Create the Docusaurus-compatible wiki on computational toxicology."  # Initial
    ]
    
    prompt = f"""

Current checklist:
- docusaurus complete: {state.get("node_checklist", {}).get("docusaurus", False)}
- info_pages complete: {state.get("node_checklist", {}).get("info_pages", False)}
- core_pages complete: {state.get("node_checklist", {}).get("core_pages", False)}
- index_pages complete: {state.get("node_checklist", {}).get("index_pages", False)}

Return a concise task_description for the selected worker.
"""
    
    decision = supervisor_model.invoke([
        *context_for_supervisor,
        SystemMessage(content=reference_files["supervisor_prompt"]),
        SystemMessage(content=prompt)])
    next_step = decision["next_step"]
    task_description = decision["task_description"]

    if next_step == "info_pages":
        result = info_workflow_node.invoke({
            "messages": state.get("messages", []),
            "info_pages": [],
            "info_created": state.get("info_created", []),
            "active_page": None,
            "done": False,
        })

        return Command(
            update={
                "messages": result.get("messages", []),
                "info_created": result.get("info_created", []),
                "node_checklist": {
                    **state.get("node_checklist", {}),
                    "info_pages": True,
                },
                "task_description": task_description,
            },
            goto="supervisor",
        )

    elif next_step == "core_pages":
        result = core_workflow_node.invoke({
            "messages": state.get("messages", []),
            "core_pages": [],
            "core_created": state.get("core_created", []),
            "active_page": None,
            "done": False,
        })

        return Command(
            update={
                "messages": result.get("messages", []),
                "core_created": result.get("core_created", []),
                "node_checklist": {
                    **state.get("node_checklist", {}),
                    "core_pages": True,
                },
                "task_description": task_description,
            },
            goto="supervisor",
        )

    return Command(
        update={
            "next_step": next_step,
            "task_description": task_description,
        },
        goto=next_step,
    )

# ======== DOCUSAURUS ==========
def docusaurus_node(state: WikiSeedState) -> Command:
    docusaurus_tools = llm.bind_tools([upsert_file])
    history = state.get("messages", [])

    prompt_messages = [
        SystemMessage(content=reference_files["docusaurus_prompt"]),
        *history,
    ]

    # Add the worker task only before the first Docusaurus model call.
    has_tool_results = any(
        isinstance(message, ToolMessage)
        for message in history
    )

    if not has_tool_results:
        prompt_messages.append(
            HumanMessage(
                content=state.get(
                    "task_description",
                    "Create all required Docusaurus files.",
                )
            )
        )

    response = docusaurus_tools.invoke(prompt_messages)

    if response.tool_calls:
        return Command(
            update={"messages": [response]},
            goto="docusaurus_tools",
        )

    created = state.get("docusaurus_created", [])

    summary = WorkerSummary(
        status="completed",
        details=f"Created {len(created)} Docusaurus files",
        files_created=created,
    )

    return Command(
        update={
            "messages": [
                HumanMessage(content=f"WorkerSummary: {summary}")
            ],
            "node_checklist": {
                **state.get("node_checklist", {}),
                "docusaurus": True,
            },
        },
        goto="supervisor",
    )

def docusaurus_tools_node(state: WikiSeedState) -> Command:
    tool_node = _tool_node([upsert_file])
    result = tool_node.invoke(state)

    new_files = _collect_tool_files(result, "docusaurus_created")
    existing_files = state.get("docusaurus_created", [])

    # Avoid replacing files collected in earlier tool batches.
    files_by_path = {
        file["path"]: file
        for file in existing_files
        if "path" in file
    }

    for file in new_files:
        if "path" in file:
            files_by_path[file["path"]] = file

    files = list(files_by_path.values())

    return Command(
        update={
            # Preserve the model/tool messages so the next LLM call knows
            # which files were already created.
            "messages": result.get("messages", []),
            "docusaurus_created": files,
        },
        goto="docusaurus",
    )

# ========= INDEX ==============
def index_node(state: WikiSeedState):
    index_tools = llm.bind_tools([upsert_file])

    info_created = state.get("info_created", [])
    core_created = state.get("core_created", [])
    core_pages = [{k: v for k, v in d.items() if k != "citations"} for d in core_created]

    all_pages = info_created + core_pages

    prompt = f"""

# Description
You are in charge of creating the index pages. 
These ALL exist in `01-indices` with the page_type `index`.

# Existing wiki pages:

{json.dumps(all_pages, ensure_ascii=False, indent=2)}

# Task
Create ALL the index pages in `## D7. Core Page Families and Seed Lists` of the `OUTLINE`.
Every page should be in AT LEAST 1 index.

# Guidelines
1. **Purpose**: Index pages are curated navigation and retrieval surfaces optimized for humans and agents. They should be concise and navigational, linking to canonical pages rather than containing substantive scientific claims.
2. **Structure**: Use clear sections and headings. Include front matter fields such as `page_type: index`, `entity_class`, `curator`, `last_reviewed`, and `status`.
3. **Cross-Linking**: Ensure that each index page links to the most relevant canonical pages in other categories. Support multi-hop retrieval by building enough links to navigate across concepts, chemicals, endpoints, assays, datasets, and evidence.
4. **Examples**: Reference the detailed descriptions in `D8. Core Indices in More Detail` for examples of how to structure index pages for chemicals, endpoints, assays, datasets, and evidence claims.
5. **Rules**: Follow the `D5.3 Index Seeding Rules` to keep indices concise and navigational.

Use this date for frontmatter: {date_str}
"""
    response = index_tools.invoke(
        [
            SystemMessage(content=reference_files["specs"]),
            SystemMessage(content=reference_files["outline"]),
            HumanMessage(content=prompt),
        ]
    )

    if response.tool_calls:
        return Command(update={"messages": [response]}, goto="index_tools")

    summary = WorkerSummary(
        status="completed",
        details="All information pages created successfully",
        files_created=state.get("index_created", [])
    )

    return Command(
        update = {
        "messages": [HumanMessage(content=str(summary))],
        "node_checklist": {**state.get("node_checklist", {}), "index_pages": True},
        },
        goto="supervisor",
    )

def index_tools_node(state: WikiSeedState) -> Command:
    tool_node = _tool_node([upsert_file])
    result = tool_node.invoke(state)
    files = _collect_tool_files(result, "index_created")

    # Generate summary
    summary = WorkerSummary(
        status="completed",
        details=f"Created {len(files)} Index pages",
        files_created=files
    )

    return Command(
        update={
            "messages": [HumanMessage(content=str(summary))],
            "index_created": files,
            "node_checklist": {**state.get("node_checklist", {}), "index_pages": True},
        },
        goto="supervisor",
    )
# ==============================
def _collect_tool_files(state, field: str) -> list[dict]:
    found = list(state.get(field, []))
    for message in state.get("messages", []):
        if getattr(message, "type", None) != "tool":
            continue
        try:
            content = message.content
            # Handle both string JSON and already-parsed objects
            if isinstance(content, str):
                result = json.loads(content)
            else:
                result = content

            # Skip if result is a list (from search_ingestion)
            if isinstance(result, list):
                continue

            file_info = result.get("file")
            if result.get("status") == "success" and file_info and file_info not in found:
                found.append(file_info)
        except (TypeError, json.JSONDecodeError):
            continue
    return found

def info_tools_node(state: WikiSeedState) -> Command:
    tool_node = _tool_node([upsert_file])
    result = tool_node.invoke(state)
    files = _collect_tool_files(result, "info_created")

    # Generate summary
    summary = WorkerSummary(
        status="completed",
        details=f"Created {len(files)} Info pages",
        files_created=files
    )

    return Command(
        update={
            "messages": [HumanMessage(content=str(summary))],
            "info_created": files,
            "node_checklist": {**state.get("node_checklist", {}), "info_pages": True},
        },
        goto="supervisor",
    )

def _tool_node(tools):
    # Imported lazily so the main graph definition stays easy to read.
    from langgraph.prebuilt import ToolNode

    return ToolNode(tools)


# --------- BUILD WORKFLOW ---------------
def build_graph():
    workflow = StateGraph(WikiSeedState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("docusaurus", docusaurus_node)
    workflow.add_node("docusaurus_tools", docusaurus_tools_node)
    workflow.add_node("index_pages", index_node)
    workflow.add_node("index_tools", index_tools_node)

    workflow.add_edge(START, "supervisor")

    return workflow.compile()

def initial_state() -> WikiSeedState:
    return {
        "messages": [
            HumanMessage(content="Create the Docusaurus-compatible wiki on computational toxicology.")
        ],
        "docusaurus_created": [],
        "info_created": [],
        "info_active_page": None,
        "core_created": [],
        "core_active_page": None,
        "index_created": [],
        "node_checklist": {"docusaurus": True, "info_pages": True, "core_pages": False, "index_pages": False},
        "task_description": "",
    }

if __name__ == "__main__":
    app = build_graph()
    app.invoke(initial_state())