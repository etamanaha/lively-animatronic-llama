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
- Inputs can be provided as Markdown files, text files, or any other structured format.

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

## Example
Here is an example of a synthesized output:

# Synthesis of Findings on the Effectiveness of Amphetamines on ADHD

## Major Themes
### 1. Supply Chain Vulnerabilities and Medication Shortages
The most recent ADHD drug shortage appears to be associated with disruptions in the international supply chain of raw ingredients, particularly amphetamines and their precursors. The study by [Article Summary 1](#article-summary-1) highlights that the sharp decline in US imports of raw amphetamines from Germany coincided with production cutbacks by multiple manufacturers. This vulnerability underscores the need for policies that strengthen supply chain resilience and require detailed information on API suppliers.

### 2. Global Variations in Stimulant Consumption
The United States is a global outlier in stimulant prescribing, consuming 67.6% of prescription stimulants while comprising only 26.8% of the population. The US consumption of amphetamines is significantly higher compared to methylphenidate, whereas other countries predominantly use methylphenidate. This variation suggests differences in clinical practice and controlled substance policy that warrant further investigation [Article Summary 2](#article-summary-2).

## Evidence and Comparisons Across Studies
### Effectiveness of Amphetamines
- **Article Summary 1**: Highlights the impact of supply chain disruptions on the availability of amphetamine-based medications.
- **Article Summary 2**: Demonstrates that the United States consumes significantly more amphetamines compared to other countries, suggesting their effectiveness in managing ADHD symptoms.
- **Article Summary 4**: Confirms that amphetamines have the largest effect in reducing the severity of ADHD core symptoms at 12 weeks.
- **Article Summary 5**: Provides a case study showing the effectiveness of immediate-release dextroamphetamine sulfate in managing ADHD symptoms when other medications are unavailable.

### Bone Health Considerations
- **Article Summary 3**: Discusses the potential negative effects of stimulant medications on bone health, including lower bone mineral density and impaired fracture healing. However, it also notes that stimulants can reduce fracture risk in younger populations through behavioral modifications.

### Global Variations
- **Article Summary 2**: Highlights significant differences in stimulant consumption between the United States and other countries, with the US consuming predominantly amphetamines and other countries using more methylphenidate.

## Agreements and Disagreements
### Agreements
All studies agree that amphetamines are effective in managing ADHD symptoms. They also highlight the importance of monitoring for adverse effects and the need for comprehensive treatment approaches that include both pharmacological and non-pharmacological interventions.

### Disagreements
- **Article Summary 3** notes potential negative effects of stimulants on bone health, while **Article Summary 5** suggests that immediate-release dextroamphetamine sulfate can be an effective alternative during shortages without mentioning bone health concerns.
- **Article Summary 2** highlights global variations in stimulant consumption, suggesting differences in clinical practice, while **Article Summary 4** focuses on the pharmacological management of ADHD in adults, emphasizing the efficacy of psychostimulants.

## Gaps and Open Questions
### Supply Chain Resilience
- How can the pharmaceutical industry and regulatory bodies improve supply chain resilience to prevent future shortages of ADHD medications?
- What policies can be implemented to require detailed information on API suppliers and monitor supply chain vulnerabilities?

### Bone Health
- What are the long-term effects of stimulant medications on bone health, particularly in adults and older populations?
- How can the negative effects of stimulants on bone health be mitigated while maintaining their effectiveness in managing ADHD symptoms?

### Global Variations
- What factors contribute to the differences in stimulant consumption between the United States and other countries?
- How can clinical practices be standardized to ensure consistent and effective treatment of ADHD worldwide?

### Alternative Medications
- What is the long-term effectiveness and safety of immediate-release dextroamphetamine sulfate in managing ADHD symptoms?
- How can healthcare providers be better equipped to manage medication shortages and provide alternative treatments?

## Bottom-Line Interpretation
Amphetamines are highly effective in managing ADHD symptoms, as evidenced by their widespread use and efficacy in reducing core symptoms. However, the recent medication shortages highlight the vulnerability of the pharmaceutical supply chain to international disruptions. Addressing these vulnerabilities is crucial to ensure consistent access to effective treatments. Additionally, the potential negative effects of stimulants on bone health warrant further investigation, particularly in long-term users. The global variations in stimulant consumption suggest differences in clinical practice that may benefit from standardization. Finally, alternative medications like immediate-release dextroamphetamine sulfate can be viable options during shortages, but more research is needed to confirm their long-term effectiveness and safety.
