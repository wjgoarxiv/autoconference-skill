# Prompt Optimization Conference Example

This example demonstrates a metric-mode conference optimizing a customer support ticket classifier prompt.

## Goal, Metric, and Expected Outputs

| Field | Value |
|-------|-------|
| **Goal** | Improve classification accuracy for support tickets |
| **Mode** | metric |
| **Metric** | Accuracy percentage from `llm:opus` evaluation (maximize) |
| **Baseline** | 68.0% zero-shot prompt |
| **Best result** | 94.0% using decision rules plus structured JSON output |
| **Target met** | Yes — converged at 94.0% |

Expected outputs: `conference_results.tsv`, per-researcher TSV/log files, three poster sessions, three peer reviews, `synthesis.md`, and `final_report.md`.

## Artifact Map

| Artifact | What to inspect |
|----------|-----------------|
| [`conference.md`](./conference.md) | Reconstructed prompt-optimization configuration |
| `conference_results.tsv` | Generated in a full run; records accuracy trajectory across all researchers |
| `synthesis.md` | Generated in a full run; explains why decision rules and JSON output combine well |
| `final_report.md` | Generated in a full run; summarizes failed approaches and recommendations |
| `peer_review_round_3.md` | Generated in a full run; confirms convergence and remaining challenged claims |

## Verify / Reproduce

The original 50-case benchmark is not committed with this compact artifact example. Validate recorded output contracts from the repository root:

```bash
python scripts/validate_package.py
```

For a fresh run, use `templates/prompt-optimization.md` with your own labeled benchmark and evaluator command.
