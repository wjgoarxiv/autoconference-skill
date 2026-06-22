# Literature Review Conference Example

This example demonstrates qualitative/coverage-oriented conference use for a multi-perspective literature survey.

## Goal, Metric, and Expected Outputs

| Field | Value |
|-------|-------|
| **Goal** | Compare morning vs evening exercise effectiveness across health and fitness outcomes |
| **Mode** | qualitative with coverage metric |
| **Metric** | Taxonomy coverage categories with at least two papers each (maximize) |
| **Baseline** | 2/8 categories covered from seed papers |
| **Best result** | 8/8 categories, 30+ papers |
| **Target met** | Yes — target reached in one round |

Expected outputs: `conference_results.tsv`, per-researcher logs, `poster_session_round_1.md`, `peer_review_round_1.md`, `synthesis.md`, and `final_report.md`.

## Artifact Map

| Artifact | What to inspect |
|----------|-----------------|
| [`conference.md`](./conference.md) | Reconstructed survey configuration and partitions |
| `conference_results.tsv` | Generated in a full run; records category coverage progression |
| `synthesis.md` | Generated in a full run; gives unified taxonomy and cross-cutting conclusions |
| `final_report.md` | Generated in a full run; lists papers by category and challenged findings |
| `peer_review_round_1.md` | Generated in a full run; records evidence-quality challenges |

## Verify / Reproduce

Validate recorded output contracts from the repository root:

```bash
python scripts/validate_package.py
```

For a fresh run, use `templates/survey-mode.md` or `/autoconference:survey` with live database access and a citation-verification workflow.
