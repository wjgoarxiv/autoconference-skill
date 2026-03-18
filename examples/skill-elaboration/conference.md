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

### Round 1 Validated Findings
1. **Procedural equipment scanning:** Grid-based, size-ordered identification (largest enclosed shapes first, then circular symbols on pipe runs, then inline symbols) outperforms detailed symbol disambiguation tables
2. **ISA-5.1 tag conventions:** Equipment IDs use letter prefix (equipment type) + area number + sequence number format (e.g., P-101, T-201, V-301)
3. **Connection topology:** Build equipment-to-equipment adjacency list, derive streams from connections -- graph-based approach is more robust than pattern-based bypass detection
4. **Flow direction inference:** Use arrows on lines, gravity direction, pump discharge orientation to determine flow direction for correct stream numbering
5. **Structured JSON schema:** Force explicit enumeration of equipment and streams in structured JSON format rather than prose descriptions
6. **Inclusion-first classification:** Include all pipe connections as streams; exclude only dashed lines (instrument signals). When in doubt, include.
7. **Cross-reference validation:** Build equipment-stream matrix; flag equipment with < 2 connections (inlet + outlet) for re-scanning to catch missing streams

### Round 2 Validated Findings
8. **3-phase workflow architecture:** Equipment Scan -> Stream Derivation -> Cross-Reference Validation is the core analysis pattern, validated independently by all three researchers
9. **Domain-specific equipment symbols:** Add generalizable descriptions for process-specific equipment types (e.g., "settling/separation equipment" for clarifiers, "aeration/mixing equipment" for blowers)
10. **Categorized stream numbering:** Type-based prefixes (S-1xx process, S-2xx sludge, S-3xx recirculation, S-4xx utilities) for systematic numbering per ISA conventions
11. **Confidence-based re-examination:** Score confidence per item; re-examine low-confidence items in a second pass to catch marginal detections
12. **Phased output structure:** JSON output mirroring analysis phases enforces workflow compliance and prevents skipped steps

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
| 1 | A | 82.5% | Procedural equipment scanning (grid, size-ordered) | completed |
| 1 | B | 82.5% | Connection topology (adjacency graph) | completed |
| 1 | C | 82.5% | Inclusion-first classification + cross-ref validation | completed |
| 2 | A | 94.5% | Integrated 3-phase workflow + domain equipment symbols | target_reached |
| 2 | B | 94.5% | Categorized stream numbering + discovery pipeline | target_reached |
| 2 | C | 94.5% | Phased output structure + confidence re-examination | target_reached |
