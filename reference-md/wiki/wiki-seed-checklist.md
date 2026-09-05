<a id="d14-completion-checklist"></a>
## D14. Completion Checklist

Use this checklist to determine whether initial wiki seeding is complete enough to support retrieval, routing, early synthesis, and verification. Mark an item complete only when the condition is satisfied in the wiki itself, not merely planned.

<a id="d141-core-structural-coverage"></a>
### D14.1 Core Structural Coverage

- [ ] The wiki contains the required top-level categories and index pages needed for navigation.
- [ ] The wiki contains a master index that links to all major seeded categories.
- [ ] Each seeded top-level category has at least one navigable index or generated entry point.
- [ ] Seeded pages use valid front matter, stable IDs, stable slugs, and an approved `page_type`.
- [ ] Seeded pages are placed in the correct top-level category according to canonical purpose.

<a id="d142-minimum-domain-spine"></a>
### D14.2 Minimum Domain Spine

- [ ] High-value concept pages exist for the core interpretive terms the agent will repeatedly encounter.
- [ ] Core method and model pages exist for the major computational toxicology approaches the agent will need for relevance judgment.
- [ ] Major dataset pages exist for the principal public resources likely to anchor downstream analysis.
- [ ] Major assay-family pages exist for the assay systems most likely to appear in literature and evidence review.
- [ ] Major endpoint pages exist for the toxicological outcomes most likely to recur in target workflows.
- [ ] Core biology pages exist for the principal targets, pathways, tissues, or species needed to interpret the seeded chemicals, assays, and endpoints.
- [ ] A small sentinel set of chemical pages exists and exercises cross-category linking across concepts, endpoints, assays, datasets, and biology.

<a id="d143-page-level-usability"></a>
### D14.3 Page-Level Usability

- [ ] Every seeded canonical page contains a short overview and a clear scope section.
- [ ] Every seeded canonical page contains at least one substantive, toxicology-specific claim, definition, or structured fact worth retrieving.
- [ ] Pages avoid generic textbook filler and emphasize domain-specific usage, interpretation, caveats, or operational relevance.
- [ ] Pages that depend on recurring synonyms or alternate names include aliases or equivalent retrieval support.
- [ ] Pages that summarize evidence link to the more canonical or evidence-bearing pages rather than duplicating unsupported prose.

<a id="d144-citation-and-provenance-readiness"></a>
### D14.4 Citation and Provenance Readiness

- [ ] Every substantive seeded claim has at least one source citation or a clearly linked evidence/source page.
- [ ] Citations are sufficiently complete to resolve source identity later during verification.
- [ ] Source-oriented pages exist where needed to preserve provenance for major reviews, reports, or datasets.
- [ ] Durable concepts and normalized facts have been routed to canonical pages rather than left only in source pages.

<a id="d145-cross-linking-and-retrieval-quality"></a>
### D14.5 Cross-Linking and Retrieval Quality

- [ ] Each seeded page links to the most relevant neighboring pages in at least one other top-level category.
- [ ] Concept pages link outward to relevant methods, assays, datasets, endpoints, workflows, or chemicals where applicable.
- [ ] Chemical pages link to relevant endpoints, assays, datasets, biology, and evidence pages where applicable.
- [ ] Endpoint pages link to relevant assays, biology, chemicals, and evidence types where applicable.
- [ ] Methods and dataset pages link to the concepts and workflows needed to interpret or use them correctly.
- [ ] Navigation from an index page to a canonical page works without requiring full-text search.
- [ ] Multi-hop retrieval is possible for at least a few sentinel queries that cross concepts, evidence, and entities.

<a id="d146-redundancy-control"></a>
### D14.6 Redundancy Control

- [ ] Seeded pages store toxicology-specific meaning, constraints, and interpretation rules rather than generic background the model likely already knows.
- [ ] Generic scientific concepts are rewritten around computational toxicology usage, edge cases, and decision relevance.
- [ ] Canonical content is not duplicated across multiple top-level categories without a clear reason.
- [ ] Index pages remain navigational and do not become the sole home of substantive scientific claims.

<a id="d147-operational-readiness"></a>
### D14.7 Operational Readiness

- [ ] The wiki contains the governance pages needed to enforce evidence standards, citation rules, and review expectations.
- [ ] The wiki contains the workflow pages needed for the early repeated tasks the system is expected to perform.
- [ ] The seeded content is sufficient for the agent to decide whether newly encountered information is in-scope, out-of-scope, or needs a new page.
- [ ] The seeded content is sufficient for the agent to place new information onto an existing canonical page in common cases.

<a id="d148-verification-readiness"></a>
### D14.8 Verification Readiness

- [ ] Seeded pages are written in a way that allows claim-level verification rather than only prose-level interpretation.
- [ ] Claims are scoped enough to compare across sources without major rewriting.
- [ ] Pages contain open questions or review notes where uncertainty, ambiguity, or unresolved disagreement remains.
- [ ] The seeded corpus is structured well enough for later contradiction checks within pages and across pages.

<a id="d149-completion-gate"></a>
### D14.9 Completion Gate

Treat initial seeding as successfully complete only when all of the following are true.

- [ ] The wiki has a coherent cross-linked spine across concepts, methods, datasets, assays, endpoints, biology, workflows, governance, and sentinel chemicals.
- [ ] Canonical pages are retrievable through indices and internal links rather than depending on ad hoc search.
- [ ] The seeded content materially improves technical definition lookup and relevance judgment for computational toxicology tasks.
- [ ] The seeded content minimizes redundancy with general model knowledge and concentrates on field-specific value.
- [ ] The wiki is ready for incremental expansion, verification, and synthesis without requiring structural rework first.
