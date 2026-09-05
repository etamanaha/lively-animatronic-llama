#!/usr/bin/env python3
"""
Hybrid Wiki Verification and Completion Process

This module implements a two-stage verification process:
1. wiki-verify: Claim-level verification and source validation
2. wiki-seed-checklist: Structural completeness assessment

The process is designed to be highly agentic, relying on comprehensive prompts
and the LLM's reasoning capabilities rather than complex code logic.
"""

from typing import TypedDict, Any, List, Dict
from pathlib import Path
import json
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM with structured output capability
llm = ChatOpenAI(
    model="devstral-small", 
    temperature=0.2,
    streaming=True, stream_chunk_timeout=300, timeout=800,
    stream_usage=True
)

# Load reference documents
reference_files = {
    "verify": Path("../../.opencode/skills/wiki-verify/SKILL.md").read_text(),
    "checklist": Path("../../reference-md/wiki/wiki-seed-checklist.md").read_text(),
    "spec": Path("../../reference-md/wiki/specs.md").read_text(),
    "overview": Path("../../reference-md/wiki/wiki-seed-overview.md").read_text(),
}

class VerificationResult(TypedDict):
    """Result of verifying a single page."""
    page_path: str
    claims_verified: int
    claims_supported: int
    claims_unsupported: int
    claims_overstated: int
    claims_contradicted: int
    claims_source_inaccessible: int
    claims_needs_human_review: int
    sources_checked: int
    sources_open_access: int
    sources_non_open_access: int
    sources_disallowed: int
    contradictions_found: int
    contradictions_resolved: int
    patches_applied: int
    verification_status: str  # "passed", "needs_rework", "needs_human_review"
    issues: List[str]
    notes: str


class CompletionAssessment(TypedDict):
    """Result of completion assessment."""
    section: str
    criteria_id: str
    passed: bool
    details: str
    missing_items: List[str]


class WikiState(TypedDict):
    """State tracking the verification and assessment process."""
    pages_to_verify: List[Dict[str, Any]]
    verification_results: List[VerificationResult]
    completion_assessment: List[CompletionAssessment]
    overall_status: str  # "in_progress", "needs_rework", "complete"
    human_review_queue: List[str]
    rework_needed: List[str]


