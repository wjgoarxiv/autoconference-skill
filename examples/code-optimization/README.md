# Code Optimization Conference Example

This example demonstrates a metric-mode conference optimizing a sorting implementation for integer arrays.

## Goal, Metric, and Expected Outputs

| Field | Value |
|-------|-------|
| **Goal** | Sort 1M integers in under 0.5 seconds |
| **Mode** | metric |
| **Metric** | `wall_time_seconds` from `script:benchmark.py` (minimize) |
| **Baseline** | 2.0421s recursive quicksort |
| **Best result** | 0.1516s using Python `sorted()` |
| **Target met** | Yes — 0.1516s < 0.5s |

Expected outputs: `conference_results.tsv`, per-researcher TSV/log files, `poster_session_round_{1,2}.md`, `peer_review_round_{1,2}.md`, `synthesis.md`, and `final_report.md`.

## Artifact Map

| Artifact | What to inspect |
|----------|-----------------|
| [`conference.md`](./conference.md) | Reconstructed run config and search-space boundaries |
| `conference_results.tsv` | Generated in a full run; records all researcher iterations and peer-review verdicts |
| `synthesis.md` | Generated in a full run; explains why `sorted()` wins |
| `final_report.md` | Generated in a full run; summarizes timeline and lessons |
| `peer_review_round_1.md` | Generated in a full run; captures challenged claims before knowledge transfer |

## Verify / Reproduce

The benchmark harness is not committed with this compact artifact example, so reproduce by inspecting the recorded logs and validating the package contracts:

```bash
python scripts/validate_package.py
```

For a fresh run, scaffold a comparable conference with `templates/code-performance.md` and provide your own benchmark command.
