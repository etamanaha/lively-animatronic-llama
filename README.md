# Adverse Outcome Pathway (AOP) Prediction Workflow

## Overview
This project provides a computational workflow for predicting Adverse Outcome Pathways (AOPs) for small molecules. It integrates multiple specialized components to create a comprehensive system for toxicology assessment:

1. **Wiki Seeding**: Establishes a foundational knowledge base with structured toxicology information
2. **RAG Ingestion**: Processes and indexes scientific literature for retrieval-augmented generation
3. **AOP Prediction**: Predicts adverse outcome pathways through similarity scoring, and aop wiki queries

The system combines literature review, in silico toxicology, and adverse-outcome pathway analysis to provide a workflow for computational toxicology assessment.

## Wiki Seeding

### Overview

Wiki seeding establishes a foundational knowledge base containing structured toxicology information organized for Docusaurus. The resulting pages provide a reference framework that can be expanded and enriched during RAG ingestion.

### Workflow Components

1. **Supervisor Node** (`workflow.py`)
   - Orchestrates the entire workflow
   - Selects the next step
- Tracks completion and execution status

2. **Docusaurus Node** (`workflow.py`)
   - Creates Docusaurus configuration files
   - Sets up folder structure and category files
   - Generates `intro.md`, `docusarus.config.ts`, `package.json`, `sidebar.ts`

3. **Info Pages Node** (`info_node.py`)
   - Creates governance and operational pages
   - Handles workflow, agent operations, and quality pages
   - Uses `info_prompt.md` for guidance

4. **Core Pages Node** (`core_node.py`)
   - Create content pages for concepts, chemicals, biology, and related topics.
   - Performs literature research through Europe PMC (`europepmc.py`)
   - Uses `core_prompt.md` for guidance

5. **Index Pages Node** (`workflow.py`) 
   - Creates navigation pages in `01-indices` 
   - Links to canonical content pages

### Reference Files

#### Prompts

- `docusaurus_prompt.md`: Instructions for Docusaurus structure
- `info_prompt.md`: Guidelines for info page creation
- `core_prompt.md`: Instructions for core page creation
- `supervisor_prompt.md`: Decision-making rules for supervisor

#### Reference Documentation
- `specs.md`: Structural rules for all wiki pages
- `categories.md`: Descriptions of each category
- `wiki-seed-overview.md`: High-level overview of the process
- `wiki-seed-outline.md`: Detailed outline of all pages
- `wiki-seed-checklist.md`: Completion checklist

#### Scripts
- `workflow.py`: Main workflow orchestrator with supervisor logic
- `info_node.py`: Info pages creation workflow
- `core_node.py`: Core pages creation workflow
- `helper_functions.py`L Shared utilities and file operations
- `europepmc.py`: Europe PMC literature search 

### Expected Output
The wiki is created in`./wiki/docs/` and includes:
- Lowercase kebab-case folders and filenames
- Markdown or MDX pages
- `_category_.json` files for Docusaurus
- Stable front matter for all pages
- Relative links between pages
- Mermaid support for diagrams

### Prerequisites
To run this code, 
- Python 3.10+
- The installation of langgraph and langchain

The code uses ChatOpenAI
```bash
pip install -U langchain langchain-openai
```
An API key for the configured OpenAI-compatible model

