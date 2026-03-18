# Conference: Skill Elaboration for P&ID Diagram Analysis

## Goal
Improve the existing `/pdf` skill so that an LLM can accurately extract process streams, identify equipment, and assign stream numbers from Piping and Instrumentation Diagrams (P&IDs).

**Target diagram:** Wastewater treatment plant P&ID (`wastewater-treatment-plant-pid-example.png`).

## Mode
metric

## Success Metric
- **Metric:** Composite score: `0.5 * (streams_found / 15) + 0.3 * (streams_numbered / streams_found) + 0.2 * (equipment_found / 8)`
- **Target:** > 85%
- **Direction:** maximize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 3

## Search Space
- **Allowed changes:** Add new sections after existing content, add symbol definition tables, add stream identification rules, add naming conventions, add structured output templates
- **Forbidden changes:** Remove or rewrite existing PDF sections, hardcode specific equipment tag numbers, add diagram-specific coordinates, exceed 300 lines, break existing PDF operations

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Symbol recognition: P&ID symbol definitions (pump=circle+arrow, tank=cylinder, valve=bowtie), equipment identification rules, ISA symbol standards, visual element recognition guidance.

### Researcher B Focus
Stream tracing: connection logic between equipment, flow direction inference rules, stream numbering conventions (ISA-5.1), bypass line detection, multi-path tracing.

### Researcher C Focus
Output structure: structured output format (JSON schema), edge case handling (bypasses, branches, dead ends), validation rules for completeness checking, naming conventions.

## Constraints
- **Max total iterations:** 45
- **Time budget:** 2h
- **Researcher timeout:** 40m
- `SKILL.md` must remain under 300 lines
- All original `/pdf` skill content must be preserved (no deletions from the base skill)
- Additions must be generalizable to other P&ID diagrams, not hardcoded for this specific diagram
- Search space is additive only: new sections may be appended, but existing sections must not be removed or rewritten

## Ground Truth

| Category | Count |
|----------|-------|
| Total process streams | 15 |
| Total equipment items | 8 |

## Current Approach
Original `/pdf` skill with no P&ID-specific knowledge. See `original_skill/SKILL.md` for the baseline skill content.

Baseline scores:
- Streams found: 4/15
- Streams numbered: 0/4
- Equipment found: 3/8
- Composite score: 20.8%

## Shared Knowledge
<!-- Auto-populated after each round with validated findings -->

## Context & References
- Evaluation harness: `evaluate.py`
- Annotation script: `annotate_pid.py`
- Target diagram: `wastewater-treatment-plant-pid-example.png`
- Original skill: `original_skill/SKILL.md`
- ISA-5.1 is the standard for P&ID stream numbering

---

## Conference Log
<!-- Auto-maintained by Conference Chair. Do not edit manually. -->
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
