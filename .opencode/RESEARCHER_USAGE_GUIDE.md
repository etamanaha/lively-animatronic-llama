# Researcher Agent Usage Guide

This guide explains how to use the researcher agent effectively to prevent data re-retrieval issues when the context window gets full.

## Overview

The researcher agent now includes a robust file tracking system that prevents unnecessary data re-retrieval. This guide covers:

1. **Project Setup** - How to start new research projects
2. **Workflow Execution** - Step-by-step research process
3. **Context Management** - Handling context window resets
4. **Error Recovery** - Resuming after interruptions
5. **Best Practices** - Tips for successful research

## Project Setup

### For New Projects

1. **Create project directory:**
   ```bash
   mkdir my-research-project
   cd my-research-project/
   ```

2. **Create progress.md:**
   ```bash
   nano progress.md
   ```
   
   Add content like:
   ```markdown
   # Research Progress: Amphetamine and ADHD
   
   ## Status: Initialized
   
   ### Completed Steps ✓
   
   ### Current Step 🔄
   - Starting information retrieval
   ```

3. **Start the research workflow:**
   - The researcher agent will track progress in session memory

### For Existing Projects

If you have existing research:

```bash
# Navigate to your existing project directory
cd existing-research-project/

# Create progress.md if it doesn't exist
nano progress.md

# Update progress.md with completed steps
```

## Workflow Execution

### Step 1: Information Retrieval

```bash
# Delegate to info-fetcher agent to retrieve papers
# This creates papers.json with 20 papers

# After successful retrieval, update progress.md
nano progress.md
# Mark information retrieval as complete
```

### Step 2: Paper Selection

```bash
# Select top 5 papers and create citations.md
# This file contains ACS style citations

# Update progress.md after creating citations
nano progress.md
# Mark paper selection as complete
```

### Step 3: Full Text Retrieval

```bash
# Retrieve full text of selected papers (fulltext1.txt, etc.)

# Update progress.md for all retrieved files
nano progress.md
# Mark full text retrieval as complete
```

### Step 4: Summarization

```bash
# Generate summaries for each paper (summary1.md, etc.)

# Update progress.md for summaries
nano progress.md
# Mark summarization as complete

# If chemical data was retrieved, also summarize it
```

### Step 5: Synthesis

```bash
# Create final synthesis combining all findings

# Update progress.md for synthesis
nano progress.md
# Mark synthesis as complete

# Research is now complete!
```

## Context Management

### Preventing Data Re-Retrieval

The researcher agent now checks for existing files before processing:

1. **Before each step**, the agent checks:
   - Does the metadata file exist?
   - Are the required files already present?
   - Are the files valid (checksum matches)?

2. **If files exist and are valid**, the agent skips re-processing
3. **If files are missing or invalid**, the agent processes them

### Example: Safe Context Reset

If the context window resets during research:

```bash
# 1. Check what files exist
ls -la *.json *.md *.txt

# 2. Verify file integrity
python3 .opencode/scripts/verify_files.py

# 3. Determine next step
python3 .opencode/scripts/check_resume_point.py

# 4. Resume from where you left off
# The researcher agent will recognize existing files
```

## Error Recovery

### Scenario: Context Window Reset

**Problem:** You were in the middle of summarization when the context window reset.

**Solution:**
```bash
# 1. Navigate to your project directory
cd my-research-project/

# 2. Check what's been completed
cat progress.md

# 3. Check which summaries already exist
ls -la summary*.md

# 4. Continue summarizing only missing files
# (The researcher agent will skip existing summaries)
```

### Scenario: Corrupted Files

**Problem:** Some files were corrupted or accidentally deleted.

**Solution:**
```bash
# 1. Check progress.md to identify what should exist
cat progress.md

# 2. Re-process only the problematic files
# (The researcher agent will recognize existing valid files)
```

### Scenario: Starting from Scratch

**Problem:** You need to start a new research project.

**Solution:**
```bash
# 1. Create a new project directory
cp -r .opencode/templates/research_project_template new-project/
cd new-project/

# 2. Configure the template files
# 3. Start the research workflow from Step 1
```

## Best Practices

### File Management

1. **Use consistent naming:**
   - Papers: `papers.json`
   - Citations: `citations.md`
   - Full texts: `fulltext1.txt`, `fulltext2.txt`, etc.
   - Summaries: `summary1.md`, `summary2.md`, etc.
   - Synthesis: `synthesis.md`
   - Chemical data: `chemical_data.json`