Create a local `.env` file in the project root:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_name
```
The model name is not a credential, but storing it in an environment variable makes it easy to change without modifying code. 

Install the project dependencies, activate the environment, configure `.env`, and run:
```bash
python workflow.py
```

## RAG ingestion

We use a hybrid approach for RAG combining a VectorDB + Knowledge Graph system (LightRAG) for factual knowledge with an LLM wiki for conceptual and procedural knowledge.

### RAG-ingest Workflow

1. PDF documents are supplied as input to the system (either manually or from e.g. a researcher agent). They should be categorized into subdirectories based on one of four ingestion strategies:

   **Strategy A - Structural Decomposition** applies to textbooks. Because the source already has an author-imposed hierarchy of chapters and sections, less work needs to be done to organize the extracted claims.

   **Strategy B - Argument-centric Extraction** For review and survey papers. Since these documents tend to be more high-level, some new concepts may be extracted but the main value is in the narrative or argument being made in the paper.

   **Strategy C - Mechanism or Case Extraction** For primary/technical papers. Information extracted from these documents will be more precise and factual, mostly going into LightRAG and being distilled for wiki ingestion.

   **Strategy D - Definitional/Procedural Extraction** For guidance documents. These documents encode formal, regulator-sanctioned definitions and decision procedures that will need to be cited precisely and consistently.

2. The documents are processed by Docling into two types or artifacts: full-text files (`.md` with a `.txt` fallback) and chunked ingestion streams (`.jsonl`). The ingestion streams are processed by a Python script which attempts to remove junk artifacts from the PDF extraction process (e.g. mojibake, contentless chunks, etc.)

3. The full-text files are ingested as-is to LightRAG, as that system will handle chunking and extraction.

4. The wiki branch has several steps to distribute the responsibilities and keep context relatively clean
   1. The ingestion stream is sent to an agentic node which cleans it up for ingestion. The agent ensures reasonable boundaries between chunks (e.g. not ending in the middle of a sentence)
   2. The cleaned-up stream is sent to an agentic node which extracts claims from the ingestion stream and comes up with a plan for which pages to edit and/or create. This plan is passed to the next step as a report
   3. The plan is implemented by a wiki-writing agent which has rules for formatting of the indicidual pages as well as a spec documenting the structure of the wiki as a whole
   4. A wiki-verification agent reads over all edited pages and ensures there are no contradictions within the page, across pages, or with the LightRAG stores. It also checks to make sure claims are backed up by known sources, going back to check original text extractions.

### Expected Output from RAG Ingestion

Claims extracted by the LightRAG node are placed into databases running in storage containers. The wiki branch of the workflow produces as its primary output edits to the wiki itself. Byproducts include various logs and reports detailing all changes made to the document from initial text extraction through wiki verification. These are meant to be used by agents, but are often human-redable.

### Installing RAG Ingetstion

To run the RAG ingest, you must first ensure the environment is properly set up and configured. The ingestion relies on:

1. A running OpenCode 2 instance (local)
2. A running LightRAG server (local)
3. A LightRAG MCP server (local)
4. An embedding model (local or remote)
5. A binding model (local or remote)
6. Storage containers (local or remote)
   - Neo4J
   - MongoDB
   - Qdrant

We chose OpenCode 2 for this project since it is more fit for this use case (running agents from within a LangGraph workflow) than v1 OpenCode. A partial opencode configuration file (`opencode.json`) is available in this repository. You will need to edit it to include the LLM provider(s) you use. Currently, OpenCode 2 is in beta, but it can be installed via shell script:

```bash 
curl -fsSL https://opencode.ai/v2/install | bash
```

LightRAG depends on an embedding model for its VectorDB serach / insertion. Since the model is small, we run it locally through Ollama.

```bash
ollama pull nomic-embed-text
```

We use the same model for our agents as we do for the LightRAG binding model. You should hook the system into whatever you prefer to use. You must update teh `lightrag_wrapper.py` file and/or the related `config.yaml` file with your personal endpoints and API key if necessary.

A `requirements.txt` file exists for setting up your preferred Python environment.

A `docker-compose.yml` file exists for running the storage containers such that the LightRAG instances can find them. Cur

Run the `makedirs.sh` script to create all relevant directories that workflows expect to exist.

```bash
cd lively-animatronic-llama
bash makedirs.sh
```

### Running RAG Ingestion

It is not possible to run an OpenCode 2 server without a password, so a default password is included in the run command:

```bash
OPENCODE_SERVER_PASSWORD=alpine opencode2 serve --hostname 127.0.0.1 --port 4096
```

Start up the storage containers through Docker:

```bash
cd lively-animatronic-llama/workflows/RAG-ingest
docker compose up -d 
```

The LightRAG server can be initialized by running the `lightrag_wrapper.py` script directly:

```bash
cd lively-animatronic-llama
PYTHONPATH=workflows python workflows/RAG-ingest/lightrag_wrapper.py
```

As long as the MCP server points to this LightRAG instance, you can use any solution. We use Lalit Suryan's server:

```bash
npx @g99/lightrag-mcp-server
```

On Windows and Mac, your Ollama server may already be running by default, but to start it up manually, use:

```bash
OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

