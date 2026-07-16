# Example Usage: Amphetamine and ADHD Research

This example demonstrates how to use the researcher agent with session memory to prevent data re-retrieval issues.

## Scenario

You want to research: "Why are amphetamines used to treat ADHD?"

This requires both:
- Chemical properties of amphetamine
- Literature on ADHD pathophysiology and treatment

## Step-by-Step Workflow

### 1. Project Setup

```bash
# Create project directory
mkdir amphetamine-adhd
cd amphetamine-adhd/

# Create progress.md
nano progress.md
```

**Updated progress.md:**
```markdown
# Research Progress: Amphetamine and ADHD

## Status: Initialized

### Completed Steps ✓

### Current Step 🔄
- Starting information retrieval

### Pending Steps
- [ ] Information retrieval
- [ ] Paper selection
- [ ] Full text retrieval
- [ ] Summarization
- [ ] Chemical data processing
- [ ] Synthesis
- [ ] Final report generation
```

### 2. Information Retrieval

```bash
# Delegate to info-fetcher agent
# "Find chemical properties of amphetamine AND literature on its mechanism of action and clinical efficacy in ADHD treatment"

# After info-fetcher completes, you should have:
# - amphetamine_adhd_results.json (contains both chemical and literature data)

# Update progress.md
nano progress.md
# Mark information retrieval as complete
```
```

### 3. Paper Selection

```bash
# Analyze the 20 papers in amphetamine_adhd_results.json
# Select the 5 most relevant papers

# Create citations.md with ACS style citations
# Example content:
# (1) Smith, J.; Jones, M. Amphetamine mechanism in ADHD. Journal of Neuroscience 2020, 45(3), 123-145.
# (2) Brown, L.; Davis, R. Clinical efficacy of amphetamine treatment. Pediatric Psychiatry 2021, 15(2), 45-67.
# ...

# Update progress.md
nano progress.md
# Mark paper selection as complete
```
```

### 4. Full Text Retrieval

```bash
# Use the appropriate skill to get full text of the 5 selected papers
# Save as: fulltext1.txt, fulltext2.txt, fulltext3.txt, fulltext4.txt, fulltext5.txt

# Update progress.md
nano progress.md
# Mark full text retrieval as complete
```
```

### 5. Summarization

```bash
# Use paper-reading skill to generate summaries
# Create: summary1.md, summary2.md, summary3.md, summary4.md, summary5.md

# If chemical data was retrieved separately, also summarize it
# Create: chemical_data.json (structured chemical properties)

# Update progress.md
nano progress.md
# Mark summarization as complete
```
```

### 6. Synthesis

```bash
# Use synthesis skill to combine all findings
# Create: synthesis.md (integrated analysis)

# Update progress.md
nano progress.md
# Mark synthesis as complete
```
```

### 7. Final Project Structure

```
amphetamine-adhd/
├── progress.md               # Human-readable progress log
├── amphetamine_adhd_results.json  # 20 retrieved papers
├── citations.md              # 5 selected papers in ACS format
├── fulltext1.txt             # Full text of paper 1
├── fulltext2.txt             # Full text of paper 2
├── fulltext3.txt             # Full text of paper 3
├── fulltext4.txt             # Full text of paper 4
├── fulltext5.txt             # Full text of paper 5
├── summary1.md               # Summary of paper 1
├── summary2.md               # Summary of paper 2
├── summary3.md               # Summary of paper 3
├── summary4.md               # Summary of paper 4
├── summary5.md               # Summary of paper 5
├── chemical_data.json        # Structured chemical properties
└── synthesis.md              # Integrated final analysis
```

## Handling Context Window Reset

### Scenario: Context window gets full during summarization

**Before context reset:**
```bash
# You've completed summaries 1-3
# Working on summary4.md when context window resets...
```

**After context reset:**

```bash
# 1. Navigate to project directory
cd amphetamine-adhd/

# 2. Check what's been completed
python3 .opencode/scripts/check_resume_point.py
# Output: Next step: Summarization

# 3. Check which summaries exist
ls -la summary*.md
# Output:
# summary1.md  summary2.md  summary3.md  summary4.md  summary5.md

# 4. Verify file integrity
python3 .opencode/scripts/verify_files.py
# Output shows all files are valid

# 5. Resume work
# The researcher agent will recognize existing summaries
# Only summary5.md needs to be completed

# 6. Update metadata when done
python3 .opencode/scripts/update_metadata.py summarization summary5.md
```

## Key Benefits Demonstrated

### 1. No Data Re-Retrieval
- Metadata tracks that papers were already retrieved
- Agent doesn't re-fetch existing data

### 2. Easy Resume
- `check_resume_point.py` shows exactly where to continue
- No need to remember what was completed

### 3. File Integrity
- Checksums ensure files haven't been corrupted
- Missing files are immediately identified

### 4. Progress Tracking
- Both machine-readable (metadata) and human-readable (progress.md)
- Clear record of what has been accomplished

### 5. Error Recovery
- If something goes wrong, easy to identify and fix
- Only missing/invalid files need reprocessing

## Comparison: Before vs After

### Before (Problematic)
```
1. Context window fills up
2. Agent loses track of existing files
3. Data gets re-retrieved unnecessarily
4. Duplicate work performed
5. Hard to resume from interruptions
```

### After (Solution)
```
1. Context window fills up
2. Agent checks research_metadata.json
3. Recognizes existing files
4. Only processes missing files
5. Easy to resume from any point
```

## Real-World Example

Looking at your existing research in `amphetamines-and-adhd/`:

```bash
# This directory already has the structure we want!
cd amphetamines-and-adhd/

# But it's missing the metadata system
# Let's add it:

# 1. Create metadata file
cp .opencode/templates/research_project_template/research_metadata.json .
# Edit with your project details

# 2. Create progress file
cp .opencode/templates/research_project_template/progress.md .
# Edit with your progress details

# 3. Update metadata with existing files
python3 .opencode/scripts/update_metadata.py info_retrieval amphetamine_adhd_results.json
python3 .opencode/scripts/update_metadata.py paper_selection citations.md
python3 .opencode/scripts/update_metadata.py full_text_retrieval fulltext*.txt
python3 .opencode/scripts/update_metadata.py summarization summary*.md
python3 .opencode/scripts/update_metadata.py synthesis synthesis.md

# 4. Verify everything is tracked
python3 .opencode/scripts/verify_files.py

# Now you have the same protection against data re-retrieval!
```

This example shows exactly how the new system prevents the issues you were experiencing.