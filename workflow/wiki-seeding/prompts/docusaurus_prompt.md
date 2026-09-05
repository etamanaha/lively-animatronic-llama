## Description

You create the Docusaurus folder structure and category files for the computational toxicology wiki.

### DOCUSAURUS PAGES include ONLY
- intro.md
- docusaurus.config.ts
- package.json
- sidebars.ts
- _category_.json for each category folder

You MUST create ALL these files. DO NOT create additional files.

### Requirements

- Determine which Docusaurus files must be created from the specification below.
- Call `upsert_file` once for every file.
- Each file must be a separate `upsert_file` call.
- Generate complete, valid file contents.
- Do not omit required files.
- After all requested tool calls have been issued, provide a brief completion message.

## D6. Docusaurus Structure and Logistics

### D6.1 Top-Level Wiki Structure

When seeding the wiki, ensure this structure is adhered to and that all referenced subfolders and pages are created according to this document.

```text
./wiki/docs
  /00-system
  /01-indices
  /02-concepts
  /03-chemicals
  /04-biology
  /05-toxicological-endpoints
  /06-assays
  /07-datasets
  /08-models-and-methods
  /09-literature
  /10-evidence
  /11-workflows
  /12-agent-operations
  /13-projects
  /14-quality-and-governance
  /15-glossary
```

Use `10-evidence` as the canonical folder name. If legacy instructions refer to `10_evidence`, normalize them to `10-evidence`.

### D6.2 Recommended Repository Layout

The conceptual wiki structure should be implemented with a Docusaurus-compatible filesystem layer. Use Markdown or MDX files under the Docusaurus `docs/` directory, filesystem-safe filenames, front matter, category metadata, relative links, and Mermaid configuration.

```text
./wiki/
  docusaurus.config.ts
  sidebars.ts
  package.json
  docs/
    intro.md
    00-system/
      _category_.json
      wiki-mission-and-scope.md
      computational-toxicology-system-overview.md
      agent-roles-and-capabilities.md
    01-indices/
      _category_.json
      master-index.md
      chemical-index.md
      toxicological-endpoint-index.md
      assay-index.md
      dataset-index.md
      model-index.md
      literature-index.md
      evidence-claim-index.md
      agent-workflow-index.md
    02-concepts/
      _category_.json
      hazard.md
      risk.md
      exposure.md
      qsar.md
      applicability-domain.md
      weight-of-evidence.md
      adverse-outcome-pathway.md
    03-chemicals/
      _category_.json
    04-biology/
      _category_.json
      targets/
        _category_.json
      pathways/
        _category_.json
      species/
        _category_.json
    05-toxicological-endpoints/
      _category_.json
    06-assays/
      _category_.json
    07-datasets/
      _category_.json
      chembl.md
      comptox-chemicals-dashboard.md
      pubchem.md
      tox21.md
      toxcast.md
      pubmed.md
    08-models-and-methods/
      _category_.json
      qsar-models.md
      read-across.md
      pbpk-modeling.md
      qivive.md
    09-literature/
      _category_.json
      papers/
        _category_.json
      reviews/
        _category_.json
      regulatory-reports/
        _category_.json
    10-evidence/
      _category_.json
      evidence-table-template.md
      contradiction-register.md
    11-workflows/
      _category_.json
      literature-review-workflow.md
      chemical-hazard-assessment-workflow.md
      dataset-profiling-workflow.md
      in-silico-assay-workflow.md
    12-agent-operations/
      _category_.json
      agent-task-template.md
      tool-invocation-record.md
      model-execution-record.md
      audit-log.md
    13-projects/
      _category_.json
      active-project-index.md
    14-quality-and-governance/
      _category_.json
      evidence-standards.md
      citation-and-provenance-rules.md
      human-review-checkpoints.md
      responsible-use-policy.md
    15-glossary/
      _category_.json
      glossary.md
```

### D6.3 Category Files

Each folder should include a `_category_.json` file so Docusaurus can display clean sidebar categories.

Example:

```json
{
  "label": "Chemicals",
  "position": 3,
  "link": {
    "type": "generated-index",
    "description": "Chemical entity pages, including substances, mixtures, metabolites, and chemical classes."
  }
}
```

Top-level category ordering:

| Position | Folder | Label |
|---:|---|---|
| 0 | `00-system` | System |
| 1 | `01-indices` | Indices |
| 2 | `02-concepts` | Concepts |
| 3 | `03-chemicals` | Chemicals |
| 4 | `04-biology` | Biology |
| 5 | `05-toxicological-endpoints` | Toxicological Endpoints |
| 6 | `06-assays` | Assays |
| 7 | `07-datasets` | Datasets |
| 8 | `08-models-and-methods` | Models and Methods |
| 9 | `09-literature` | Literature |
| 10 | `10-evidence` | Evidence |
| 11 | `11-workflows` | Workflows |
| 12 | `12-agent-operations` | Agent Operations |
| 13 | `13-projects` | Projects |
| 14 | `14-quality-and-governance` | Quality and Governance |
| 15 | `15-glossary` | Glossary |

### D6.4 Sidebar Strategy

For the initial wiki, use Docusaurus autogenerated sidebars and curate only the most important landing pages manually.

Example `sidebars.ts`:

```ts
import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  wikiSidebar: [
    'intro',
    {
      type: 'autogenerated',
      dirName: '.',
    },
  ],
};

export default sidebars;
```

As the wiki matures, curated sidebars can be added for chemicals, endpoints, assays, workflows, and evidence claims.

<a id="d65-mermaid-concept-map-support"></a>
### D6.5 Mermaid Concept Map Support

The concept map uses Mermaid. To render it in Docusaurus, enable Mermaid in `docusaurus.config.ts`.

```ts
import type {Config} from '@docusaurus/types';
import {themes as prismThemes} from 'prism-react-renderer';

const config: Config = {
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
  themeConfig: {
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
};

export default config;
```

### D6.6 Build Validation

Before using the wiki as an operational knowledge substrate, validate the site locally.

```bash
npm install
npm run start
npm run build
```

The build should fail on broken links if `onBrokenLinks: 'throw'` is configured. Broken links indicate retrieval and provenance problems for both humans and agents.

<a id="d67-compatibility-principle"></a>
### D6.7 Compatibility Principle

The Docusaurus layer should not replace the knowledge model. It is an implementation wrapper around the same atomic, linked, evidence-centered wiki. Pages should remain agent-operable through structured front matter and consistent sections, while Docusaurus provides navigation, rendering, search, and publishing.

