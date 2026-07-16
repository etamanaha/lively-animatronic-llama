# Researcher Agent Quick Reference

## Preventing Data Re-Retrieval

### 1. Start a New Project
```bash
mkdir my-project
cd my-project/
# Create progress.md
nano progress.md
```

### 2. After Each Step - Update Progress
```bash
# Update progress.md manually to mark steps as complete
nano progress.md
```

### 3. Check Status Before Resuming
```bash
# Check progress.md to see what's been completed
cat progress.md
```

## Common Commands

### Check Progress
```bash
cat progress.md
```

### Update Progress
```bash
nano progress.md
```

## Step Names

- Information retrieval - After retrieving papers
- Paper selection - After selecting top papers  
- Full text retrieval - After downloading full texts
- Summarization - After generating summaries
- Chemical processing - After processing chemical data
- Synthesis - After creating final synthesis

## File Naming Convention

- **Papers:** `papers.json`
- **Citations:** `citations.md`
- **Full texts:** `fulltext1.txt`, `fulltext2.txt`, etc.
- **Summaries:** `summary1.md`, `summary2.md`, etc.
- **Synthesis:** `synthesis.md`
- **Chemical data:** `chemical_data.json`

## Directory Structure

```
my-research-project/
├── progress.md               # Human-readable progress
├── papers.json               # Retrieved papers
├── citations.md              # ACS citations
├── fulltext1.txt             # Paper full texts
├── summary1.md               # Paper summaries
├── synthesis.md              # Final synthesis
└── chemical_data.json        # Chemical properties
```

## Troubleshooting

### Data keeps re-retrieving?
```bash
# Make sure you updated progress.md after each step
nano progress.md
```

### Can't find resume point?
```bash
cat progress.md
```

### Files show as missing?
```bash
# Verify files exist with ls -la
```

### Checksum mismatches?
```bash
# File was modified after being tracked
# Re-process the modified file
```

## Best Practices

✓ **Always update progress.md** after each step  
✓ **Verify files** before starting new work  
✓ **Use consistent naming** for all files  
✓ **Check progress.md** if unsure where to continue  

✗ **Don't load file contents** into context  
✗ **Don't skip progress updates**  
✗ **Don't rename tracked files** without updating progress.md  

## Quick Start Example

```bash
# 1. Create project
mkdir amphetamine-adhd
cd amphetamine-adhd/

# 2. Create progress.md
nano progress.md

# 3. Run research workflow
# (Delegate to info-fetcher, etc.)

# 4. Update progress.md after each step
nano progress.md

# 5. Check progress
cat progress.md

# 6. Continue research...
```

## Need Help?

- See `RESEARCHER_USAGE_GUIDE.md` for detailed instructions
- See `researcher.md` for agent workflow details
- See `.opencode/scripts/README.md` for script documentation