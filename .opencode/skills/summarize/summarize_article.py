import sys
import os
import re

# Configuration
SUMMARY_TEMPLATE = """# Article Summary
## Citation
{}

## Research Question
{}

## Methods
{}

## Results
{}

## Discussion
{}

## Conclusion
{}
"""
    
def extract_citation(text):
    """Extract citation in ACS format from various possible locations"""
    lines = text.split('\n')

    # Look for the title at the very beginning (before any section headers)
    for i, line in enumerate(lines[:10]):
        if line.strip() and not line.startswith('#') and not line.startswith('##'):
            # This might be the title
            title = line.strip()
            # Look for author information in the next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('#') and not next_line.startswith('##'):
                    # Try to construct a basic citation
                    return f"{title}. {next_line}"
            return title

    return "Citation not available in standard format"

def extract_section(text, section_keywords, section_name):
    """Extract a specific section from text using multiple keywords"""
    lines = text.split('\n')
    section_lines = []

    # Try to find the section header - look specifically for ## SectionName
    for i, line in enumerate(lines):
        if line.startswith('##'):
            line_upper = line.upper()
            if any(keyword.upper() in line_upper for keyword in section_keywords):
                # Found section header, extract content including subsections
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('##') and j > i + 1:  # Next main section (allow one subsection)
                        break
                    if lines[j].strip() and not lines[j].strip().startswith(('References', 'REFERENCES', 'Acknowledgements', 'ACKNOWLEDGEMENTS')):
                        section_lines.append(lines[j].strip())
                break

    return ' '.join(section_lines) if section_lines else "Not provided"

def summarize_text(text):
    """Generate a summary of the article text."""
    # Extract citation
    citation = extract_citation(text)

    # Extract research question from Abstract or Introduction
    research_question = extract_section(text, ['Abstract', 'Introduction', 'Background', 'Objective', 'Aim'], 'research_question')

    # Extract methods
    methods = extract_section(text, ['Methods', 'Methodology', 'Experimental Design', 'Participants', 'Materials and Methods', 'Study Population', 'Exposure', 'Statistical Analysis'], 'methods')

    # Extract results
    results = extract_section(text, ['Results', 'Findings', 'Outcomes', 'Data', 'Descriptive Statistics', 'Association'], 'results')

    # Extract discussion
    discussion = extract_section(text, ['Discussion', 'Interpretation', 'Analysis', 'Conclusion'], 'discussion')

    # Extract conclusion
    conclusion = extract_section(text, ['Conclusion', 'Conclusions', 'Summary', 'Final Remarks'], 'conclusion')

    # Generate summary
    summary = SUMMARY_TEMPLATE.format(
        citation,
        research_question,
        methods,
        results,
        discussion,
        conclusion
    )

    return summary



def summarize_article(input_source, output_format="markdown", output_file=None):
    """
    Main function for programmatic access

    Args:
        input_source (str): Path to local file containing article text
        output_format (str): "markdown", "json", or "html"
        output_file (str): Path to save output (optional)

    Returns:
        str: Generated summary text
    """
    # Validate input - only accept local file paths
    if not os.path.exists(input_source):
        print(f"Invalid input source: {input_source}")
        print("The summarize skill only accepts local file paths containing article text.")
        print("Use the literature-search-europepmc skill to retrieve articles first.")
        return None

    # Read article content from local file
    try:
        with open(input_source, 'r') as f:
            article_text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    if not article_text:
        print("Failed to retrieve article content")
        return None

    # Generate summary
    summary = summarize_text(article_text)

    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(summary)
        print(f"Summary saved to {output_file}")

    return summary

def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python summarize_article.py <input_source> [--output <output_file>] [--format <format>]")
        print("  input_source: File path containing article text (retrieved via literature-search-europepmc)")
        print("  --output: Output file path (default: summary.md)")
        print("  --format: Output format (markdown, json, html)")
        print("\nNote: This skill only summarizes articles that have already been retrieved.")
        print("Use the literature-search-europepmc skill to fetch articles first.")
        sys.exit(1)

    input_source = sys.argv[1]
    output_file = "summary.md"
    output_format = "markdown"

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Execute summarization
    result = summarize_article(input_source, output_format, output_file)
    if result:
        print("Summarization completed successfully")
    else:
        print("Summarization failed")
        sys.exit(1)

if __name__ == "__main__":
    main()