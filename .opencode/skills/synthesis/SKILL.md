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

## Integration of Chemical Data with Literature

This skill can synthesize findings from both literature summaries and chemical data summaries to provide comprehensive insights.

### Inputs for Combined Synthesis
- Structured summaries of research papers
- Structured chemical data summaries
- Both types of inputs can be provided together

### When to Use for Combined Synthesis
- The user has gathered both chemical compound data and literature about the compound
- The task is to understand how chemical properties relate to biological effects and clinical applications
- Creating comprehensive reports that integrate pharmacological data with research findings

**Not for:**
- Synthesis of only chemical data (use chemical summaries alone)
- Synthesis of only literature (use literature synthesis alone)

### Workflow for Combined Synthesis
1. Gather chemical data summaries and literature summaries
2. Analyze relationships between:
   - Chemical properties and biological targets
   - Bioactivity data and pharmacological effects
   - Molecular mechanisms and clinical outcomes
   - Structure-activity relationships
3. Identify patterns across both data types
4. Create a synthesis that explains how chemical properties contribute to observed biological effects
5. Highlight connections between molecular data and research findings

### Synthesis Principles for Combined Data
- **Correlate chemical properties with biological effects:** Explain how molecular characteristics relate to observed pharmacological actions
- **Bridge molecular mechanisms and clinical applications:** Show how drug-target interactions lead to therapeutic effects
- **Highlight structure-activity relationships:** Discuss how chemical structure influences biological activity
- **Integrate safety considerations:** Combine chemical safety data with literature on adverse effects
- **Provide comprehensive context:** Explain the full picture from molecule to clinical application

### Output Format for Combined Synthesis

```markdown
# Synthesis: [Research Topic] - Chemical and Biological Integration

## Chemical Profile Overview
[Summary of key chemical properties and bioactivity data]

## Biological Effects and Mechanisms
[Synthesis of how chemical properties relate to biological effects]

## Structure-Activity Relationships
[Analysis of how chemical structure influences biological activity]

## Clinical Applications and Therapeutic Uses
[Integration of chemical data with clinical research findings]

## Safety and Pharmacological Considerations
[Combined analysis of chemical safety data and literature on adverse effects]

## Key Findings Integration
### Chemical Data Findings
- [Key chemical property 1]
- [Key bioactivity finding 1]

### Literature Findings
- [Key research finding 1]
- [Key research finding 2]

### Integrated Understanding
[Explanation of how chemical and biological data together provide comprehensive understanding]

## Gaps and Open Questions
### Chemical Data Gaps
- [What chemical information is missing?]

### Literature Gaps
- [What research questions remain unanswered?]

### Integrated Research Needs
- [What combined chemical + biological research is needed?]

## Bottom-line Interpretation
[Comprehensive interpretation integrating both chemical and biological evidence]
```

### Example of Combined Synthesis

# Synthesis: Amphetamine Mechanism of Action and ADHD Treatment

## Chemical Profile Overview
Amphetamine (C9H13N) is a central nervous system stimulant with a molecular weight of 135.21 g/mol. It acts as a norepinephrine-dopamine reuptake inhibitor with IC50 values of 0.047 μM for dopamine reuptake inhibition and 0.65 μM for norepinephrine reuptake inhibition.

## Biological Effects and Mechanisms
The chemical structure of amphetamine, with its phenyl ring and amine group, allows it to cross the blood-brain barrier and interact with monoamine transporters. The literature shows that this mechanism increases synaptic dopamine and norepinephrine levels, which modulate attention and impulse control - key deficits in ADHD.

## Structure-Activity Relationships
The specific stereochemistry of amphetamine (dextroamphetamine is more potent than levoamphetamine) correlates with its ability to increase dopamine release. The literature confirms that dextroamphetamine has greater clinical efficacy for ADHD symptoms, demonstrating the structure-activity relationship.

## Clinical Applications and Therapeutic Uses
Chemical data shows amphetamine's high affinity for dopamine transporters, while literature demonstrates this leads to improved focus and reduced hyperactivity in ADHD patients. The combination explains why amphetamine is effective for ADHD treatment.

## Safety and Pharmacological Considerations
While chemical data shows amphetamine's pharmacological profile, literature research highlights potential side effects like increased heart rate and blood pressure, as well as risks of dependence and abuse.

## Key Findings Integration
### Chemical Data Findings
- High affinity for dopamine and norepinephrine transporters
- Specific stereochemical requirements for activity
- Blood-brain barrier penetration capabilities

### Literature Findings
- Increased synaptic dopamine improves ADHD symptoms
- Dextroamphetamine more effective than levoamphetamine
- Clinical efficacy confirmed in multiple studies

### Integrated Understanding
The chemical properties of amphetamine explain its pharmacological mechanism, which in turn accounts for its clinical effectiveness in treating ADHD. The molecular structure enables the biological effects that produce therapeutic benefits.

## Bottom-line Interpretation
Amphetamine's effectiveness in treating ADHD stems from its chemical structure enabling dopamine and norepinephrine modulation in the brain. This integrated understanding of chemical properties and biological effects provides a comprehensive explanation for its therapeutic use.

## Specific Example: Amphetamine and ADHD

**User Question:** "Why are amphetamines used to treat ADHD?"

**Inputs:**
1. Chemical data summary of amphetamine (from ChEMBL or similar)
2. Literature summaries of 5 key research papers on amphetamine and ADHD

**Synthesis Process:**

1. **Extract chemical properties:**
   - Molecular structure and pharmacokinetics
   - Dopamine/norepinephrine reuptake inhibition data
   - Blood-brain barrier penetration capabilities

2. **Extract literature findings:**
   - ADHD pathophysiology (dopamine deficiency)
   - Clinical trial results showing efficacy
   - Mechanism of action studies
   - Safety and side effect profiles

3. **Integrate findings:**
   - Explain how chemical structure enables dopamine modulation
   - Show how pharmacological effects address ADHD symptoms
   - Correlate bioactivity data with clinical outcomes
   - Analyze structure-activity relationships

4. **Create comprehensive synthesis:**
   - Chemical profile section
   - Biological mechanism section
   - Clinical application section
   - Safety considerations section
   - Integrated conclusion

**Output Structure:**

```markdown
# Why Are Amphetamines Used to Treat ADHD?

## Chemical Profile of Amphetamine
[Summarize key chemical properties from chemical data]

## ADHD Pathophysiology
[Summarize literature on ADHD brain chemistry]

## Mechanism of Action
[Integrate chemical data with literature on how amphetamine works]

## Clinical Efficacy
[Summarize literature on treatment effectiveness]

## Safety and Considerations
[Combine chemical safety data with literature on side effects]

## Integrated Explanation
[Comprehensive answer showing how chemical properties lead to therapeutic effects]

## References
[Cite both chemical data sources and literature papers]
```
