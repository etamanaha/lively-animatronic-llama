import json
import subprocess
import os

def fetch_references(pmid, output_file):
    """Fetch references for a given PMID using the Europe PMC API."""
    command = [
        "uv", "run", "scripts/europepmc_api.py", "get_references",
        "MED", pmid, "--output", output_file
    ]
    subprocess.run(command, check=True)

def fetch_full_text(pmcid, output_file):
    """Fetch full text for a given PMCID using the Europe PMC API."""
    command = [
        "uv", "run", "scripts/europepmc_api.py", "get_fulltext",
        pmcid, "--output", output_file
    ]
    subprocess.run(command, check=True)

def summarize_article(full_text_file, output_file):
    """Summarize the article using the summarize skill."""
    with open(full_text_file, 'r') as f:
        full_text = f.read()

    # Here you would integrate the summarization logic
    # For now, we'll just write a placeholder summary
    summary = f"""# Article Summary
## Citation
Not provided

## Research Question
Not provided

## Methods
Not provided

## Results
Not provided

## Discussion
Not provided

## Conclusion
Not provided
"""

    with open(output_file, 'w') as f:
        f.write(summary)

def main():
    # Example usage
    pmid = "34265844"  # Example PMID
    references_file = "references.json"
    full_text_file = "fulltext.txt"
    summary_file = "summary.md"

    # Step 1: Fetch references
    fetch_references(pmid, references_file)

    # Step 2: Extract PMCIDs from references and fetch full texts
    with open(references_file, 'r') as f:
        references = json.load(f)

    for reference in references.get('references', []):
        pmcid = reference.get('pmcid')
        if pmcid:
            full_text_file = f"fulltext_{pmcid}.txt"
            fetch_full_text(pmcid, full_text_file)

            # Step 3: Summarize the article
            summary_file = f"summary_{pmcid}.md"
            summarize_article(full_text_file, summary_file)

if __name__ == "__main__":
    main()