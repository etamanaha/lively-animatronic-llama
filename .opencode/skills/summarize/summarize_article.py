import sys
import requests
from bs4 import BeautifulSoup
import re

def fetch_online_article(url):
    """Fetch the text content from an online article."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Try to extract main content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "iframe"]):
            script.decompose()

        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        print(f"Error fetching online article: {e}")
        return None

def summarize_text(text):
    """Generate a summary of the article text."""
    # Extract key sections from the text
    lines = text.split('\n')

    # Extract citation (first line or look for citation patterns)
    citation = "Not provided"
    for line in lines[:10]:  # Check first 10 lines
        if "doi:" in line.lower() or "pmid:" in line.lower() or "pmcid:" in line.lower():
            citation = line.strip()
            break
    if citation == "Not provided" and lines:
        citation = lines[0].strip() if lines[0].strip() else "Not provided"

    # Extract research question from Abstract
    research_question = "Not provided"
    for line in lines:
        if "Question" in line or "Objective" in line or "Aim" in line:
            research_question = line.strip()
            break

    # Extract methods
    methods = "Not provided"
    for i, line in enumerate(lines):
        if "Methods" in line or "Setting and Design" in line or "METHODS" in line:
            methods_start = i
            # Extract until next section or end of text
            methods_lines = []
            for j in range(methods_start, len(lines)):
                if lines[j].startswith('##') and j > methods_start:
                    break
                if lines[j].strip() and not lines[j].strip().startswith(('References', 'REFERENCES', 'Acknowledgements', 'ACKNOWLEDGEMENTS')):
                    methods_lines.append(lines[j].strip())
            methods = ' '.join(methods_lines)
            break

    # Extract results
    results = "Not provided"
    for i, line in enumerate(lines):
        if "Results" in line or "RESULT" in line:
            results_start = i
            # Extract until next section or end of text
            results_lines = []
            for j in range(results_start, len(lines)):
                if lines[j].startswith('##') and j > results_start:
                    break
                if lines[j].strip() and not lines[j].strip().startswith(('References', 'REFERENCES', 'Acknowledgements', 'ACKNOWLEDGEMENTS')):
                    results_lines.append(lines[j].strip())
            results = ' '.join(results_lines)
            break

    # Extract discussion
    discussion = "Not provided"
    for i, line in enumerate(lines):
        if "Discussion" in line or "DISCUSSION" in line:
            discussion_start = i
            # Extract until next section or end of text
            discussion_lines = []
            for j in range(discussion_start, len(lines)):
                if lines[j].startswith('##') and j > discussion_start:
                    break
                if lines[j].strip() and not lines[j].strip().startswith(('References', 'REFERENCES', 'Acknowledgements', 'ACKNOWLEDGEMENTS')):
                    discussion_lines.append(lines[j].strip())
            discussion = ' '.join(discussion_lines)
            break

    # Extract conclusion
    conclusion = "Not provided"
    for i, line in enumerate(lines):
        if "Conclusions" in line or "Conclusion" in line or "CONCLUSION" in line:
            conclusion_start = i
            # Extract until next section or end of text
            conclusion_lines = []
            for j in range(conclusion_start, len(lines)):
                if lines[j].startswith('##') and j > conclusion_start:
                    break
                if lines[j].strip() and not lines[j].strip().startswith(('References', 'REFERENCES', 'Acknowledgements', 'ACKNOWLEDGEMENTS')):
                    conclusion_lines.append(lines[j].strip())
            conclusion = ' '.join(conclusion_lines)
            break

    # Generate summary
    summary = f"""# Article Summary
## Citation
{citation}

## Research Question
{research_question}

## Methods
{methods}

## Results
{results}

## Discussion
{discussion}

## Conclusion
{conclusion}
"""

    return summary

def main():
    # Example usage
    import sys
    if len(sys.argv) < 2:
        print("Usage: python summarize_article.py <input_file_or_url>")
        sys.exit(1)

    input_source = sys.argv[1]

    # Check if input is a URL
    if input_source.startswith(('http://', 'https://')):
        print(f"Fetching article from URL: {input_source}")
        article_text = fetch_online_article(input_source)
        if not article_text:
            print("Failed to fetch article from URL")
            sys.exit(1)
    else:
        # Assume it's a local file
        print(f"Reading article from file: {input_source}")
        try:
            with open(input_source, 'r') as f:
                article_text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    # Generate summary
    summary = summarize_text(article_text)

    # Write summary to file
    output_file = "summary.md"
    with open(output_file, 'w') as f:
        f.write(summary)

    print(f"Summary written to {output_file}")

if __name__ == "__main__":
    main()