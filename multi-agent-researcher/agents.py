
from typing import Any, TypedDict, Literal
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, ToolMessage
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pathlib import Path
import yaml
import os
import re
import json
from prompts import (
    SUPERVISOR_PROMPT,
    RESEARCHER_PROMPT,
    ARTICLE_SUMMARIZER_PROMPT,
    WRITER_PROMPT
)

from europepmc_api_researcher import search_europepmc, get_fulltext

# Load environment variables
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="devstral-small", temperature=0.2) 

class SupervisorDecision(BaseModel):
    next_step: Literal["researcher", "summarizer", "writer", "END"]
    task_description: str = Field(description="The next action to perform")

def safe_filename(value: Any, fallback: str) -> str:
    text = as_text(value).strip()
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._")
    return (text[:120] or fallback)

def save_fulltext(
    result: Any,
    identifier: dict[str, Any],
    output_dir: str,
    index: int,
) -> str:
    """Save full text returned as either a path or article text."""
    articles_dir = Path(output_dir) / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    pmcid = identifier.get("pmcid") or identifier.get("pmid") or identifier.get("doi")
    stem = safe_filename(pmcid, f"article_{index:02d}")
    output_path = articles_dir / f"{stem}.txt"

    result_text = as_text(result).strip()

    # If the tool returned an existing file path, copy its contents.
    try:
        returned_path = Path(result_text)
        if "\n" not in result_text and returned_path.is_file():
            text = returned_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        else:
            text = result_text
    except OSError:
        # Long article text is not a valid filename.
        text = result_text

    output_path.write_text(text, encoding="utf-8")
    return str(output_path)

def as_text(value: Any, limit: int | None = None) -> str:
    """Convert a tool/model value to text, optionally truncating it."""
    if isinstance(value, ToolMessage):
        value = value.content
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, default=str)

    if limit is not None and len(value) > limit:
        return value[:limit] + "\n[tool output truncated]"

    return value

def fulltext_for_summary(article: dict[str, Any]) -> str:
    """Read article text from the saved path or fall back to inline text."""
    saved_path = article.get("fulltext_path")

    if saved_path:
        try:
            path = Path(str(saved_path))
            if path.is_file():
                return path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
        except OSError:
            pass

    return as_text(article.get("fulltext_result", ""))

def save_markdown_report(
    content: str,
    output_dir: str = "research_output",
) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_path = output_path / "research_report.md"
    report_path.write_text(content, encoding="utf-8")

    return str(report_path)

def create_supervisor_chain():

    def supervisor_invoke(state) -> dict[str, Any]:
        findings = state.get("research_findings", [])
        summaries = state.get("article_summaries", [])
        target = state.get("target_articles", 3)
        research_complete = state.get("researcher_complete", False)
        writer_complete = state.get("writer_complete", False)
        summary_ids = {as_text(item.get("article_key")) for item in summaries}
        finding_ids = {
            as_text(item.get("article_key") or item.get("identifier"))
            for item in findings
        }
        missing_summaries = bool(finding_ids - summary_ids)

        if writer_complete:
            decision = SupervisorDecision(next_step="END", task_description="Workflow complete.")
        elif not research_complete or len(findings) < target:
            decision = SupervisorDecision(
                next_step="researcher",
                task_description="Find and download more relevant full-text articles.",
            )
        elif missing_summaries:
            decision = SupervisorDecision(
                next_step="summarizer",
                task_description="Create one summary for each downloaded article.",
            )
        else:
            decision = SupervisorDecision(
                next_step="writer",
                task_description="Write the overall report from the article summaries.",
            )

        # The model sees state for observability, but deterministic guards control routing.
        return decision.model_dump()

    return supervisor_invoke


def create_researcher_agent():
    researcher_llm = llm.bind_tools([search_europepmc, get_fulltext])
    search_name = search_europepmc.name
    fulltext_name = get_fulltext.name

    def researcher_invoke(state) -> dict[str, Any]:
        query = state.get("query", "")
        output_dir = state.get("output_dir", "research_output")

        messages = [
            SystemMessage(content=RESEARCHER_PROMPT),
            HumanMessage(content=f"Research question:\n{query}"),
        ]

        records: list[dict[str, Any]] = []
        searched = False
        downloads = 0
        target = state.get("target_articles", 3)

        for _ in range(8):
            response = researcher_llm.invoke(messages)
            messages.append(response)

            calls = getattr(response, "tool_calls", []) or []
            if not calls:
                break

            for call in calls:
                name = call["name"]
                args = call.get("args", {}) or {}

                if name == search_name:
                    if searched:
                        result = "Search already completed. Use the existing results."
                    else:
                        searched = True
                        result = search_europepmc.invoke(args)

                elif name == fulltext_name:
                    if downloads >= target:
                        result = "Download target reached."
                    else:
                        result = get_fulltext.invoke(args)

                        saved_path = save_fulltext(
                            result=result,
                            identifier=args,
                            output_dir=output_dir,
                            index=downloads + 1,
                        )

                        article_key = (
                            args.get("pmcid")
                            or args.get("pmid")
                            or args.get("doi")
                            or f"article_{downloads + 1}"
                        )

                        records.append({
                            "article_key": as_text(article_key),
                            "identifier": args,
                            "fulltext_path": saved_path,
                        })

                        downloads += 1

                else:
                    result = f"Unsupported tool: {name}"

                messages.append(
                    ToolMessage(
                        content=as_text(result, 8000),
                        tool_call_id=call["id"],
                        name=name,
                    )
                )

            if downloads >= target:
                break

        return {
            "research_findings": records,
            "researcher_complete": downloads >= target,
        }

    return researcher_invoke

def create_summarizer_agent():
    """Summarize each downloaded article in a separate LLM call."""
    def summarizer_invoke(state) -> dict[str, Any]:
        existing = {
            as_text(item.get("article_key")): item
            for item in state.get("article_summaries", [])
        }
        summaries = list(existing.values())

        for article in state.get("research_findings", []):
            article_key = as_text(article.get("article_key") or article.get("identifier"))
            if article_key in existing:
                continue

            fulltext = fulltext_for_summary(article)
            response = llm.invoke([
                SystemMessage(content=ARTICLE_SUMMARIZER_PROMPT),
                HumanMessage(content=json.dumps({
                    "query": state.get("query", ""),
                    "article_identifier": article.get("identifier"),
                    "full_text": fulltext,
                }, ensure_ascii=False)),
            ])
            summary = response.content if isinstance(response.content, str) else str(response.content)
            summaries.append({
                "article_key": article_key,
                "identifier": article.get("identifier"),
                "summary": summary,
                "fulltext_result": article.get("fulltext_result"),
            })

        return {
            "article_summaries": summaries,
            "summarizer_complete": True,
        }

    return summarizer_invoke

def create_writer_agent():
    def writer_invoke(state) -> dict[str, Any]:
        payload = {
            "query": state.get("query", ""),
            "article_summaries": state.get("article_summaries", []),
        }

        response = llm.invoke([
            SystemMessage(content=WRITER_PROMPT),
            HumanMessage(
                content=json.dumps(
                    payload,
                    indent=2,
                    ensure_ascii=False,
                )
            ),
        ])

        draft = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )

        report_path = save_markdown_report(
            content=draft,
            output_dir=state.get("output_dir", "research_output"),
        )

        return {
            "draft": draft,
            "report_path": report_path,
            "writer_complete": True,
        }

    return writer_invoke