Once all of the required services / servers are running, the workflow can be run:

```bash
cd lively-animatronic-llama
PYTHONPATH=workflows python workflows/RAG-ingest/workflow.py
```

## AOP prediction

AOP prediction is the main toxicology reasoning component of the project. It takes a chemical input and builds a candidate Adverse Outcome Pathway by combining ADMET analysis, CTX-based read-across, similarity scoring, iterative pathway expansion, and critic review. The workflow is designed to be iterative and evidence-driven: it should continue when the pathway is still under-supported and stop when the evidence is insufficient or the pathway is complete. It assembles evidence into a structured MIE -> KE -> KE -> AO pathway, with the number of KEs varying based on pathway reasonability.

### Key agents and skills used
- `admet-mie` — Calculates ADMET scores of chemicals and predicts possible MIEs (for first pathway step)
- `aop-expert` — Queries the aop xml database to map potential KEs and AOs
- `admet-ai-scoring` — identifies core ADMET properties and likely mechanistic liabilities.
- `admet-secondary-scoring` — provides a secondary ADMET pass for extra coverage.
- `confidence-scoring` — estimates pathway reliability and confidence.
- `mie-identification` — maps ADMET signals to likely Molecular Initiating Events.
- `similarity-scoring` — ranks candidates based on overlap with the target profile and read-across support.
For best results, the workflow also expects:
- A resolved chemical name or structure
- Read-across-friendly analogs when available
- At least some mechanistic evidence from ADMET or literature
- Proper environment variables for model access and CTX credentials

### Workflows
#### aop_wiki_api: 
API path for accessing AOP wiki pathway information and descriptions. 
#### aop_prediction:
**orchestrator.py** — Builds the overall LangGraph framework using nodes for each step and routing through edges and conditional edges. It coordinates the full AOP workflow, including ADMET analysis, read-across, similarity scoring, pathway expansion, critic review, and finalization.

**workflow.py** — Defines the shared AOP state, pathway heuristics, confidence calculations, node helper functions, pruning logic, and output saving. It also contains the core node implementations for ADMET, candidate generation, pathway expansion, critic review, and AO finalization.

**read_across.py** — Implements CTX-only read-across logic for resolving the target chemical, finding analogs, scoring structural similarity, and building supporting evidence for pathway construction. It helps seed and strengthen the AOP workflow with analog-based context.

**similarity_acoring.py** — Scores candidate pathway steps against the target chemical’s ADMET profile and read-across evidence. It ranks candidate KEs and AOs based on similarity, mechanistic overlap, and support from the current pathway context.

**utils.py** — Provides the shared agent execution wrapper used throughout the workflow. It handles LLM calls, prompt assembly, optional structured output, and caching so that agents can be invoked consistently from the workflow.

**ctx_api.py** — Wraps the CTX Python client and provides functions for chemical search, chemical details lookup, compound bundle retrieval, and query resolution. It serves as the API layer that read-across uses to interact with EPA CTX data.


### Process Flow
The AOP prediction workflow follows this general order:

1. **Initial ADMET analysis**: identify likely MIEs and toxicity-relevant liabilities.
2. **CTX read-across**: resolve the target chemical and search for close analogs or supporting evidence.
3. **Candidate generation**: ask the AOP expert for plausible downstream KEs and AOs.
4. **Similarity scoring**: rank candidate events against the target profile and read-across support.
5. **Pathway expansion**: add one biologically plausible step at a time.
6. **Critic review**: check whether the pathway is too shallow, too generic, duplicated, or ready to terminate.
7. **Finalization**: close the pathway only if the evidence is strong enough.
8. **Documentation**: save the result and prepare it for wiki publication.

