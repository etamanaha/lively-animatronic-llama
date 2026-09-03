from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from graph import app


def check_api_keys() -> bool:
    if not os.getenv("OPENAI_API_KEY"):
        print("API key NOT found. Set OPENAI_API_KEY in your .env file.")
        return False
    return True


def main() -> None:
    load_dotenv()
    if not check_api_keys():
        return

    print("AOP Literature Research Assistant")
    print("=" * 50)

    query = input("\nEnter your research topic: ").strip()
    if not query:
        print("Please enter a research topic.")
        return

    target_text = input("Number of articles to download (default 3): ").strip()
    target_articles = int(target_text) if target_text.isdigit() and int(target_text) > 0 else 3

    limit_text = input("Recursion limit (default 20): ").strip()
    recursion_limit = int(limit_text) if limit_text.isdigit() and int(limit_text) > 0 else 20

    initial_state = {
        "query": query,
        "output_dir": "research_output",
        "target_articles": target_articles,
        "research_findings": [],
        "article_summaries": [],
        "draft": "",
        "report_path": "",
        "researcher_complete": False,
        "summarizer_complete": False,
        "writer_complete": False,
    }

    config = {"recursion_limit": recursion_limit}
    final_state = dict(initial_state)
    step = 0

    try:
        for update in app.stream(initial_state, config=config):
            step += 1
            node_name, node_output = next(iter(update.items()))
            node_output = node_output or {}
            final_state.update(node_output)
            print(f"\n--- Step {step}: {node_name.upper()} ---")

            if node_name == "supervisor":
                print(f"Next: {node_output.get('next_step', 'unknown')}")
                print(f"Task: {node_output.get('current_sub_task', '')}")
            elif node_name == "researcher":
                findings = node_output.get("research_findings", [])
                print(f"Downloaded/retrieved: {len(findings)} article(s)")
            elif node_name == "summarizer":
                summaries = node_output.get("article_summaries", [])
                print(f"Created: {len(summaries)} article summary/ies")
            elif node_name == "writer":
                print(f"Report: {node_output.get('report_path', '(not saved)')}")
                print(f"Draft length: {len(node_output.get('draft', ''))} characters")

    except Exception as exc:
        print(f"\nWorkflow error: {exc}")
        return

    print("\n" + "=" * 50)
    print("WORKFLOW COMPLETE")
    print("=" * 50)
    print(f"Articles: {len(final_state.get('research_findings', []))}")
    print(f"Summaries: {len(final_state.get('article_summaries', []))}")
    print(f"Report: {final_state.get('report_path', '(not saved)')}")

    draft = final_state.get("draft", "")
    if draft and not final_state.get("report_path"):
        output_path = Path("research_report.md")
        output_path.write_text(draft, encoding="utf-8")
        print(f"Draft saved to: {output_path}")


if __name__ == "__main__":
    main()
