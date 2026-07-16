#!/usr/bin/env python3
"""
Script to verify that all files tracked in research_metadata.json exist and are valid.

Usage:
    python3 verify_files.py
"""

import json
import os
import hashlib
import sys

def calculate_checksum(filepath):
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def verify_files():
    """Verify all files tracked in metadata."""
    
    # Check if metadata file exists
    if not os.path.exists("research_metadata.json"):
        print("Error: research_metadata.json not found in current directory")
        sys.exit(1)
    
    # Load metadata
    with open("research_metadata.json", "r") as f:
        metadata = json.load(f)
    
    print(f"Verifying files for project: {metadata.get('project_name', 'Unknown')}")
    print(f"Status: {metadata.get('status', 'Unknown')}")
    print(f"Completed steps: {len(metadata.get('completed_steps', []))}")
    print()
    
    all_valid = True
    total_files = 0
    valid_files = 0
    
    if "files" in metadata:
        for key, file_info in metadata["files"].items():
            if isinstance(file_info, dict):
                total_files += 1
                file_path = file_info.get("path")
                if file_path:
                    if os.path.exists(file_path):
                        current_checksum = calculate_checksum(file_path)
                        stored_checksum = file_info.get("checksum")
                        
                        if current_checksum == stored_checksum:
                            print(f"✓ {key}: {file_path} (valid)")
                            valid_files += 1
                        else:
                            print(f"✗ {key}: {file_path} (checksum mismatch)")
                            print(f"  Expected: {stored_checksum}")
                            print(f"  Actual:   {current_checksum}")
                            all_valid = False
                    else:
                        print(f"✗ {key}: {file_path} (missing)")
                        all_valid = False
            elif isinstance(file_info, list):
                for i, item in enumerate(file_info):
                    total_files += 1
                    file_path = item.get("path")
                    if file_path:
                        if os.path.exists(file_path):
                            current_checksum = calculate_checksum(file_path)
                            stored_checksum = item.get("checksum")
                            
                            if current_checksum == stored_checksum:
                                print(f"✓ {key}[{i}]: {file_path} (valid)")
                                valid_files += 1
                            else:
                                print(f"✗ {key}[{i}]: {file_path} (checksum mismatch)")
                                print(f"  Expected: {stored_checksum}")
                                print(f"  Actual:   {current_checksum}")
                                all_valid = False
                        else:
                            print(f"✗ {key}[{i}]: {file_path} (missing)")
                            all_valid = False
    
    print()
    print(f"Summary: {valid_files}/{total_files} files valid")
    
    if all_valid:
        print("✓ All files verified successfully")
        return 0
    else:
        print("✗ Some files are missing or corrupted")
        return 1

if __name__ == "__main__":
    sys.exit(verify_files())