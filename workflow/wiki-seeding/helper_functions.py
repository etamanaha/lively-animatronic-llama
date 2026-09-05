from langchain_core.tools import tool
from pathlib import Path
import json
import yaml
from typing import Any

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()

llm = ChatOpenAI(
    model=os.environ["OPENAI_MODEL"],
    temperature=0.2,
    streaming=True, 
    stream_chunk_timeout=300, 
    timeout=800,
    stream_usage=True)

reference_files = {
    "categories": Path("../../reference-md/wiki/top-level-categories.md").read_text(),
    "specs": Path("../../reference-md/wiki/specs.md").read_text(),
    "page-template": Path("../../reference-md/wiki/page-template-examples.md").read_text(),
    "outline": Path("../../reference-md/wiki/wiki-seed-outline.md").read_text(),
    "overview": Path("../../reference-md/wiki/wiki-seed-overview.md").read_text(),
    "checklist": Path("../../reference-md/wiki/wiki-seed-checklist.md").read_text(),
    "docusaurus_prompt": Path("./prompts/docusaurus_prompt.md").read_text(),
    "supervisor_prompt": Path("./prompts/supervisor_prompt.md").read_text(),
    "info_prompt": Path("./prompts/info_prompt.md").read_text(),
    "core_prompt": Path("./prompts/core_prompt.md").read_text(),
}

DOCS_ROOT = Path("../../wiki/docs").resolve()

def safe_path(path: str) -> Path:
    if not path or not path.strip():
        raise ValueError("A file path is required")

    path_text = path.replace("\\", "/").strip().lstrip("/")
    for prefix in ("wiki/docs/", "wiki/", "docs/"):
        if path_text.startswith(prefix):
            path_text = path_text[len(prefix):]
            break

    candidate = (DOCS_ROOT / path_text).resolve()
    try:
        candidate.relative_to(DOCS_ROOT)
    except ValueError as exc:
        raise ValueError(f"Unsafe path: {path}") from exc
    return candidate

@tool
def upsert_file(file_path: str, content: str) -> str:
    """Create or replace a UTF-8 text file inside wiki/docs."""
    try:
        target = safe_path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

        # Return structured data with file info
        relative_path = str(target.relative_to(DOCS_ROOT))
        print("page created:", file_path)
        return json.dumps({
            "status": "success",
            "message": f"created {relative_path}",
            "file": {
                "name": Path(file_path).name,
                "path": relative_path
            }
        })
    except Exception as exc:
        return json.dumps({
            "status": "error",
            "message": str(exc)
        })

@tool
def read_file(path: str) -> str:
    """Read one text file inside wiki/docs."""
    file_path = safe_path(path)

    if not file_path.exists():
        return json.dumps(
            {"path": path, "exists": False, "content": ""},
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "path": file_path.relative_to(DOCS_ROOT).as_posix(),
            "exists": True,
            "content": file_path.read_text(encoding="utf-8"),
        },
        ensure_ascii=False,
    )

def get_section_after_header(file_path: str, header: str) -> str:
    """Get all content after a specific header within a file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
        in_target_section = False
        section_content = []

        # Determine the header level of our target
        target_level = header.count('#')

        for line in lines:
            stripped_line = line.strip()

            if stripped_line == header:
                in_target_section = True
                section_content.append(line)  # Include the header line
                continue
            elif in_target_section and stripped_line.startswith('#'):
                # Stop at next header of same level that is a section header
                current_level = stripped_line.count('#')
                if current_level == target_level:
                    # Check if this is a section header (pattern: ## `something`)
                    if '`' in stripped_line:
                        break
                    # If not a section header, include it and continue
                    section_content.append(line)
            elif in_target_section:
                section_content.append(line)

        return ''.join(section_content)

category_path = "../../reference-md/wiki/top-level-categories.md"
template_path = "../../reference-md/wiki/page-template-examples.md"

def optional_section(file_path: str, header: str) -> str:
    """Return a section when present; otherwise return an empty string."""
    try:
        return get_section_after_header(file_path, header).strip()
    except ValueError:
        return ""

def page_specific_references(page: dict) -> tuple[str, str]:
    """Load only the category and page-type template needed for this page."""
    page_type = str(page["page_type"]).strip()
    page_path = Path(str(page["path"]))
    folder_name = page_path.parent.name

    category_text = optional_section(category_path, f"### `{folder_name}`")
    template_text = optional_section(template_path, f"## `{page_type}`")
    return category_text, template_text

# VERIFICATION
def _read_frontmatter(path: Path) -> dict[str, Any]:
    """Read YAML frontmatter without failing on pages that have none."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else {}


