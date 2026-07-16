#!/usr/bin/env python3
"""
Script to update research metadata after completing a step.

Usage:
    python3 update_metadata.py <step_name> [file_paths...]

Example:
    python3 update_metadata.py full_text_retrieval fulltext1.txt fulltext2.txt
"""

import json
import os
import sys
import hashlib
from datetime import datetime

def calculate_checksum(filepath):
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_modification_time(filepath):
    """Get file modification time in ISO format."""
    mod_time = os.path.getmtime(filepath)
    return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%dT%H:%M:%SZ")

def update_metadata(step_name, file_paths):
    """Update the research metadata file after completing a step."""
    
    # Check if metadata file exists
    if not os.path.exists("research_metadata.json"):
        print("Error: research_metadata.json not found in current directory")
        sys.exit(1)
    
    # Load existing metadata
    with open("research_metadata.json", "r") as f:
        metadata = json.load(f)
    
    # Update completed steps
    if step_name not in metadata["completed_steps"]:
        metadata["completed_steps"].append(step_name)
    
    # Update status
    status_map = {
        "info_retrieval": "papers_retrieved",
        "paper_selection": "papers_selected", 
        "full_text_retrieval": "full_texts_retrieved",
        "summarization": "summaries_generated",
        "chemical_processing": "chemical_data_processed",
        "synthesis": "synthesis_completed"
    }
    
    if step_name in status_map:
        metadata["status"] = status_map[step_name]
    
    # Process new files
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} does not exist, skipping")
            continue
        
        file_name = os.path.basename(file_path)
        
        # Check if file already exists in metadata
        file_exists = False
        if "files" in metadata:
            for key, file_info in metadata["files"].items():
                if isinstance(file_info, dict) and file_info.get("path") == file_path:
                    file_exists = True
                    # Update existing file info
                    metadata["files"][key]["checksum"] = calculate_checksum(file_path)
                    metadata["files"][key]["created_at"] = get_file_modification_time(file_path)
                    break
                elif isinstance(file_info, list):
                    for item in file_info:
                        if item.get("path") == file_path:
                            file_exists = True
                            item["checksum"] = calculate_checksum(file_path)
                            item["created_at"] = get_file_modification_time(file_path)
                            break
        
        if not file_exists:
            # Add new file to appropriate category
            if step_name == "info_retrieval" and file_name.endswith(".json"):
                metadata["files"]["papers_json"] = {
                    "path": file_path,
                    "created_at": get_file_modification_time(file_path),
                    "checksum": calculate_checksum(file_path)
                }
            elif step_name == "paper_selection" and file_name.endswith(".md"):
                metadata["files"]["citations"] = {
                    "path": file_path,
                    "created_at": get_file_modification_time(file_path),
                    "checksum": calculate_checksum(file_path)
                }
            elif step_name == "full_text_retrieval" and file_name.endswith(".txt"):
                if "full_texts" not in metadata["files"]:
                    metadata["files"]["full_texts"] = []
                metadata["files"]["full_texts"].append({
                    "path": file_path,
                    "created_at": get_file_modification_time(file_path),
                    "checksum": calculate_checksum(file_path)
                })
            elif step_name == "summarization" and file_name.endswith(".md"):
                if "summaries" not in metadata["files"]:
                    metadata["files"]["summaries"] = []
                metadata["files"]["summaries"].append({
                    "path": file_path,
                    "created_at": get_file_modification_time(file_path),
                    "checksum": calculate_checksum(file_path)
                })
            elif step_name == "synthesis" and file_name.endswith(".md"):
                metadata["files"]["synthesis"] = {
                    "path": file_path,
                    "created_at": get_file_modification_time(file_path),
                    "checksum": calculate_checksum(file_path)
                }
            elif step_name == "chemical_processing" and file_name.endswith(".json"):
                metadata["files"]["chemical_data"] = {
                    "path": file_path,
                    "created_at": get_file_modification_time(file_path),
                    "checksum": calculate_checksum(file_path)
                }
    
    # Save updated metadata
    with open("research_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Updated metadata for step: {step_name}")
    print(f"New status: {metadata['status']}")
    print(f"Completed steps: {len(metadata['completed_steps'])}")
    print(f"Total files tracked: {sum(1 for f in metadata['files'].values() if isinstance(f, dict)) + sum(len(lst) for lst in metadata['files'].values() if isinstance(lst, list))}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 update_metadata.py <step_name> [file_paths...]")
        print("\nAvailable step names:")
        print("- info_retrieval")
        print("- paper_selection")
        print("- full_text_retrieval")
        print("- summarization")
        print("- chemical_processing")
        print("- synthesis")
        sys.exit(1)
    
    step_name = sys.argv[1]
    file_paths = sys.argv[2:] if len(sys.argv) > 2 else []
    
    update_metadata(step_name, file_paths)