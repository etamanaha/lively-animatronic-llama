# agents.py
from typing import Dict, Any
from datetime import datetime, timezone
import yaml
import os
import json
import subprocess
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from prompts import (
    supervisor_prompt_template,
    researcher_prompt_template,
    writer_prompt_template,
    critique_prompt_template
)

# Load environment variables
load_dotenv()
import os

# --- 1. Setup LLM and Tools ---

# Initialize LLM 
llm = ChatOpenAI(model="devstral-small", temperature=0.1) # CHANGE

def _call_llm(llm_obj, *args, **kwargs):
    """Helper to call LLM or tool objects that may expose different APIs.

    Tries common method names in order: invoke, run, __call__.
    This increases compatibility across LangChain versions.
    """
    # prefer invoke
    if hasattr(llm_obj, "invoke") and callable(getattr(llm_obj, "invoke")):
        return llm_obj.invoke(*args, **kwargs)
    # fallback to run
    if hasattr(llm_obj, "run") and callable(getattr(llm_obj, "run")):
        return llm_obj.run(*args, **kwargs)
    # last resort: call object directly if callable
    if callable(llm_obj):
        return llm_obj(*args, **kwargs)
    # Not callable
    raise AttributeError("LLM/tool object has no invoke/run and is not callable")

# SEARCH EUROPEPMC
def search_europepmc(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search Europe PMC for scientific literature"""
    print("search_europepmc called")
    output_file = "/tmp/europepmc_search_results.json"

    cmd = [
        "uv", "run",
        "../skills/literature-search-europepmc/scripts/europepmc_api.py",
        "search",
        query,
        "--max_results", str(max_results),
        "--result_type", "core",
        "--output", output_file
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        with open(output_file, 'r') as f:
            results = json.load(f)

        return results

    except subprocess.CalledProcessError as e:
        print(f"Error searching EuropePMC: {e.stderr}")
        return {"error": str(e.stderr), "results": []}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e), "results": []}

# GET FULLTEXT
def get_europepmc_fulltext(pmcid: str, fmt: str = "text") -> Dict[str, Any]:
    """
    Retrieve full text of an article by PMCID from Europe PMC.

    Args:
        pmcid: PubMed Central ID (e.g., "PMC8371605")
        fmt: Output format - "text" (plain text) or "xml" (raw XML)

    Returns:
        Dictionary with:
        - pmcid: the requested PMCID
        - fulltext: the retrieved text content
        - error: error message if retrieval failed (None if successful)
        - has_fulltext: boolean indicating if full text was available
    """
    if not pmcid or not pmcid.startswith("PMC"):
        return {
            "pmcid": pmcid,
            "fulltext": "",
            "error": f"Invalid PMCID: {pmcid}",
            "has_fulltext": False
        }

    print("retrieving full text")
    output_file = f"/tmp/europepmc_fulltext_{pmcid.replace('PMC', '')}.txt"
    cmd = [
        "uv", "run",
        "../skills/literature-search-europepmc/scripts/europepmc_api.py",
        "get_fulltext",
        pmcid,
        "--format", fmt,
        "--output", output_file
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=120  # Extended timeout for full text retrieval
        )

        # Check if the command succeeded
        if result.returncode == 0:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    fulltext = f.read()
                return {
                    "pmcid": pmcid,
                    "fulltext": fulltext,
                    "error": None,
                    "has_fulltext": True
                }
            except (OSError, IOError) as e:
                return {
                    "pmcid": pmcid,
                    "fulltext": "",
                    "error": f"Error reading output file: {str(e)}",
                    "has_fulltext": False
                }
        else:
            # Command failed - check stderr for details
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return {
                "pmcid": pmcid,
                "fulltext": "",
                "error": f"Full text retrieval failed: {error_msg}",
                "has_fulltext": False
            }

    except subprocess.TimeoutExpired:
        return {
            "pmcid": pmcid,
            "fulltext": "",
            "error": "Timeout: Full text retrieval took too long",
            "has_fulltext": False
        }
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else f"Process failed with code {e.returncode}"
        return {
            "pmcid": pmcid,
            "fulltext": "",
            "error": f"Subprocess error: {error_msg}",
            "has_fulltext": False
        }
    except Exception as e:
        return {
            "pmcid": pmcid,
            "fulltext": "",
            "error": f"Unexpected error: {str(e)}",
            "has_fulltext": False
        }

"""
def select_top_articles(results: list, query: str, num_top: int = 5) -> list:

    Select top N articles from search results using LLM-assisted ranking.

    Args:
        results: List of article metadata from Europe PMC
        query: Original search query
        num_top: Number of top articles to select

    Returns:
        List of top articles with ranking scores

    if len(results) <= num_top:
        return results

    # Create ranking prompt for LLM
    ranking_prompt = 
    You are an expert research assistant. Please rank these {len(results)} scientific articles
    based on their relevance to the query: "{query}".

    For each article, consider:
    1. Relevance to the query topic
    2. Recency (newer articles may be more relevant)
    3. Author reputation (if available)
    4. Journal impact (if available)
    5. Availability of full text (articles with PMCID are preferred)

    Format your response as JSON with an array of objects, each containing:
    - "index": the original index (0-based)
    - "score": relevance score (0-10, higher is better)
    - "reason": brief explanation for the score

    Articles:
    {json.dumps(results, indent=2)}

    Return only the JSON array, no other text.


    try:
        response = _call_llm(llm, ranking_prompt)
        content = response.content if hasattr(response, 'content') else str(response)

        # Extract JSON from response
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join([l for l in lines if not l.strip().startswith("```")])
        content = content.strip()

        rankings = json.loads(content)

        # Sort by score and select top N
        rankings.sort(key=lambda x: x['score'], reverse=True)
        top_indices = [r['index'] for r in rankings[:num_top]]

        # Return top articles with their ranking info
        return [{
            **results[idx],
            "ranking_score": rankings[i]['score'],
            "ranking_reason": rankings[i]['reason']
        } for i, idx in enumerate(top_indices)]

    except Exception as e:
        print(f"LLM ranking failed, using fallback: {e}")
        # Fallback: sort by publication date (newest first)
        return sorted(
            results,
            key=lambda x: x.get('pubYear', 0),
            reverse=True
        )[:num_top]
"""
    
# --- 2. Create Agent Nodes ---

SELECTION_PROMPT = """
You are an expert research assistant. Below is a list of scientific articles from Europe PMC.

Research query: "{query}"
Numder of articles: {total}

Your task is tank these articles from 1 (best) to {total} (worst), prioritizing relevance to the research query over general subject-matter similarity.

## How to assess relevance

1. Decompose the research query into its key concepts:
    - Population or biolo

1. Relevance to the research query: "{query}"
2. Publication date (more recent is generally better, but foundational work matters)
3. Citation count (higher citations indicatw impact)
4. Availabiity of full text (articles with PMCID are preferred)
5. Journal quality and reputation

Format your response as JSON with this structure:
{{
  "ranked_articles": [
    {{
      "rank": 1,
      "pmcid": "PMC123456",
      "reason": "Most relevant and recent with high citation count"
    }},
    ...
  ],
  "top_5": ["PMC123456", "PMC789012", ...]  # List of top 5 PMCIDs
}}

Articles to rank:
{article_list}

Important: Only include articles that have a PMCID in the top 5, as these are the only ones with full text available.
"""
# ----------------- #
# SUPERVISOR NODE   #
# ----------------- #
def create_supervisor_chain():
    """Creates the supervisor decision chain."""
    def supervisor_invoke(state):
        research = state.get("research_findings", [])
        research_text = "\n---\n".join(research) if research else "No research yet."
        
        # Get state info
        revision = state.get("revision_number", 0)
        has_research = len(research) > 0
        has_draft = bool(state.get("draft", "").strip())
        critique = state.get("critique_notes", "")
        
        # Deterministic decision logic FIRST (before calling LLM)
        # This ensures consistent workflow progression
        
        # 1. If critique says APPROVED, we're done
        if "APPROVED" in critique.upper() and has_draft:
            print("Supervisor: Draft approved, ending workflow")
            return {
                "next_step": "END",
                "task_description": "Report approved and complete"
            }
        
        # 2. If no research yet, start with research
        if not has_research:
            print("Supervisor: No research yet, directing to researcher")
            return {
                "next_step": "researcher",
                "task_description": f"Research the topic: {state.get('main_task', '')}"
            }
        
        # 3. If we have research but no draft, create first draft
        if has_research and not has_draft:
            print("Supervisor: Have research, creating first draft")
            return {
                "next_step": "writer",
                "task_description": "Write the first draft based on research findings"
            }
        
        # 4. If we have a draft but no critique yet, send to critiquer
        if has_draft and not critique:
            print("Supervisor: Have draft, sending to critiquer")
            return {
                "next_step": "writer",  # This will trigger write -> critique flow
                "task_description": "Prepare draft for critique"
            }
        
        # 5. If we have critique with feedback (not approved), revise
        if critique and "APPROVED" not in critique.upper() and revision < 3:
            print(f"Supervisor: Revision {revision}, sending back to writer")
            return {
                "next_step": "writer",
                "task_description": "Revise the draft based on critique feedback"
            }
        
        # 6. Max revisions reached
        if revision >= 3:
            print("Supervisor: Max revisions reached, ending")
            return {
                "next_step": "END",
                "task_description": "Maximum revisions reached, finalizing report"
            }
        
        # 7. Try LLM decision as fallback
        prompt = supervisor_prompt_template.format(
            main_task=state.get("main_task", ""),
            research_findings=research_text,
            draft=state.get("draft", "No draft yet."),
            critique_notes=critique if critique else "No critique yet.",
            revision_number=revision
        )
        
        try:
            response = _call_llm(llm, prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse JSON
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join([l for l in lines if not l.strip().startswith("```")])
            text = text.strip()
            
            decision = json.loads(text)
            
            if "next_step" in decision:
                return decision
            
        except Exception as e:
            print(f"LLM parsing error: {e}")
        
        # 8. Final fallback - continue with writer
        print("Supervisor: Using final fallback - continuing with writer")
        return {
            "next_step": "writer",
            "task_description": "Continue with draft creation"
        }
    
    return supervisor_invoke

# ----------------- #
# RESEARCHER NODE   #
# ----------------- #

def extract_structured_citations(results):
    """Convert EuropePMC results to wiki-seed citation schema"""
    citations = []
    for idx, result in enumerate(results, 1):
        citation = {
            "citation_id": f"cit-{idx:03d}",
            "source_type": "paper",  # Default, could detect review type
            "title": result.get('title', 'Untitled'),
            "authors": result.get('authorList', {}).get('author', []),
            "year": result.get('pubYear', 'N/A'),
            "container": result.get('journalTitle', 'N/A'),
            "doi": result.get('doi', 'N/A'),
            "url": f"https://europepmc.org/article/MED/{result.get('id', '')}" if result.get('id') else "N/A",
            "access_status": "open_access",  # EuropePMC is open access
            "retrieved_on": datetime.now().strftime("%Y-%m-%d"),
            "notes": "Extracted from Europe PMC database"
        }
        citations.append(citation)
    return citations

def format_citations_yaml(citations: list[dict]) -> str:
    """Format citation records as separate YAML documents according to wiki-seed schema."""
    documents = []

    for citation in citations:
        # Handle authors - ensure they're always a list of strings
        raw_authors = citation.get("authors", [])
        authors = []
        for author in raw_authors:
            if isinstance(author, dict):
                # Extract name from author dict
                name = author.get("name")
                if not name:
                    # Build name from first and last name
                    first = author.get("firstName", "")
                    last = author.get("lastName", "")
                    name = f"{first} {last}".strip()
                if name:
                    authors.append(name)
            elif isinstance(author, str):
                authors.append(author)
            # Skip invalid author entries

        # Build citation record with all required fields
        record = {
            "citation_id": citation.get("citation_id", "N/A"),
            "source_type": citation.get("source_type", "paper"),
            "title": citation.get("title", "Untitled"),
            "authors": authors if authors else ["Unknown"],
            "year": citation.get("year", "N/A"),
            "container": citation.get("container", "N/A"),
            "doi": citation.get("doi", "N/A"),
            "url": citation.get("url", "N/A"),
            "access_status": citation.get("access_status", "open_access"),
            "retrieved_on": citation.get(
                "retrieved_on",
                datetime.now().strftime("%Y-%m-%d"),
            ),
            "notes": citation.get("notes", "Extracted from Europe PMC database"),
        }

        # Convert to YAML and add to documents
        documents.append(yaml.safe_dump(
            record,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        ).rstrip())

    return "\n---\n".join(documents)

def format_as_markdown(content: str, citations: list[dict], main_task: str = "Topic") -> str:
    """Format research output as Markdown with proper structure."""
    if not content:
        return ""
    # Check if content is already a complete markdown document
    if content.strip().startswith("# ") or content.strip().startswith("## "):
        print("--- IT'S ALREADY PROEPRLY FORMATTED --- ")
        print("check for yaml")
        # It's already markdown, just check for yaml
        markdown_lines = content.split('\n')
        # Find where # references is
        end_line = 0
        ref_insert_pos = len(markdown_lines)
        for i, line in enumerate(markdown_lines):
            if i > end_line:
                end_line = i
            if line.strip().lower() in ['## references']:
                ref_insert_pos = i + 1

        # Insert references section
        markdown_lines.insert(ref_insert_pos, "")
        if citations:
            print("if citations")
            markdown_lines.insert(ref_insert_pos + 1, "```yaml")
            #markdown_lines.insert(ref_insert_pos + 2, format_citations_yaml(citations))
            markdown_lines.insert(end_line + 2, "```")
        else:
            print("else")
            markdown_lines.insert(ref_insert_pos + 1, "- No citations available")
        print("markdown lines:", markdown_lines)
        
        return "\n".join(markdown_lines)
    
    else:
        print(" --- PROCESS UNSTRUCTURED TEXT ---")
        # Process as unstructured text
        lines = content.split('\n')
        markdown_lines = []

        # Add title
        markdown_lines.append(f"# Research Report: {main_task}")
        markdown_lines.append("")

        # Add abstract section
        markdown_lines.append("## Abstract")
        abstract = lines[0] if lines else "No abstract available"
        markdown_lines.append(abstract)
        markdown_lines.append("")

        # Add introduction
        markdown_lines.append("## Introduction")
        intro_lines = lines[1:5] if len(lines) > 5 else lines[1:]
        for line in intro_lines:
            if line.strip():
                markdown_lines.append(f"- {line.strip()}")
        markdown_lines.append("")

        # Add key findings
        markdown_lines.append("## Key Findings")
        findings_lines = lines[5:10] if len(lines) > 10 else lines[5:]
        for line in findings_lines:
            if line.strip():
                markdown_lines.append(f"- {line.strip()}")
        markdown_lines.append("")

        # Add conclusion
        markdown_lines.append("## Conclusion")
        markdown_lines.append("- Summary of findings")
        markdown_lines.append("")

        # Add references
        markdown_lines.append("## References")
        if citations:
            markdown_lines.append("```yaml")
            markdown_lines.append(format_citations_yaml(citations))
            markdown_lines.append("```")
        else:
            markdown_lines.append("- No citations available")
        print("markdown lines:", markdown_lines)
        return "\n".join(markdown_lines)

def validate_citations(citations):
    """Validate citations against wiki-seed schema"""
    print("validation function")
    required_fields = [
        'citation_id', 'source_type', 'title', 'authors',
        'year', 'container', 'doi', 'url', 'access_status',
        'retrieved_on', 'notes'
    ]
    for citation in citations:
        for field in required_fields:
            if field not in citation:
                citation[field] = "N/A" if field != 'authors' else []
    return citations

def save_markdown_report(content: str, filename: str = None) -> str:
    """Save Markdown content to file."""
    if not filename:
        # Generate filename from timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/research_report_{timestamp}.md"

    with open(filename, 'w') as f:
        f.write(content)

    print(f"Report saved to: {filename}")
    return filename

def create_researcher_agent():
    """Creates a researcher agent that uses EuropePMC search with full text retrieval"""

    def researcher_invoke(input_dict):
        query = input_dict.get("input", "")
        results = []
        fulltext_results = []

        if not query or query in ["Continue work", "Complete"]:
            query = "General research information"

        try:
            # Step 1: Search for more articles (20 instead of 5)
            print(f"[Researcher] Searching EuropePMC for: {query}")
            search_response = search_europepmc(query, max_results=20)
            results = search_response.get("results", [])
            error = search_response.get("error")

            if error:
                print(f"[Researcher] Search error: {error}")
                return {
                    "output": f"Research failed for: {query}",
                    "input": query,
                    "citations": [],
                    "raw_results": [],
                    "fulltext_used": False
                }

            if not results:
                print("[Researcher] No results found")
                return {
                    "output": "No relevant articles found",
                    "input": query,
                    "citations": [],
                    "raw_results": [],
                    "fulltext_used": False
                }

            # Step 2: Select top 5 articles using LLM
            print(f"[Researcher] Found {len(results)} articles, selecting top 5...")
            article_list = []
            for idx, result in enumerate(results, 1):
                pmcid = result.get("pmcid", "")
                title = result.get("title", "Untitled")
                year = result.get("pubYear", "N/A")
                citations = result.get("citedByCount", 0)
                journal = result.get("journalTitle", "N/A")
                has_fulltext = bool(pmcid)

                article_list.append({
                    "id": idx,
                    "pmcid": pmcid,
                    "title": title,
                    "year": year,
                    "citations": citations,
                    "journal": journal,
                    "has_fulltext": has_fulltext,
                    "abstract": result.get("abstractText", "")[:200] + "..." if result.get("abstractText") else "No abstract"
                })

            print("article_list:", json.dumps(article_list, indent=2))

            # Create selection prompt
            selection_prompt = SELECTION_PROMPT.format(
                total=len(results),
                query=query,
                article_list=json.dumps(article_list, indent=2)
            )

            # Get LLM ranking
            ranking_response = _call_llm(llm, selection_prompt)
            ranking_text = ranking_response.content if hasattr(ranking_response, 'content') else str(ranking_response)

            # Add this before the try block to debug
            print(f"[Researcher] Raw LLM response length: {len(ranking_text)}")
            print(f"[Researcher] Raw LLM response preview: {ranking_text[:200]}")
            print(f"[Researcher] Does response start with ```? {ranking_text.strip().startswith('```')}")

            try:
                # Clean the response text
                text = ranking_text.strip()
                if text.startswith("```"):
                    lines = text.split("\n")
                    text = "\n".join([l for l in lines if not l.strip().startswith("```")])
                text = text.strip()

                # Validate text is not empty
                if not text:
                    raise ValueError("Empty response from LLM")

                # Try to parse JSON
                ranking_data = json.loads(text)
                top_5_pmcids = ranking_data.get("top_5", [])

                # Validate the response structure
                if not isinstance(top_5_pmcids, list):
                    raise ValueError(f"top_5 is not a list, got: {type(top_5_pmcids)}")

                print(f"[Researcher] Selected top articles: {top_5_pmcids}")

            except Exception as e:
                print(f"[Researcher] Failed to parse ranking: {e}")
                print(f"[Researcher] Raw response length: {len(ranking_text)} chars")
                print(f"[Researcher] Raw response preview: {ranking_text[:500]}")

                # Enhanced fallback: select articles with PMCID, prioritizing newer ones
                articles_with_pmcid = [r for r in results if r.get("pmcid")]

                # Sort by publication year (newest first), then by citation count
                articles_with_pmcid.sort(
                    key=lambda x: (
                        -int(x.get("pubYear", 0)) if x.get("pubYear") and str(x.get("pubYear")).isdigit() else 0,
                        -int(x.get("citedByCount", 0)) if x.get("citedByCount") else 0
                    )
                )

                top_5_pmcids = [r.get("pmcid") for r in articles_with_pmcid[:5]]
                print(f"[Researcher] Using fallback selection: {top_5_pmcids}")
            
            # Step 3: Retrieve full text for top 5 articles
            print(f"[Researcher] Retrieving full text for {len(top_5_pmcids)} articles...")
            fulltext_results = []
            for pmcid in top_5_pmcids:
                if not pmcid:
                    continue

                print(f"[Researcher] Getting full text for {pmcid}...")
                fulltext_response = get_europepmc_fulltext(pmcid, fmt="text")

                if fulltext_response.get("has_fulltext"):
                    fulltext_results.append({
                        "pmcid": pmcid,
                        "fulltext": fulltext_response["fulltext"],
                        "article": next((r for r in results if r.get("pmcid") == pmcid), {})
                    })
                else:
                    print(f"[Researcher] No full text for {pmcid}: {fulltext_response.get('error', 'Unknown error')}")
                    # Fallback: use abstract if full text not available
                    article = next((r for r in results if r.get("pmcid") == pmcid), {})
                    if article:
                        fulltext_results.append({
                            "pmcid": pmcid,
                            "fulltext": article.get("abstractText", ""),
                            "article": article,
                            "fallback": True
                        })

            # Step 4: Generate summary using full text
            print("[Researcher] Generating research summary...")

            summary_prompt = f"""
            You are a research assistant summarizing scientific articles.

            Task: Create a comprehensive summary of key findings about "{query}"

            Guidelines:
            1. Focus on the most important and recent research
            2. Include specific details, methodologies, and results from the full text
            3. Highlight any contradictions or limitations
            4. Use bullet points for key findings
            5. Be concise but informative (300-500 words)

            Articles with full text content:
            """
            for i, result in enumerate(fulltext_results):
                summary_prompt += f"\n\nArticle {i+1} ({result['pmcid']}):\n"
                summary_prompt += f"Title: {result['article'].get('title', 'N/A')}\n"
                summary_prompt += f"Year: {result['article'].get('pubYear', 'N/A')}\n"
                summary_prompt += f"Abstract: {result['article'].get('abstractText', 'N/A')[:300]}\n"
                summary_prompt += f"Full Text:\n{result['fulltext'][:2000]}"
                if len(result['fulltext']) > 2000:
                    summary_prompt += "\n[Full text truncated, showing first 2000 characters]"

            summary_prompt += "\n\nProvide your summary in bullet points, citing specific findings from the articles."


            print("--- \nsummary_prompt:", summary_prompt, "\n---")

            summary_response = _call_llm(llm, summary_prompt)
            summary = (
                summary_response.content
                if hasattr(summary_response, "content")
                else str(summary_response)
            )

            print("--- \nsummary:", summary, "\n---")
            # Extract citations for JUST the 5 full text

            top_5_citations = extract_structured_citations([r["article"] for r in fulltext_results])
            print(f"[Researcher] Extracted {len(top_5_citations)} citations")
            if top_5_citations:
                print(f"[Researcher] Sample citation: {top_5_citations[0]}")
            return {
                "output": summary or "Research summary generated",
                "input": query,
                "citations": top_5_citations,
                "raw_results": results,
                "fulltext_results": fulltext_results,
                "fulltext_used": len(fulltext_results) > 0,
                "top_articles": [r["article"] for r in fulltext_results]
            }

        except Exception as e:
            print(f"Research error: {e}")
            return {
                "output": f"Research failed for: {query}",
                "input": query,
                "citations": [],
                "raw_results": [],
                "fulltext_used": False
            }

    return researcher_invoke

# ----------------- #
# WRITER NODE       #
# ----------------- #
def create_writer_chain():
    """Creates the writer chain."""
    def writer_invoke(state):
        research = state.get("research_findings", [])
        research_text = "\n\n".join(research) if research else "No research available."
        citations = state.get("citations", [])
        print(f"[Writer] Received {len(citations)} citations") 
        citations_text = format_citations_yaml(citations) if citations else "No citations available."

        try:
            prompt = writer_prompt_template.format(
                main_task=state.get("main_task", ""),
                research_findings=research_text,
                citations=citations_text,
                draft=state.get("draft", ""),
                critique_notes=state.get("critique_notes", "")
            )

            response = _call_llm(llm, prompt)
            print("llm call done")
            content = response.content if hasattr(response, 'content') else str(response)
            print("------")
            print("content:", content)
            # Clean up the content
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join([l for l in lines if not l.strip().startswith("```")])
            content = content.strip()
            print("-----")
            print("content input into format_as_markdown:", content)
            # Format as Markdown
            markdown_content = format_as_markdown(content, citations, state.get("main_task", "Topic"))

            # Validate the output
            if not markdown_content or len(markdown_content.strip()) < 100:
                raise ValueError("Generated content is too short")

            return markdown_content

        except Exception as e:
            print(f"Writer error: {e}")
            print(f"Research text length: {len(research_text)}")
            print(f"Research text preview: {research_text[:200]}")

            # Fallback: create a simple report from research findings
            fallback_report = f"""# Research Report: {state.get('main_task', 'Topic')}

            ## Abstract
            {research_text[:200]}...

            ## Research Findings
            {research_text}
            """

            if citations:
                fallback_report += f"""

                ## References
                ```yaml
                {format_citations_yaml(citations)}
                """
        return fallback_report

    return writer_invoke

# ----------------- #
# CRITIQUE NODE     #
# ----------------- #
def create_critique_chain():
    """Creates the critique chain."""
    def critique_invoke(state):
        draft = state.get("draft", "")
        print("draft:", draft)
        revision_num = state.get("revision_number", 0)
    
        # Safety checks
        if len(draft.strip()) < 100:
            return "APPROVED - Draft is minimal but acceptable."
        
        if revision_num >= 3:
            return "APPROVED - Maximum revisions reached. The report is satisfactory."
        
        prompt = critique_prompt_template.format(
            main_task=state.get("main_task", ""),
            draft=draft
        )
        
        try:
            response = _call_llm(llm, prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return content if content else "APPROVED"
        except Exception as e:
            print(f"Critique error: {e}")
            return "APPROVED - Error in critique, proceeding with current draft."
    
    return critique_invoke