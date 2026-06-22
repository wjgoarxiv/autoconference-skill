# Skill Elaboration Conference Example

This example demonstrates using the conference pattern to improve a domain-specific skill workflow.

## Goal, Metric, and Expected Outputs

| Field | Value |
|-------|-------|
| **Goal** | Improve a diagram-analysis skill workflow for P&ID extraction |
| **Mode** | metric |
| **Metric** | Composite extraction score (maximize) |
| **Baseline** | 20.8% generic workflow |
| **Best result** | 94.5% integrated scan → derive → validate workflow |
| **Target met** | Yes — exceeded 85% target in two rounds |

Expected outputs: `conference_results.tsv`, per-researcher logs, two poster sessions, two peer reviews, `synthesis.md`, and `final_report.md`.

## Artifact Map

| Artifact | What to inspect |
|----------|-----------------|
| [`conference.md`](./conference.md) | Reconstructed skill-improvement configuration |
| `conference_results.tsv` | Generated in a full run; records composite score progression |
| `synthesis.md` | Generated in a full run; contains the unified workflow proposed by the conference |
| `final_report.md` | Generated in a full run; summarizes findings, failed approaches, and next validation ideas |
| `peer_review_round_2.md` | Generated in a full run; records final validation and challenged findings |

## Verify / Reproduce

Validate recorded output contracts from the repository root:

```bash
python scripts/validate_package.py
```

For a fresh run, use a local eval rubric that scores streams found, streams numbered, equipment found, and false positives.
