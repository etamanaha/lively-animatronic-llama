---
name: summarize
description: Use this skill after finding relevant papers to summarize the content of each paper into a structured, information-dense summary. This skill is used to extract key information from individual papers before synthesizing findings across multiple sources.
---

## Research paper summarization skill

## Inputs

Accept one of the following:
- Full article text
- PDF converted to text
- Abstract
- Relevant excerpts
- PMCID (e.g., PMC1234567)
- PMID
- DOI (e.g., 10.1038/s41586-021-03819-2)
- URL

## When to Use
- Summarizing individual research papers into a structured summary, extracting key insights, and providing a comprehensive overview of the paper's contributions, methods, results, and limitations.
- Use when the user wants key information from a paper without reading the entire document.

**Not for:**
- Summarizing multiple papers at once (use the synthesis skill for that), or for non-research documents like tutorials, textbooks, or blog posts.
- Searching for additional information.

## If given a PMCID, PMID, DOI, or Europe PMC URL:

1. Retrieve the full text if it is openly available.
2. Use the retrieved article as the source for the summary.
3. If the full text cannot be retrieved, summarize the abstract instead and state that the summary is based only on the abstract.

## Instructions
Read the provided article and summarize it using the following structure.

### 1. ACS style citation

### 2. Research Question
State the primary scientific question or hypothesis. This should be a 1-2 sentence summary of the research objective.

### 3. Methods
Briefly describe how the researchers answered the research question. Do not go into excessive detail, but include enough information to understand the experimental design and approach.

Include:
- Study design (e.g., experimental, observational, computational, systematic review)
- Experimental model (e.g., human participants, animals, cell lines, tissues, environmental samples)
- Processes or techniques used, such as:
  - surveys
  - chromatography
  - spectroscopy
  - sequencing
  - machine learning
  - statistical analyses
- The type of data measured (e.g., gene expression, protein abundance, metabolite concentrations, behavioral outcomes, chemical concentrations, physiological measurements)
- Any notable controls or comparison groups, if reported

### 4. Results
Summarize the key outcomes. Provided numerical results, trends, and statistical significance where applicable.

### 5. Discussion
Summarize the authors' interpretation of the results, their implications, and any limitations or future directions they mention.

### 6. Conclusion
Provide a brief summary of the overall findings and their significance in the context of the research question.

## Requirements

- Do not invent information.
- Do not copy text verbatim from the article; instead, paraphrase and summarize.
- Preserve scientific terminology.
- Prefer precision over simplification.
- If required information is missing, state "Not reported."

## Output Format

```markdown
# Article Title

## Research Question
...
## Citation in ACS Style
...
## Abstract
...
## Methods
...
## Results
...
## Discussion
...
## Conclusion
...

## Usage Examples

### Basic Usage

**Summarize a local file**
python summarize_article.py /path/to/article.txt --output summary.md

**Summarize from a URL**
python summarize_article.py https://example.com/article.html --output summary.md

**Summarize using PMCID**
python summarize_article.py PMC1234567 --output summary.md

**Summarize using DOI**
python summarize_article.py 10.1038/s41586-021-03819-2 --output summary.md

## Error Handling

### Common Issues and Solutions
1. File not found errors:
  - Verify the input file path is correct
  - Check file permissions
2. URL fetch failures:
  - Check internet connectivity
  - Verify the URL is accessible
  - Some websites block automated requests
3. PMCID/DOI fetch failures:
  - Ensure the PMCID/DOI is valid
  - Check Europe PMC/CrossRef API status
  - Some articles may not have open access full text
4. Section not found:
  - The article may have non-standard formatting
  - Try manual section identification
  - Report to maintainer for pattern improvements
5. Memory errors with large files:
  - Process smaller sections of the text
  - Increase system memory allocation

## Technical Details

### Input Validation
The script validates input sources before processing:
  - URLs are checked for proper format
  - PMCIDs/DOIs are validated
  - Local files are checked for existence and readability
  
### Caching Mechanism
Fetched articles are cached to avoid repeated downloads:
  - Cache directory: .summarize_cache
  - Each article is stored with its PMCID as filename
  - Cache is checked before making new API requests

### Output Formats
Supported output formats:
  - Markdown (default): Human-readable format with headings
  - JSON: Structured data for programmatic use
  - HTML: Formatted output for web display

### Performance Considerations
  - Large articles (>10MB) may require increased memory
  - API rate limits apply when fetching from Europe PMC
  - Complex formatting may slow down processing

## Integration with Other Skills
This skill can be integrated with other research workflows:
1. With literature-search-europepmc: 
```bash
# Search for papers, then summarize them
uv run scripts/europepmc_api.py search "caffeine health effects" --output results.json
# Extract PMCIDs and summarize
python extract_pmcids.py results.json | xargs -I {} python summarize_article.py {} --output "summary_{}.md"
```
2. With synthesis skill:
```bash
# Generate individual summaries, then synthesize
for pmcid in PMC1234567 PMC7654321; do
  python summarize_article.py $pmcid --output "summary_${pmcid}.md"
done
# Use synthesis skill on the summaries
```

## Troubleshooting
### Debugging Tips
1. Enable verbose output:
```bash
python summarize_article.py PMC1234567 --output summary.md --verbose
```
2. Check cache contents:
```bash
ls -la .summarize_cache/
```
3. Test with simple articles first:
```bash
# Start with articles that have clear section headers
python summarize_article.py PMC1234567 --output test_summary.md
```