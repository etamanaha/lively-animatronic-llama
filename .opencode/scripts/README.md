# Research Metadata Management Scripts

This directory contains scripts to help manage research projects and prevent data re-retrieval issues.

## Available Scripts

### 1. update_metadata.py

Update the research metadata file after completing a research step.

**Usage:**
```bash
python3 update_metadata.py <step_name> [file_paths...]
```

**Step names:**
- `info_retrieval` - After retrieving papers
- `paper_selection` - After selecting top papers
- `full_text_retrieval` - After downloading full texts
- `summarization` - After generating summaries
- `chemical_processing` - After processing chemical data
- `synthesis` - After creating final synthesis

**Example:**
```bash
# After retrieving full text papers
python3 update_metadata.py full_text_retrieval fulltext1.txt fulltext2.txt fulltext3.txt fulltext4.txt fulltext5.txt
```

### 2. verify_files.py

Verify that all files tracked in research_metadata.json exist and are valid.

**Usage:**
```bash
python3 verify_files.py
```

**Output:**
- Lists all tracked files with their status
- Shows checksum validation results
- Provides summary of valid/invalid files

**Example:**
```bash
python3 verify_files.py
# Output:
# Verifying files for project: amphetamine_adhd
# Status: full_texts_retrieved
# Completed steps: 3
# 
# ✓ papers_json: amphetamine_adhd_results.json (valid)
# ✓ citations: citations.md (valid)
# ✓ full_texts[0]: fulltext1.txt (valid)
# ✓ full_texts[1]: fulltext2.txt (valid)
# ...
# 
# Summary: 25/25 files valid
# ✓ All files verified successfully
```

### 3. check_resume_point.py

Determine the appropriate resume point for a research project.

**Usage:**
```bash
python3 check_resume_point.py
```

**Output:**
- Shows current project status
- Lists completed steps
- Indicates next step to perform

**Example:**
```bash
python3 check_resume_point.py
# Output:
# Project: amphetamine_adhd
# Status: full_texts_retrieved
# Completed steps: ['info_retrieval', 'paper_selection', 'full_text_retrieval']
# 
# Next step: Summarization
```

## Usage Patterns

### Typical Workflow

1. **Start a new project:**
   ```bash
   cp -r .opencode/templates/research_project_template my-project/
   cd my-project/
   # Edit template files with project-specific info
   ```

2. **After each research step, update metadata:**
   ```bash
   # After retrieving papers
   python3 ../scripts/update_metadata.py info_retrieval papers.json
   
   # After selecting papers
   python3 ../scripts/update_metadata.py paper_selection citations.md
   
   # After getting full texts
   python3 ../scripts/update_metadata.py full_text_retrieval fulltext*.txt
   ```

3. **Verify files before resuming:**
   ```bash
   python3 ../scripts/verify_files.py
   ```

4. **Check resume point if context is lost:**
   ```bash
   python3 ../scripts/check_resume_point.py
   ```

### Error Recovery

If the context window resets or you need to resume work:

```bash
# 1. Check what files exist
ls -la *.json *.md *.txt

# 2. Verify file integrity
python3 ../scripts/verify_files.py

# 3. Determine next step
python3 ../scripts/check_resume_point.py

# 4. Continue from where you left off
# (Only process files that don't exist or are invalid)
```

## Best Practices

1. **Always update metadata** after each successful step
2. **Verify files** before starting new steps
3. **Check resume point** if you're unsure where to continue
4. **Use consistent naming** for all generated files
5. **Run verification** regularly to catch issues early

## Troubleshooting

### "File not found" errors
- Ensure you're in the correct directory (where research_metadata.json is located)
- Check that the file paths in metadata are correct
- Use absolute paths if working across directories

### Checksum mismatches
- This indicates the file has been modified since it was tracked
- Either the file was accidentally changed, or it needs to be reprocessed
- Check the file content to determine if it's correct

### Missing metadata file
- Create one using the template system
- Or run the migration script for existing projects

### Script permission issues
- Make scripts executable:
  ```bash
  chmod +x scripts/*.py
  ```

## Integration with Researcher Agent

The researcher agent should be updated to:

1. **Create metadata file** at project start
2. **Update metadata** after each completed step
3. **Check file existence** before processing
4. **Use file paths** instead of loading full content into context
5. **Maintain progress logs** for transparency

This integration prevents data re-retrieval and ensures research progress is preserved across context window resets.