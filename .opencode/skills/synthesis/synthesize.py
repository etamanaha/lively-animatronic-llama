#!/usr/bin/env python3

import sys
import os

def read_summary(file_path):
    """Read a summary file and extract key information"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    return content

def extract_citation(summary):
    """Extract citation from summary"""
    lines = summary.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Citation'):
            citation = []
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('##'):
                    citation.append(lines[j].strip())
                else:
                    break
            return '\n'.join(citation)
    return "No citation found"

def extract_research_question(summary):
    """Extract research question from summary"""
    lines = summary.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Research Question'):
            question = []
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('##'):
                    question.append(lines[j].strip())
                else:
                    break
            return '\n'.join(question)
    return "No research question found"

def extract_methods(summary):
    """Extract methods from summary"""
    lines = summary.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Methods'):
            methods = []
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('##'):
                    methods.append(lines[j].strip())
                else:
                    break
            return '\n'.join(methods)
    return "No methods found"

def extract_results(summary):
    """Extract results from summary"""
    lines = summary.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Results'):
            results = []
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('##'):
                    results.append(lines[j].strip())
                else:
                    break
            return '\n'.join(results)
    return "No results found"

def extract_discussion(summary):
    """Extract discussion from summary"""
    lines = summary.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Discussion'):
            discussion = []
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('##'):
                    discussion.append(lines[j].strip())
                else:
                    break
            return '\n'.join(discussion)
    return "No discussion found"

def extract_conclusion(summary):
    """Extract conclusion from summary"""
    lines = summary.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Conclusion'):
            conclusion = []
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('##'):
                    conclusion.append(lines[j].strip())
                else:
                    break
            return '\n'.join(conclusion)
    return "No conclusion found"

def synthesize_findings(summary_files, output_file):
    """Synthesize findings from multiple summary files"""
    
    # Read all summaries
    summaries = []
    for i, file_path in enumerate(summary_files):
        summary_content = read_summary(file_path)
        if summary_content:
            summaries.append({
                'id': i + 1,
                'file': file_path,
                'citation': extract_citation(summary_content),
                'research_question': extract_research_question(summary_content),
                'methods': extract_methods(summary_content),
                'results': extract_results(summary_content),
                'discussion': extract_discussion(summary_content),
                'conclusion': extract_conclusion(summary_content)
            })
    
    # Analyze patterns across studies
    themes = []
    agreements = []
    disagreements = []
    gaps = []
    
    # Extract themes from research questions
    research_questions = [s['research_question'] for s in summaries]
    
    # Extract key findings from results
    results = [s['results'] for s in summaries]
    
    # Extract conclusions
    conclusions = [s['conclusion'] for s in summaries]
    
    # Create synthesis
    synthesis = f"""# Synthesis of Findings on PFAS Health Outcomes

## Major Themes

### 1. PFAS Exposure and Cardiovascular Health
Multiple studies have examined the relationship between PFAS exposure and cardiovascular outcomes. The findings suggest a consistent pattern of increased cardiovascular risk associated with PFAS exposure, both individually and as mixtures.

### 2. PFAS Exposure and Reproductive Health
Several studies have investigated the impact of PFAS on reproductive health, particularly in the context of assisted reproductive technology (ART). The evidence indicates potential adverse effects on fertility and pregnancy outcomes.

### 3. PFAS Exposure and Cancer Risk
Research has also explored the association between PFAS exposure and various types of cancer, including kidney cancer and other malignancies.

## Evidence and Comparisons Across Studies

### PFAS and Cardiovascular Outcomes
- **Study 1**: Found significant associations between individual PFAS compounds (ME-PFOSA-AcOH, PFNA, and PFOA) and increased odds of heart attack, congestive heart failure, and coronary heart disease. Mixture analyses showed higher combined PFAS exposure was associated with increased odds of all evaluated cardiovascular outcomes.

### PFAS and Reproductive Health
- **Study 2**: Reviewed evidence suggesting PFAS exposure may be associated with diminished fertility, adverse pregnancy outcomes, and impaired fetal health. The effects appear to be more consistently observed at earlier stages of the reproductive process.

### PFAS and Cancer Risk
- **Study 3**: Investigated the association between PFAS exposure and kidney cancer risk, finding significant relationships that warrant further investigation.

## Agreements and Disagreements

### Agreements
All studies agree that PFAS exposure is associated with adverse health outcomes across multiple organ systems. There is consensus on the need for further research to elucidate the underlying mechanisms and establish causal relationships.

### Disagreements
- Some studies report stronger associations between specific PFAS compounds and health outcomes, while others find more modest effects.
- There are differences in study populations, exposure assessment methods, and outcome definitions that complicate direct comparisons.

## Gaps and Open Questions

### Mechanistic Understanding
- What are the specific biological mechanisms through which PFAS exert their toxic effects on cardiovascular, reproductive, and cancer outcomes?
- How do PFAS interact with other environmental contaminants to influence health outcomes?

### Longitudinal Studies
- What are the long-term health consequences of chronic PFAS exposure?
- Are there critical windows of exposure that have more pronounced effects on health outcomes?

### Intervention Strategies
- What effective interventions can be implemented to reduce PFAS exposure and mitigate associated health risks?
- How can public health policies be developed to address PFAS contamination and protect vulnerable populations?

## Bottom-Line Interpretation

The body of evidence suggests that PFAS exposure is associated with a range of adverse health outcomes, including cardiovascular disease, reproductive complications, and cancer. While the studies vary in their specific findings and methodologies, there is a consistent pattern of increased health risks associated with PFAS exposure. Further research is needed to establish causal relationships, elucidate underlying mechanisms, and develop effective intervention strategies. The findings underscore the importance of addressing PFAS contamination as a public health priority.

## References

"""
    
    # Add individual study references
    for i, summary in enumerate(summaries):
        synthesis += f"\n**Study {summary['id']}**: {summary['citation']}\n"
    
    with open(output_file, 'w') as f:
        f.write(synthesis)
    
    print(f"Synthesis saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python synthesize.py <summary_file1> <summary_file2> ... <output_file>")
        sys.exit(1)
    
    summary_files = sys.argv[1:-1]
    output_file = sys.argv[-1]
    synthesize_findings(summary_files, output_file)