class HybridVerificationProcess:
    """
    Hybrid verification process combining wiki-verify and completion checklist.
    
    This process is designed to be highly agentic, relying on comprehensive prompts
    and the LLM's reasoning capabilities to guide the verification and assessment.
    """
    
    def __init__(self, pages: List[Dict[str, Any]]):
        """
        Initialize the verification process.
        
        Args:
            pages: List of page dictionaries with 'path' and 'content' keys
        """
        self.state = WikiState(
            pages_to_verify=pages,
            verification_results=[],
            completion_assessment=[],
            overall_status="in_progress",
            human_review_queue=[],
            rework_needed=[]
        )
    
    def run_verification(self) -> WikiState:
        """
        Run the complete hybrid verification process.
        
        Returns:
            Updated WikiState with verification and assessment results
        """
        print("Starting hybrid verification process...")
        
        # Phase 1: Individual page verification
        self._run_page_verification()
        
        # Phase 2: Completion assessment
        self._run_completion_assessment()
        
        # Phase 3: Determine overall status
        self._determine_overall_status()
        
        return self.state
    
    def _run_page_verification(self):
        """Run claim-level verification on all pages."""
        print("\nPhase 1: Individual Page Verification")
        print("=" * 50)
        
        for page_info in self.state["pages_to_verify"]:
            page_path = page_info.get("path")
            content = page_info.get("content", "")
            
            if not page_path:
                continue
                
            print(f"\nVerifying: {page_path}")
            
            # Create comprehensive verification prompt
            verification_prompt = self._create_verification_prompt(page_path, content)
            
            # Use LLM to perform verification
            verification_result = self._perform_verification(verification_prompt)
            
            # Store result
            self.state["verification_results"].append(verification_result)
            
            # Track issues for rework
            if verification_result["verification_status"] == "needs_rework":
                self.state["rework_needed"].append(page_path)
                
            if verification_result["verification_status"] == "needs_human_review":
                self.state["human_review_queue"].append(page_path)
            
            print(f"Verified: {verification_result['claims_verified']} claims")
            print(f"Status: {verification_result['verification_status']}")
            if verification_result["issues"]:
                print(f"Issues: {', '.join(verification_result['issues'])}")
    
    def _create_verification_prompt(self, page_path: str, content: str) -> str:
        """Create a comprehensive verification prompt for a single page."""
        return f"""
# Wiki Page Verification Task

## Instructions
You are performing claim-level verification of a wiki pages according to the wiki-verify skill specification. Follow the verification checklist below to analyze this page.

## Required References
- [Wiki Specification Reference](../../reference-md/wiki/specs.md)
- [Verification Skill](../../.opencode/skills/wiki-verify/SKILL.md)

## Page Information
- **Path**: {page_path}
- **Content**:
```markdown
{content}
```

## Verification Checklist

### 1. Claim Extraction
Extract all substantive claims from the page. Each claim should have:
- Unique claim ID
- Claim text
- Source citations
- Scope qualifiers (species, tissue, assay, endpoint, dose, route, time, population)
- Confidence/evidence strength
- Status (draft, supported, uncertain, needs_review)

### 2. Source Verification
For each claim with citations:
- Resolve the source (DOI, URL, title, publication year, authors, repository)
- Check if the source is open-access according to the allowed source policy
- Verify the source is actually accessible
- Compare the claim against the source evidence

### 3. Evidence Comparison
For each claim:
- Verify the source actually supports the claim
- Check organism, endpoint, assay, dose/exposure context
- Check uncertainty and confidence levels

### 4. Claim Classification
Classify each claim as one of:
- `supported`: Claim is well-supported by accessible, open-access sources
- `unsupported`: Claim lacks sufficient evidence or sources are inadequate
- `overstated`: Claim goes beyond what the sources support
- `contradicted`: Claim contradicts other verified claims or sources
- `source_inaccessible`: Sources cannot be accessed or are not open-access
- `needs_human_review`: Claim requires human judgment due to complexity or uncertainty

### 5. Contradiction Checking
Check for contradictions:
- Within the page itself
- Against other pages in the wiki (if accessible)
- Against known knowledge graph facts (if available)

### 6. Verification Output
Provide a structured verification result with:
- Number of claims verified
- Breakdown by status
- Number of sources checked
- Breakdown by source accessibility
- Number of contradictions found and resolved
- Any patches that should be applied
- Overall verification status
- List of specific issues
- Notes for human reviewers

## Allowed Source Policy
Only consider sources that are:
- Open-access journal articles (PubMed Central, Europe PMC, arXiv, bioRxiv, etc.)
- Government and intergovernmental sources (EPA, FDA, NIH, OECD, etc.)
- Public databases (EPA CompTox, ToxCast, PubChem, ChEMBL, etc.)
- Open technical reports and standards
- Open-source software documentation

Disallowed:
- Paywalled articles
- Sources requiring institutional login
- Unauthorized file-sharing copies
- Citation-only references

## Repair Strategy
For issues found, suggest minimal patches that:
- Preserve useful structure
- Remove or qualify unsupported content
- Add review notes for uncertain content
- Maintain claim IDs for supported content

## Output Format
Return your analysis as a structured JSON object with the following keys:
- page_path: string
- claims_verified: int
- claims_supported: int
- claims_unsupported: int
- claims_overstated: int
- claims_contradicted: int
- claims_source_inaccessible: int
- claims_needs_human_review: int
- sources_checked: int
- sources_open_access: int
- sources_non_open_access: int
- sources_disallowed: int
- contradictions_found: int
- contradictions_resolved: int
- patches_applied: int
- verification_status: "passed" | "needs_rework" | "needs_human_review"
- issues: array of strings (specific issues found)
- notes: string (additional notes for human reviewers)

## Verification Standards
- Every substantive claim must have at least one citation
- Sources must be open-access and accessible
- Claims must be supported by the cited evidence
- Contradictions must be resolved or flagged
- Uncertainty must be explicitly noted
- Page structure must support future verification

Begin your verification analysis now.
"""
    
    def _perform_verification(self, prompt: str) -> VerificationResult:
        """Use LLM to perform verification and parse the result."""
        try:
            # Use structured output for verification results
            structured_llm = llm.with_structured_output(VerificationResult)
            
            response = structured_llm.invoke([
                SystemMessage(content=reference_files["verify"]),
                SystemMessage(content=reference_files["spec"]),
                HumanMessage(content=prompt)
            ])
            
            return response
            
        except Exception as e:
            print(f"Error during verification: {e}")
            return VerificationResult(
                page_path="unknown",
                claims_verified=0,
                claims_supported=0,
                claims_unsupported=0,
                claims_overstated=0,
                claims_contradicted=0,
                claims_source_inaccessible=0,
                claims_needs_human_review=0,
                sources_checked=0,
                sources_open_access=0,
                sources_non_open_access=0,
                sources_disallowed=0,
                contradictions_found=0,
                contradictions_resolved=0,
                patches_applied=0,
                verification_status="needs_human_review",
                issues=[f"Verification failed: {str(e)}"],
                notes="Manual verification required due to processing error."
            )
    
    def _run_completion_assessment(self):
        """Run structural completeness assessment."""
        print("\nPhase 2: Completion Assessment")
        print("=" * 50)
        
        # Define assessment sections from the checklist
        sections = [
            ("D14.1 Core Structural Coverage", "D14.1"),
            ("D14.2 Minimum Domain Spine", "D14.2"),
            ("D14.3 Page-Level Usability", "D14.3"),
            ("D14.4 Citation and Provenance Readiness", "D14.4"),
            ("D14.5 Cross-Linking and Retrieval Quality", "D14.5"),
            ("D14.6 Redundancy Control", "D14.6"),
            ("D14.7 Operational Readiness", "D14.7"),
            ("D14.8 Verification Readiness", "D14.8"),
        ]
        
        for section_name, criteria_id in sections:
            print(f"\nAssessing: {section_name} ({criteria_id})")
            
            # Create assessment prompt
            assessment_prompt = self._create_assessment_prompt(section_name, criteria_id)
            
            # Use LLM to perform assessment
            assessment_result = self._perform_assessment(assessment_prompt, criteria_id)
            
            # Store result
            self.state["completion_assessment"].append(assessment_result)
            
            status_emoji = "✅" if assessment_result["passed"] else "❌"
            print(f"  {status_emoji} {section_name}")
            if not assessment_result["passed"] and assessment_result["missing_items"]:
                print(f"Missing: {', '.join(assessment_result['missing_items'][:3])}...")
    
    def _create_assessment_prompt(self, section_name: str, criteria_id: str) -> str:
        """Create a comprehensive assessment prompt for a checklist section."""
        
        # Extract the specific section from the checklist
        section_content = self._extract_section_from_checklist(criteria_id)
        
        # Get verification results summary
        verification_summary = self._get_verification_summary()
        
        return f"""
# Wiki Completion Assessment Task

## Instructions
You are assessing whether the wiki meets the completion criteria for {section_name}. This is part of the final quality gate before declaring wiki seeding complete.

## Required References
- [Wiki Seed Checklist](../../reference-md/wiki/wiki-seed-checklist.md)
- [Wiki Specification Reference](../../reference-md/wiki/specs.md)
- [Wiki Seed Overview](../../reference-md/wiki/wiki-seed-overview.md)

## Criteria to Assess
{section_content}

## Current Wiki State

### Verification Results
{verification_summary}

### Page Inventory
- Total pages created: {len(self.state['pages_to_verify'])}
- Pages verified: {len(self.state['verification_results'])}
- Pages needing rework: {len(self.state['rework_needed'])}
- Pages needing human review: {len(self.state['human_review_queue'])}

### Structural Information
Analyze the wiki structure based on the pages provided to determine if the criteria are met.

## Assessment Guidelines

### Core Structural Coverage (D14.1)
- Check for required top-level categories
- Verify index pages exist and are navigable
- Check front matter validity
- Verify correct category placement

### Minimum Domain Spine (D14.2)
- Check for high-value concept pages
- Verify core method/model pages exist
- Check major dataset pages
- Verify assay-family and endpoint pages
- Check biology pages
- Verify sentinel chemical pages with cross-links

### Page-Level Usability (D14.3)
- Check for overview and scope sections
- Verify substantive toxicology-specific content
- Check for proper claim formatting
- Verify citation presence

### Citation and Provenance Readiness (D14.4)
- Verify every substantive claim has citations
- Check citation completeness
- Verify source pages exist where needed
- Check that facts are routed to canonical pages

### Cross-Linking and Retrieval Quality (D14.5)
- Verify cross-category links exist
- Check concept-to-method links
- Verify chemical-to-endpoint links
- Check endpoint-to-assay links
- Verify multi-hop retrieval is possible

### Redundancy Control (D14.6)
- Check for toxicology-specific content
- Verify minimal generic background
- Check that canonical content isn't duplicated
- Verify index pages remain navigational

### Operational Readiness (D14.7)
- Check governance pages exist
- Verify workflow pages are present
- Check scope determination capability
- Verify page placement capability

### Verification Readiness (D14.8)
- Check claim-level structure
- Verify claims are scoped for comparison
- Check for open questions/review notes
- Verify contradiction checking is possible

## Assessment Output Format
Return your assessment as a structured JSON object with:
- section: string (section name)
- criteria_id: string (e.g., "D14.1")
- passed: boolean (true if criteria are met)
- details: string (detailed assessment)
- missing_items: array of strings (specific missing items)

## Assessment Standards
- Be strict but fair in applying criteria
- Consider the wiki as a whole, not individual pages
- Note structural issues that prevent operational use
- Identify gaps that would block retrieval or routing

Begin your assessment now.
"""
    
    def _perform_assessment(self, prompt: str, criteria_id: str) -> CompletionAssessment:
        """Use LLM to perform completion assessment."""
        try:
            # Use structured output for assessment results
            structured_llm = llm.with_structured_output(CompletionAssessment)
            
            response = structured_llm.invoke([
                SystemMessage(content=reference_files["checklist"]),
                SystemMessage(content=reference_files["overview"]),
                HumanMessage(content=prompt)
            ])
            
            # Ensure criteria_id is set correctly
            response["criteria_id"] = criteria_id
            
            return response
            
        except Exception as e:
            print(f"Error during assessment: {e}")
            return CompletionAssessment(
                section="unknown",
                criteria_id=criteria_id,
                passed=False,
                details=f"Assessment failed: {str(e)}",
                missing_items=["Assessment error"]
            )
    
    def _extract_section_from_checklist(self, criteria_id: str) -> str:
        """Extract a specific section from the checklist."""
        try:
            # Find the section header
            lines = reference_files["checklist"].split('\n')
            for i, line in enumerate(lines):
                if criteria_id in line:
                    # Extract content until next section header
                    section_lines = []
                    for j in range(i, len(lines)):
                        section_lines.append(lines[j])
                        if lines[j].startswith('## ') and j > i:
                            break
                    return '\n'.join(section_lines)
            return "Section not found"
        except Exception as e:
            print(f"Error extracting section: {e}")
            return ""
    
    def _get_verification_summary(self) -> str:
        """Generate a summary of verification results."""
        if not self.state["verification_results"]:
            return "No verification results available yet."
        
        results = self.state["verification_results"]
        total_claims = sum(r["claims_verified"] for r in results)
        supported = sum(r["claims_supported"] for r in results)
        unsupported = sum(r["claims_unsupported"] for r in results)
        overstated = sum(r["claims_overstated"] for r in results)
        contradicted = sum(r["claims_contradicted"] for r in results)
        inaccessible = sum(r["claims_source_inaccessible"] for r in results)
        needs_review = sum(r["claims_needs_human_review"] for r in results)
        
        passed = sum(1 for r in results if r["verification_status"] == "passed")
        needs_rework = sum(1 for r in results if r["verification_status"] == "needs_rework")
        needs_human = sum(1 for r in results if r["verification_status"] == "needs_human_review")
        
        return f"""
Total Pages Verified: {len(results)}
  - Passed: {passed}
  - Needs Rework: {needs_rework}
  - Needs Human Review: {needs_human}

Total Claims Verified: {total_claims}
  - Supported: {supported}
  - Unsupported: {unsupported}
  - Overstated: {overstated}
  - Contradicted: {contradicted}
  - Source Inaccessible: {inaccessible}
  - Needs Human Review: {needs_review}

Sources Checked: {sum(r['sources_checked'] for r in results)}
  - Open Access: {sum(r['sources_open_access'] for r in results)}
  - Non-Open Access: {sum(r['sources_non_open_access'] for r in results)}
  - Disallowed: {sum(r['sources_disallowed'] for r in results)}

Contradictions: {sum(r['contradictions_found'] for r in results)} found, {sum(r['contradictions_resolved'] for r in results)} resolved
"""
    
    def _determine_overall_status(self):
        """Determine the overall status of the wiki."""
        
        # Check if all pages passed verification
        all_verified = all(
            r["verification_status"] == "passed" 
            for r in self.state["verification_results"]
        )
        
        # Check if all completion criteria passed
        all_criteria_met = all(
            a["passed"] 
            for a in self.state["completion_assessment"]
        )
        
        if all_verified and all_criteria_met:
            self.state["overall_status"] = "complete"
            print("\nWiki seeding complete! All verification and assessment criteria passed.")
        elif self.state["rework_needed"] or not all_criteria_met:
            self.state["overall_status"] = "needs_rework"
            print("\nWiki needs rework before completion.")
            if self.state["rework_needed"]:
                print(f"  Pages needing rework: {len(self.state['rework_needed'])}")
            if not all_criteria_met:
                failed_criteria = [a["section"] for a in self.state["completion_assessment"] if not a["passed"]]
                print(f"  Failed criteria: {', '.join(failed_criteria)}")
        else:
            self.state["overall_status"] = "needs_human_review"
            print("\nWiki needs human review before completion.")
            print(f"  Pages needing review: {len(self.state['human_review_queue'])}")
    
    def get_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        
        report = []
        report.append("=" * 60)
        report.append("WIKI VERIFICATION AND COMPLETION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Overall Status: {self.state['overall_status'].upper()}")
        report.append("")
        
        # Verification Summary
        report.append("VERIFICATION SUMMARY")
        report.append("-" * 60)
        report.append(self._get_verification_summary())
        report.append("")
        
        # Completion Assessment
        report.append("COMPLETION ASSESSMENT")
        report.append("-" * 60)
        for assessment in self.state["completion_assessment"]:
            status = "PASS" if assessment["passed"] else "❌ FAIL"
            report.append(f"{status} {assessment['section']} ({assessment['criteria_id']})")
            if not assessment["passed"] and assessment["missing_items"]:
                report.append(f"   Missing: {', '.join(assessment['missing_items'][:5])}")
        report.append("")
        
        # Action Items
        report.append("ACTION ITEMS")
        report.append("-" * 60)
        if self.state["rework_needed"]:
            report.append(f"Pages needing rework: {len(self.state['rework_needed'])}")
            for page in self.state["rework_needed"][:10]:
                report.append(f"  - {page}")
            if len(self.state["rework_needed"]) > 10:
                report.append(f"  ... and {len(self.state['rework_needed']) - 10} more")
        
        if self.state["human_review_queue"]:
            report.append(f"Pages needing human review: {len(self.state['human_review_queue'])}")
            for page in self.state["human_review_queue"][:10]:
                report.append(f"  - {page}")
            if len(self.state["human_review_queue"]) > 10:
                report.append(f"  ... and {len(self.state['human_review_queue']) - 10} more")
        
        if not self.state["rework_needed"] and not self.state["human_review_queue"]:
            report.append("No action items. Wiki is ready for use.")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    print("Hybrid Wiki Verification Process")
    print("=" * 50)
    
    # In a real scenario, you would load actual pages from the wiki
    # This is just an example with mock data
    example_pages = [
        {
            "path": "wiki/docs/02-concepts/toxicokinetics.md",
            "content": """
---
title: Toxicokinetics
page_type: concept
date: 2024-01-15
verification_status: unverified
---

# Toxicokinetics

Toxicokinetics describes the movement of chemicals through the body.

## Absorption
Chemicals can be absorbed through various routes including oral, dermal, and inhalation.

## Distribution
After absorption, chemicals are distributed throughout the body via the bloodstream.

## Metabolism
The liver is the primary site of metabolism for many chemicals.

## Excretion
Excretion occurs primarily through the kidneys, but also through feces, sweat, and breath.

## References
- [EPA Toxicokinetics](https://example.com/epa-tk)
"""
        },
        {
            "path": "wiki/docs/03-chemicals/benzo-a-pyrene.md",
            "content": """
---
title: Benzo[a]pyrene
page_type: chemical
date: 2024-01-16
verification_status: unverified
---

# Benzo[a]pyrene

Benzo[a]pyrene is a polycyclic aromatic hydrocarbon found in tobacco smoke.

## Properties
- CAS: 50-32-8
- Molecular formula: C20H12
- Molecular weight: 252.31 g/mol

## Toxicity
Benzo[a]pyrene is a known carcinogen.

## References
- [IARC Monographs](https://monographs.iarc.who.int)
"""
        }
    ]
    
    # Run the verification process
    process = HybridVerificationProcess(example_pages)
    final_state = process.run_verification()
    
    # Print summary report
    print(process.get_summary_report())
    
    # Save results to JSON
    with open("verification_results.json", "w") as f:
        json.dump(final_state, f, indent=2)
    print("\nResults saved to verification_results.json")