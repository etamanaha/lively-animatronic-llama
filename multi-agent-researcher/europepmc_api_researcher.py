from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
from langchain_core.tools import tool
import json
import re
import subprocess
import urllib.parse
from polite_http import http_client

API_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/"

API_CLIENT = http_client.HttpClient(API_BASE, qps=1.0)

@tool
def search_europepmc(
    query: str,
    max_results: int = 10,
    result_type: str = "core",
    sort: str = "",
    output_file: str = "/tmp/europepmc_search_results.json",
) -> str:
    """Search Europe PMC and return the results as a JSON string."""
    # Enforce open-access only
    if "OPEN_ACCESS:" not in query.upper():
        query = f"({query}) AND OPEN_ACCESS:y"

    params = {
        "query": query,
        "format": "json",
        "resultType": result_type,
        "pageSize": min(max_results, 1000),
        "cursorMark": "*",
    }
    if sort:
        params["sort"] = sort

    try:
        data = API_CLIENT.fetch_json(f"search?{urllib.parse.urlencode(params)}")
        results = data.get("resultList", {}).get("result", [])
        hit_count = data.get("hitCount", 0)
        next_cursor = data.get("nextCursorMark", "")

        output_data = {
            "hitCount": hit_count,
            "nextCursorMark": next_cursor,
            "results": results[:max_results],
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")

        return output_path.read_text(encoding="utf-8")
    except Exception as exc:
        return json.dumps({"error": str(exc)})

def _extract_all_text(elem: ET.Element) -> str:
    parts = [elem.text or ""]
    for child in elem:
        parts.append(_extract_all_text(child))
        parts.append(child.tail or "")
    return "".join(parts)

def _xml_to_plain_text(xml_string: str) -> str:
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml_string)).strip()

    sections: list[str] = []
    title = root.find(".//article-title")
    if title is not None:
        sections.append(f"# {_extract_all_text(title).strip()}")

    for abstract in root.findall(".//abstract"):
        text = _extract_all_text(abstract).strip()
        if text:
            sections.append(f"## Abstract\n\n{text}")

    body = root.find(".//body")
    if body is not None:
        parts: list[str] = []
        for elem in body.iter():
            tag = elem.tag.split("}")[-1]
            if tag == "title":
                text = _extract_all_text(elem).strip()
                if text:
                    parts.append(f"\n## {text}\n")
            elif tag == "p":
                text = _extract_all_text(elem).strip()
                if text:
                    parts.append(text)
        sections.append("\n\n".join(parts))

    return "\n\n".join(sections)

@tool
def get_fulltext(pmcid: str, fmt: str = "text") -> str:
    """Retrieve open-access article full text by PMCID."""
    url = f"{pmcid}/fullTextXML"
    xml_content = API_CLIENT.fetch_text(url, timeout=60)
    if fmt == "xml":
        return xml_content
    return _xml_to_plain_text(xml_content)

