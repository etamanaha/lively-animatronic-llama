from __future__ import annotations
from pathlib import Path
from langchain_core.tools import tool
import json
import re
from lxml import etree
import urllib.parse
from polite_http import http_client

API_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
API_CLIENT = http_client.HttpClient(API_BASE, qps=1.0,)

DROP_TAGS = {
    "ref-list", "fig", "table-wrap", "table", "supplementary-material",
    "supplementary-materials", "media", "graphic", "inline-graphic",
    "disp-formula", "inline-formula", "chem-struct-wrap", "code",
    "permissions", "funding-group", "ack", "acknowledgments",
}

def _local_name(tag) -> str:
    # Comments and processing instructions have callable .tag values in lxml.
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _first_text(root: etree._Element, xpath: str) -> str:
    nodes = root.xpath(xpath)
    return _clean_text("".join(nodes[0].itertext())) if nodes else ""


def _attribute(element: etree._Element, name: str) -> str:
    """Read an attribute whether or not it is namespace-qualified."""
    for key, value in element.attrib.items():
        if _local_name(key) == name:
            return value or ""
    return ""


def _author_name(contrib: etree._Element) -> str:
    """Extract a readable author name from common JATS author layouts."""
    name = contrib.xpath("./*[local-name()='name']")
    if name:
        node = name[0]
        surname = _first_text(node, "./*[local-name()='surname']")
        given = _first_text(node, "./*[local-name()='given-names']")
        prefix = _first_text(node, "./*[local-name()='prefix']")
        suffix = _first_text(node, "./*[local-name()='suffix']")
        if surname or given:
            parts = [x for x in (prefix, given, surname, suffix) if x]
            # Keep the existing citation format: surname, given names.
            if surname and given:
                result = f"{surname}, {given}"
                if prefix:
                    result = f"{prefix} {result}"
                if suffix:
                    result = f"{result}, {suffix}"
                return result
            return " ".join(parts)

    # Some publishers use string-name instead of name/surname/given-names.
    string_name = contrib.xpath(
        "./*[local-name()='string-name'] | "
        "./*[local-name()='name-alternatives']/*[local-name()='string-name']"
    )
    if string_name:
        value = _clean_text("".join(string_name[0].itertext()))
        if value:
            return value

    # Group authors are represented with collab rather than personal names.
    collab = _first_text(contrib, "./*[local-name()='collab']")
    if collab:
        return collab

    # Last fallback for unusual but valid JATS contributor markup.
    return _clean_text("".join(contrib.itertext()))


def _extract_authors(meta: etree._Element) -> list[str]:
    contributors = meta.xpath(".//*[local-name()='contrib']")
    author_contributors = [
        c for c in contributors
        if _attribute(c, "contrib-type").lower() == "author"
    ]

    # A few JATS documents omit contrib-type. Only use those records if no
    # explicitly identified authors were found, avoiding editors/reviewers.
    if not author_contributors:
        author_contributors = [
            c for c in contributors
            if not _attribute(c, "contrib-type")
        ]

    authors = []
    for contrib in author_contributors:
        name = _author_name(contrib)
        if name and name not in authors:
            authors.append(name)
    return authors


def _extract_citation(root: etree._Element, pmcid: str) -> dict:
    article_meta = root.xpath(".//*[local-name()='article-meta']")
    meta = article_meta[0] if article_meta else root

    title = _first_text(meta, "./*[local-name()='title-group']/*[local-name()='article-title']")
    if not title:
        title = _first_text(root, ".//*[local-name()='article-title']")

    authors = _extract_authors(meta)

    year = ""
    for date_path in (
        "./*[local-name()='pub-date'][@pub-type='epub']/*[local-name()='year']",
        "./*[local-name()='pub-date']/*[local-name()='year']",
        "./*[local-name()='history']//*[local-name()='date']/*[local-name()='year']",
    ):
        year = _first_text(meta, date_path)
        if year:
            break

    doi = ""
    for node in meta.xpath(".//*[local-name()='article-id'][@pub-id-type='doi']"):
        doi = _clean_text("".join(node.itertext()))
        if doi:
            break
    if not doi:
        doi = _first_text(meta, ".//*[local-name()='pub-id'][@pub-id-type='doi']")

    url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    # Match href by local name; this avoids requiring an xlink namespace map.
    self_uri = meta.xpath(
        ".//*[local-name()='self-uri']/@*[local-name()='href']"
    )
    if self_uri:
        url = self_uri[0]

    license_text = _first_text(meta, ".//*[local-name()='license']")
    access_status = (
        "open_access"
        if license_text or pmcid.upper().startswith("PMC")
        else "unknown"
    )

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "url": url,
        "access_status": access_status,
    }


def _remove_unnecessary(root: etree._Element) -> None:
    for node in list(root.iter()):
        name = _local_name(node.tag)
        if name in DROP_TAGS:
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
        elif name == "xref" and node.get("ref-type") in {"bibr", "fig", "table"}:
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)


def _section_text(sec: etree._Element) -> str:
    parts = []
    title = sec.find("./title")
    if title is not None:
        value = _clean_text("".join(title.itertext()))
        if value:
            parts.append(value)

    for child in sec:
        name = _local_name(child.tag)
        if name == "title":
            continue
        if name == "sec":
            nested = _section_text(child)
            if nested:
                parts.append(nested)
        elif name in {"p", "disp-quote", "list", "def-list"}:
            value = _clean_text("".join(child.itertext()))
            if value:
                parts.append(value)

    return "\n".join(parts)


def _cut_at_boundary(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    candidate = text[:max_chars]
    boundary = max(candidate.rfind("\n"), candidate.rfind(". "))
    if boundary < max_chars // 2:
        boundary = max_chars
    return candidate[:boundary].rstrip() + "\n[content truncated]"


def compact_fulltext(xml: str, max_chars: int = 30000) -> dict:
    parser = etree.XMLParser(
        load_dtd=False,
        resolve_entities=False,
        no_network=True,
        recover=True,
        huge_tree=True,
    )
    root = etree.fromstring(xml.encode("utf-8"), parser)
    citation = _extract_citation(root, pmcid="")
    _remove_unnecessary(root)

    chunks = []
    if citation["title"]:
        chunks.append(citation["title"])

    for abstract in root.xpath(".//*[local-name()='abstract']"):
        value = _clean_text("".join(abstract.itertext()))
        if value:
            chunks.append("Abstract\n" + value)

    body = root.find(".//body")
    found_conclusion = False
    if body is not None:
        for sec in body.xpath("./*[local-name()='sec']"):
            text = _section_text(sec)
            if text:
                chunks.append(text)
            title = sec.find("./title")
            title_text = _clean_text("".join(title.itertext())) if title is not None else ""
            if re.search(r"\b(conclusion|conclusions)\b", title_text, re.I):
                found_conclusion = True
                break

    result = _cut_at_boundary("\n\n".join(chunks), max_chars)
    if found_conclusion and not result.endswith("[content truncated]"):
        result += "\n[stopped after conclusion]"
    return {"citation": citation, "fulltext": result}


@tool
def get_fulltext(pmcid: str) -> dict:
    """Retrieve compacted open-access article text plus citation metadata."""
    xml_fulltext = API_CLIENT.fetch_text(f"{pmcid}/fullTextXML", timeout=60)
    data = compact_fulltext(xml_fulltext, max_chars=30000)
    data["citation"]["url"] = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    data["citation"]["access_status"] = "open_access"
    return data

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