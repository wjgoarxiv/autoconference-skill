# Conference: Customer Support Ticket Classifier Prompt Optimization

## Goal
Improve customer support ticket classification accuracy.

## Mode
metric

## Success Metric
- **Metric:** accuracy_percent
- **Target:** >= 90
- **Direction:** maximize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 3

## Search Space
- **Allowed changes:** Prompt instructions, examples, response format, and classification decision rules.
- **Forbidden changes:** Evaluation labels, benchmark cases, and scoring rubric.

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Instruction phrasing and category definitions.

### Researcher B Focus
Few-shot example selection.

### Researcher C Focus
Output structure and reasoning format.

## Guard
Do not alter the benchmark set or target labels.

## Noise Handling
- **Noise runs:** 1
- **Min consensus delta:** 0

## Current Approach
Zero-shot prompt with category list only, measured at 68.0% accuracy.

## Shared Knowledge
Decision rules plus structured JSON output reached 94.0% and resisted micro-optimization regressions.

## Conference Log
See `conference_results.tsv`, `synthesis.md`, and `final_report.md`.
