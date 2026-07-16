#!/usr/bin/env python3
"""
Script to determine the appropriate resume point for a research project.

Usage:
    python3 check_resume_point.py
"""

import json
import os
import sys

def check_resume_point():
    """Determine where to resume research from."""
    
    # Check if metadata file exists
    if not os.path.exists("research_metadata.json"):
        print("No research_metadata.json found. Starting new project.")
        return "new_project"
    
    # Load metadata
    with open("research_metadata.json", "r") as f:
        metadata = json.load(f)
    
    print(f"Project: {metadata.get('project_name', 'Unknown')}")
    print(f"Status: {metadata.get('status', 'Unknown')}")
    print(f"Completed steps: {metadata.get('completed_steps', [])}")
    print()
    
    # Determine resume point
    completed_steps = metadata.get('completed_steps', [])
    
    if "synthesis" in completed_steps:
        print("✓ Research appears to be complete")
        return "complete"
    elif "summarization" in completed_steps:
        print("Next step: Synthesis")
        return "synthesis"
    elif "full_text_retrieval" in completed_steps:
        print("Next step: Summarization")
        return "summarization"
    elif "paper_selection" in completed_steps:
        print("Next step: Full text retrieval")
        return "full_text_retrieval"
    elif "info_retrieval" in completed_steps:
        print("Next step: Paper selection")
        return "paper_selection"
    else:
        print("Next step: Information retrieval")
        return "info_retrieval"

if __name__ == "__main__":
    resume_point = check_resume_point()
    sys.exit(0 if resume_point else 1)