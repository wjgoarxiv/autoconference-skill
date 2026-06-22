# Conference: P&ID Skill Elaboration

## Goal
Improve a domain-specific workflow for P&ID diagram analysis.

## Mode
metric

## Success Metric
- **Metric:** composite_extraction_score
- **Target:** >= 0.85
- **Direction:** maximize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 2

## Search Space
- **Allowed changes:** Workflow instructions, extraction phases, confidence checks, and output structure.
- **Forbidden changes:** Evaluation rubric and ground-truth answer key.

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Equipment and symbol recognition.

### Researcher B Focus
Stream tracing and numbering.

### Researcher C Focus
Output structure and validation checks.

## Guard
Do not optimize by omitting uncertain items without evidence.

## Noise Handling
- **Noise runs:** 1
- **Min consensus delta:** 0

## Current Approach
Generic diagram reading workflow with 20.8% composite score.

## Shared Knowledge
The best workflow is a simple three-phase process: equipment scan, stream derivation, validation.

## Conference Log
See `conference_results.tsv`, `synthesis.md`, and `final_report.md`.
