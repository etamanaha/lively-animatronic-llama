---
name: summarize
description: Use this skill after finding relevant papers to summarize the content of each paper into a structured, information-dense summary. This skill is used to extract key information from individual papers before synthesizing findings across multiple sources.
permission:
  webfetch: deny
  websearch: deny
---

## Research paper summarization skill

## Inputs

Accept one of the following:
- Full article text
- PDF converted to text
- Abstract
- Relevant excerpts
- PMCID
- PMID
- DOI
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
State the primary scientific question or hypothesis.

### 3. Methods
Using the methods section (if available), briefly describe how the researchers answered the research question. Do not go into excessive detail, but include enough information to understand the experimental design and approach.

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
Using the results section (if available), summarize the key outcomes. Provided numerical results, trends, and statistical significance where applicable.

### 5. Dicussion
Using the discussion section (if available), summarize the authors' interpretation of the results, their implications, and any limitations or future directions they mention.

### 6. Conclusion
Provide a brief summary of the overall findings and their significance in the context of the research question.

## Requirements

- Do not invent information.
- Clearly distinguish reported findings from interpretation.
- Keep the summary under 500 words unless instructed otherwise.
- Preserve scientific terminology.
- Prefer precision over simplification.
- If required information is missing, state "Not reported."

## Output Format

```markdown
# Article Summary
## Citation
...
## Research Question
...
## Methods
...
## Results
...
## Discussion
...
## Conclusion
...
```
