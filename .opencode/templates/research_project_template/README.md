# Research Project Template

This template provides the structure for new research projects to ensure consistency and prevent data re-retrieval issues.

## Usage

1. **Copy this template** to a new directory for your research project:
   ```bash
   cp -r .opencode/templates/research_project_template my-research-project/
   ```

2. **Rename files** to match your project:
   - Replace `REPLACE_WITH_PROJECT_NAME` in all template files
   - Update timestamps in `research_metadata.json`

3. **Update metadata** in `research_metadata.json`:
   - Set `project_name` to your research topic
   - Configure `paper_count` and `selected_papers` as needed
   - Set `requires_chemical_data` and `requires_literature_data` flags

4. **Follow the workflow** in the researcher agent documentation

## File Structure

```
my-research-project/
├── research_metadata.json    # Tracks all files and progress
├── progress.md               # Human-readable progress tracking
├── README.md                 # This file
├── papers.json               # Will contain retrieved papers
├── citations.md              # Will contain ACS citations
├── fulltext1.txt             # Will contain paper full texts
├── summary1.md               # Will contain paper summaries
├── synthesis.md              # Will contain final synthesis
└── chemical_data.json        # Will contain chemical properties (if applicable)
```

## Benefits

- **Prevents data re-retrieval**: Clear tracking of existing files
- **Context window management**: Minimizes context usage by tracking file paths
- **Error recovery**: Easy to resume from context loss
- **Consistency**: Standardized structure across all research projects
- **Documentation**: Built-in progress tracking and notes

## Best Practices

1. **Always update metadata** after each step
2. **Use consistent naming** for all generated files
3. **Check file existence** before re-processing
4. **Maintain progress logs** for transparency
5. **Validate files** using checksums when resuming