This workflow is intended to behave like an evidence manager rather than an answer generator. If the evidence is weak, it should stop, mark uncertainty, or stay incomplete instead of inventing a pathway.

### Output
The AOP prediction workflow produces:
- A structured pathway from MIE to KE to AO
- MIE prediction and basic ADMET properties
- Confidence scores for each step and for the overall pathway
- Similarity scores for candidate events
- Critic/review reasons when the pathway is incomplete and periodically through the prediction
- A final human-readable summary suitable for wiki publication

### Notes
Not every chemical produces a valid AOP. For data-poor chemicals or non-toxicants, the correct result may be an incomplete pathway or no supported pathway at all. That is expected behavior.

### Running
To run the AOP prediction workflow:

```bash
python workflows/aop-prediction/orchestrator.py aspirin
```

## Project Structure

### `.opencode`

Contains agents, skills, scripts, and plugins to support all opencode-centric agentic aspects of workflows.

#### Agents

- `admet-mie` Calculates ADMET score for a given molecule and maps potential MIES to it, along with calculating ADMET for similar molecules.
- `aop-constructor` Agent used to manage 'admet-mie' and 'aop-expert'. Mostly leftover from previous workflow.
- `aop-expert` Handles interactions with the downloaded `.xml` file containing the OECD AOP database. Combined with the `aop-xml` skill, it gives a brief overview of the contents along with instructions on how to traverse the database and do some basic analysis on it.
- `jsonl-cleaner` Takes a raw RAG ingestion stream and cleans it up in ways that a pure Python script would have trouble with (e.g. determining if a chunk contains useful content, fixing grammatical errors, and repairing boundaries across chunks)
- `wiki-expert` Contains high-level overview information about the wiki structure. This agent is used in all nodes relating to the wiki and is meant to be used in conjunction with any of the wiki skills.

#### Skills

- `admet-ai-scoring` Predicts core ADMET properties for a molecule and identifies likely targets and signals used for MIE prediction.
- `admet-secondary-scoring` Provides secondary scoring to 'admet-ai-scoring' to catch any additional liabilities or interpretations that may be missed.
- `confidence-scoring` Computes confidence metrics for pathway steps.
- `mie-identification` Identifies potential MIEs for a molecule based on ADMET scores by connecting endpoints to MIEs in the AOP database.
- `similarity-scoring` Analyzes the similarity of ADMET scores between molecules
- `aop-xml` Meant to be used by the `aop-expert` agent. Contains information that is more procedural while the agent contains information that is more general.
- `wiki-read` Contains information about the wiki structure as well as procedures for searching the wiki given a query.
- `wiki-ingest` Explains the kinds of information that are meant to be stored in the wiki along with details about claim extraction and citation generation.
- `wiki-write` Contains information about wiki page structure, rules for page editing and creation, as well as a workflow for making new pages and sections in the wiki.
- `wiki-verify` Explains procedures for checking the validity of claims within a page, checking for contradictions in the wiki, and verifying that all sources are open-access. Includes repair strategies for broken or noncompliant pages.

### `workflows`

Contains LangGraph workflows meant for more structured agentic execution.

- `aop_wiki_api` Accesses the AOP Wiki for use in AOP prediction
- `aop-prediction` Obtains chemical from user and performs ADMET analysis, similarity scoring, candidate generation, read across, and AOP prediction
- `multi-agent-researcher`
- `rag-ingest` Handles the entire pipeline from PDF -> LightRAG ingestion and verified wiki edits

### `reference-md`

Contains markdown-formatted reference data that agents may conditionally find useful but which would pollute the context with unecessary information if unconditionally included in a skill or agent definition.

### `wiki`

The wiki itself, formatted as a Docusaurus project so that humans can have visibility into what the agents are storing and reading from.

### `data`

Downloaded data for use by agents / skills. This is open-source data such as the OECD database, but not redistributed here either for licensing reasons or because it would take up too much space.

### `artifacts`

Generated by `makedirs.sh`, this is where execution logs and other secondary artifacts from running workflows should be written. Used for auditing agent activity.