2. **Keep files organized:**
   ```
   my-research-project/
   ├── research_metadata.json
   ├── progress.md
   ├── papers.json
   ├── citations.md
   ├── fulltext1.txt
   ├── fulltext2.txt
   ├── summary1.md
   ├── summary2.md
   ├── synthesis.md
   └── chemical_data.json
   ```

3. **Update metadata regularly:**
   - After each successful step
   - Before starting new steps
   - When files are modified

### Context Optimization

1. **Minimize context usage:**
   - Store file paths, not file contents
   - Reference files by path when needed
   - Use checksums for validation

2. **Keep metadata in context:**
   - The `research_metadata.json` file is your persistent record
   - Load it at the start of each session
   - Update it after each step

3. **Use progress logs:**
   - Maintain `progress.md` for human-readable status
   - Update it alongside metadata
   - Review it to understand project status

### Research Workflow

1. **Plan thoroughly:**
   - Define research questions clearly
   - Identify required data types (chemical, literature)
   - Estimate time and resources needed

2. **Document progress:**
   - Update both metadata and progress logs
   - Add notes about decisions and findings
   - Track any issues encountered

3. **Verify regularly:**
   - Run `verify_files.py` after major steps
   - Check `check_resume_point.py` before resuming
   - Review `progress.md` for context

## Troubleshooting

### Common Issues and Solutions

**Issue: Data keeps getting re-retrieved**
- **Cause:** Metadata not being updated or checked
- **Solution:** Always run `update_metadata.py` after each step

**Issue: Files show as missing but they exist**
- **Cause:** File paths in metadata don't match actual files
- **Solution:** Check file paths in `research_metadata.json`

**Issue: Checksum mismatches**
- **Cause:** Files were modified after being tracked
- **Solution:** Re-process the modified files

**Issue: Can't determine resume point**
- **Cause:** Metadata file is incomplete or corrupted
- **Solution:** Recreate metadata based on existing files

**Issue: Scripts not working**
- **Cause:** Permission issues or Python not available
- **Solution:** Make scripts executable with `chmod +x scripts/*.py`

## Advanced Usage

### Custom Metadata Fields

You can add custom fields to `research_metadata.json`:

```json
{
  "project_name": "custom_project",
  "created_at": "2026-07-15T10:00:00Z",
  "custom_fields": {
    "research_questions": [
      "What is the mechanism of action?",
      "What are the clinical implications?"
    ],
    "key_findings": [],
    "notes": "Important: Focus on recent studies (2020+)"
  },
  "files": {},
  "completed_steps": [],
  "status": "initialized"
}
```

### Multiple Data Sources

For complex research requiring multiple data types:

```json
{
  "configuration": {
    "requires_chemical_data": true,
    "requires_literature_data": true,
    "data_sources": [
      {
        "type": "chemical",
        "source": "ChEMBL",
        "compounds": ["amphetamine", "methylphenidate"]
      },
      {
        "type": "literature",
        "source": "PubMed",
        "keywords": ["ADHD", "treatment", "mechanism"]
      }
    ]
  }
}
```

### Team Collaboration

For shared research projects:

```bash
# Commit metadata and files to version control
git add research_metadata.json progress.md *.json *.md *.txt
git commit -m "Research progress update"

# Pull updates from team members
git pull origin main

# Verify all files are still valid
python3 .opencode/scripts/verify_files.py
```

## Integration with Other Agents

### Info-Fetcher Agent

The info-fetcher agent should:
- Create `papers.json` with retrieved papers
- Update metadata after completion
- Handle both chemical and literature data as needed

### Paper-Reading Skill

The paper-reading skill should:
- Process files referenced by path (not loaded into context)
- Generate summaries with consistent naming
- Update metadata after generating each summary

### Synthesis Skill

The synthesis skill should:
- Reference all source files by path
- Combine findings into coherent output
- Update metadata with final synthesis file

## Summary

By following this guide, you should be able to:

1. **Start new research projects** with proper tracking
2. **Execute research workflows** without data re-retrieval
3. **Handle context window resets** gracefully
4. **Recover from errors** quickly
5. **Maintain research consistency** across projects

The key to preventing data re-retrieval is the metadata system - always update it after each step and check it before starting new work.