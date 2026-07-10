---
name: synthesis
description: Use this skill after creating structured summaries of individual papers to synthesize findings across multiple sources into a coherent overview. This skill is used to identify patterns, themes, and gaps in the literature, providing a higher-level interpretation of the research landscape.
permission:
  webfetch: deny
  websearch: deny
---

# Literature Synthesis Skill

## Inputs
- Structured summaries of individual research papers, notes, or excerpts from multiple sources.

## When to use
- The user has already gathered multiple papers, notes, or summaries from a literature search.
- The task is to combine findings across sources into a higher-level interpretation.

**Not for:** 
- Summarizing individual papers (use the summarize skill for that)
- Non-research documents like tutorials, textbooks, or blog posts.

## Workflow
1. Gather the relevant papers, notes, or summaries from the literature-search and paper-reading stages.
2. Compare sources across dimensions such as:
   - topic focus
   - methods and datasets
   - conclusions and claims
   - strengths and weaknesses
   - whether findings converge or conflict
3. Group papers into themes or clusters when helpful.
4. Write a synthesis that moves from individual studies to broader patterns and implications.


5. All information must be cited with in-text references to the original sources. Do not invent citations or findings.

## Synthesis principles
- Focus on patterns across the literature rather than repeating paper-by-paper summaries.
- Highlight both consensus and disagreement.
- Keep note of what information is coming from which source. Provide in-text citations to the original sources.

## Output format
```markdown
# Synthesis of [Research Topic]
## Major themes or clusters
...
## Evidence and comparisons across studies
...
## Agreements and disagreements
...
## Gaps and open questions
...
## Bottom-line interpretation
...
```