def _page_record(path: Path, docs_root: Path) -> dict[str, Any]:
    """Create a wiki-page record using a reliable relative path."""
    relative_path = path.relative_to(docs_root).as_posix()
    metadata = _read_frontmatter(path)

    return {
        "path": relative_path,
        "title": metadata.get("title", path.stem.replace("-", " ").title()),
        "content": path.read_text(encoding="utf-8"),
        "page_type": metadata.get("page_type", "wiki"),
        "category": metadata.get("category", path.parent.name),
        "reasoning": metadata.get("reasoning", "Existing wiki page loaded for verification."),
    }


def _collect_markdown(
    docs_root: Path,
    category: str,
) -> list[dict[str, Any]]:
    category_root = docs_root / category
    if not category_root.exists():
        return []

    return [
        _page_record(filepath, docs_root)
        for filepath in sorted(category_root.rglob("*.md"))
        if filepath.is_file()
    ]


def _collect_docusaurus_files(wiki_root: Path) -> list[dict[str, Any]]:
    patterns = (
        "intro.md",
        "docusaurus.config.js",
        "docusaurus.config.ts",
        "package.json",
        "sidebars.js",
        "sidebars.ts",
        "sidebars/*.js",
        "sidebars/*.ts",
        "src/css/custom.css",
        "**/_category_.json",
    )

    files: list[dict[str, Any]] = []
    seen: set[Path] = set()

    for pattern in patterns:
        for filepath in sorted(wiki_root.glob(pattern)):
            if not filepath.is_file() or filepath in seen:
                continue

            seen.add(filepath)
            files.append({
                "path": filepath.relative_to(wiki_root).as_posix(),
                "title": filepath.name,
                "content": filepath.read_text(encoding="utf-8"),
                "page_type": "docusaurus",
                "category": filepath.parent.name,
            })

    return files


def populate_empty_state_with_wiki_pages(
    state: dict[str, Any],
    wiki_root: str | Path = "wiki",
    docs_root: str | Path | None = None,
) -> dict[str, Any]:
    """Populate every missing or empty page list independently.

    Existing non-empty lists are preserved. Missing keys and empty lists are
    populated from the current wiki on disk.
    """
    wiki_root = Path(wiki_root)
    docs_root = Path(docs_root) if docs_root else wiki_root / "docs"
    populated = dict(state)

    content_collectors = {
        "info_created": lambda: _collect_markdown(docs_root, "info"),
        "core_created": lambda: _collect_markdown(docs_root, "core"),
        "index_created": lambda: _collect_markdown(docs_root, "index"),
    }

    for field, collector in content_collectors.items():
        if not populated.get(field):
            populated[field] = collector()

    # Docusaurus files are handled separately and not verified
    if not populated.get("docusaurus_created"):
        populated["docusaurus_created"] = []

    return populated


if __name__ == "__main__":
    state = {
        "info_created": [],
        "core_created": [],
        "index_created": [],
        "docusaurus_created": [],
    }
    populated_state = populate_empty_state_with_wiki_pages(state)
    for key in populated_state:
        if key.endswith("_created"):
            print(f"{key}: {len(populated_state[key])}")