---
inclusion: manual
---

# Spec Analyzer — Cross-Artifact Consistency & Quality Analysis

## Purpose

Perform a non-destructive, read-only cross-artifact consistency and quality analysis across the Kiro spec files (`requirements.md`, `design.md`, and `tasks.md`) for a given feature spec. This analysis identifies inconsistencies, duplications, ambiguities, coverage gaps, and underspecified items before implementation begins.

## Operating Constraints

- **STRICTLY READ-ONLY**: Do NOT modify any files. Output a structured analysis report in chat only.
- **Offer remediation suggestions**: The user must explicitly approve before any follow-up edits.
- **Project documentation authority**: Files in `RAG-FIN-Topicos-Avanzados/project_documentation/` serve as the project's ground truth. Conflicts with these documents are automatically CRITICAL.

## Execution Steps

### 1. Initialize Analysis Context

Locate the target spec directory. Default: `.kiro/specs/fin-advisor-rag/`.

Read `.config.kiro` to determine `specType` and `workflowType`.

Derive paths:
- REQUIREMENTS = `{SPEC_DIR}/requirements.md`
- DESIGN = `{SPEC_DIR}/design.md`
- TASKS = `{SPEC_DIR}/tasks.md`

If any required file is missing, report which file is absent and instruct the user to complete the spec workflow for that phase first. Do NOT abort entirely — analyze whatever artifacts exist and note the missing ones.

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From requirements.md:**
- All requirement titles and IDs (Requirement 1, 2, …)
- User stories
- Acceptance criteria
- Glossary terms
- Correctness properties (if present)

**From design.md:**
- Architecture and component descriptions
- Data models and schemas
- API endpoint definitions
- Technology choices
- Sequence/interaction flows
- File/folder structure decisions

**From tasks.md:**
- Task IDs and descriptions
- Sub-task breakdowns
- Task checkbox status (completed, in-progress, not started)
- Referenced file paths
- Phase/grouping structure

**From project documentation (if exists):**
- `RAG-FIN-Topicos-Avanzados/project_documentation/` files as supplementary ground truth

### 3. Build Semantic Models

Create internal representations (do NOT include raw artifacts in output):

- **Requirements inventory**: For each requirement, record its ID, user story summary, and acceptance criteria count. Use the requirement number as the primary key (e.g., `REQ-01`).
- **User story/action inventory**: Discrete user actions with their acceptance criteria.
- **Task coverage mapping**: Map each task to one or more requirements (by keyword matching, explicit references, or semantic inference).
- **Design component inventory**: List components, APIs, data models defined in design.md.

### 4. Detection Passes

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection
- Identify near-duplicate requirements or acceptance criteria
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection
- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TBD, ???, `<placeholder>`, etc.)

#### C. Underspecification
- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in design.md
- Design components with no corresponding requirement

#### D. Coverage Gaps
- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Acceptance criteria requiring buildable work not reflected in tasks
- Design components not covered by any task

#### E. Inconsistency
- Terminology drift (same concept named differently across files)
- Data entities referenced in design but absent in requirements (or vice versa)
- Task ordering contradictions (integration tasks before foundational setup without dependency note)
- Conflicting requirements (e.g., one specifies technology X while another specifies technology Y)
- Port numbers, environment variables, or configuration values that differ between artifacts

#### F. Project Documentation Alignment
- Requirements or design decisions that contradict the project documentation in `project_documentation/`
- Missing requirements for items specified in project documentation

### 5. Severity Assignment

- **CRITICAL**: Contradicts project documentation, missing core artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Analysis Report

Output a Markdown report in chat (no file writes) with this structure:

```
## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | requirements.md:REQ-03 | ... | ... |
```

One row per finding with stable IDs prefixed by category initial (A=Ambiguity, D=Duplication, U=Underspec, C=Coverage, I=Inconsistency, P=ProjectAlign).

**Coverage Summary Table:**

```
| Requirement | Has Task? | Task IDs | Notes |
|-------------|-----------|----------|-------|
```

**Unmapped Tasks:** (tasks with no clear requirement mapping)

**Metrics:**
- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count
- Files Analyzed

### 7. Next Actions

- If CRITICAL issues exist: Recommend resolving before task execution
- If only LOW/MEDIUM: User may proceed, with improvement suggestions
- Provide explicit suggestions like: "Update requirement X to clarify Y", "Add a task for requirement Z", "Align terminology between design.md and requirements.md for concept W"

### 8. Offer Remediation

Ask: "Would you like me to suggest concrete edits for the top N issues?"

Do NOT apply edits automatically. Wait for explicit user approval.

## Analysis Guidelines

- NEVER modify files (this is read-only analysis)
- NEVER hallucinate missing sections (if absent, report them accurately)
- Prioritize project documentation conflicts (these are always CRITICAL)
- Use specific examples over generic patterns (cite specific instances)
- Report zero issues gracefully (emit success report with coverage statistics)
- Keep output token-efficient — limit findings table to 50 rows, summarize overflow
- Rerunning without changes should produce consistent IDs and counts
