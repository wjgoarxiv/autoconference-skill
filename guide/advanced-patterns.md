# Advanced Patterns

Patterns for users who have run at least one conference and want to go deeper: guard parameters, noise handling, worktree integration, CI/CD, custom evaluators, multi-conference campaigns, and answers to common questions.

---

## Guard Parameters (Safety Constraints)

Guard parameters are hard limits that prevent runaway execution. Set them in `conference.md` under `## Constraints`:

```markdown
## Constraints
max_total_iterations: 60
max_rounds: 4
time_budget: 8h
researcher_timeout: 45m
```

**`max_total_iterations`** — hard cap on total iterations summed across all researchers across all rounds. The most important guard for cost control. Rule of thumb: `researchers × iterations_per_round × max_rounds × 0.8` (80% of theoretical maximum, accounting for reverts).

**`max_rounds`** — hard cap on rounds. Set this to your actual budget, not an aspirational number. The conference treats `max_rounds` as a budget to spend, not a limit to fear — it will run all rounds unless convergence occurs first.

**`time_budget`** — wall-clock limit. Useful for overnight runs where you want the conference to stop by morning. Format: `8h`, `30m`, `2h30m`.

**`researcher_timeout`** — per-researcher time limit per round. If a researcher exceeds this, it is marked `FAILED` for the round and re-spawned next round. Default: `time_budget / researcher_count`. Set explicitly if researchers have very different expected run times.

**Per-experiment timeout** — inherited from autoresearch-skill. Each Bash command inside a researcher is wrapped with `timeout 5m` automatically. Exit code 124 = timeout; the experiment is reverted and the researcher continues. This is distinct from `researcher_timeout` (per-round level).

---

## Noise Handling (`min_consensus_delta`)

In metric mode, small improvements may be measurement noise rather than real gains. The Conference Chair uses a noise threshold when evaluating convergence:

```
converged = round_best(N) <= round_best(N-1) + noise_threshold
            AND same condition held in round N-1
```

Default `noise_threshold`: 0.1% of the baseline metric value. For integer-valued metrics (test cases passed, classification correct), the threshold is 0.

### Tuning the noise threshold

**If the conference converges too early** (the metric is still clearly improving but convergence is declared): increase the `min_consensus_delta` by lowering the noise tolerance. Add to `conference.md`:

```markdown
## Convergence
min_consensus_delta: 0.5
```

This means: only declare convergence if no researcher improved by more than 0.5 (in metric units) across 2 consecutive rounds.

**If the conference never converges** (oscillating around a plateau with small fluctuations): the metric likely has measurement noise. Options:
1. Increase `min_consensus_delta` to match the typical noise floor
2. Average the metric over multiple runs in your evaluator script
3. Switch to a more stable metric (e.g., median instead of mean latency)

**For noisy benchmarks** (e.g., GPU inference time): always run the evaluator 3× and report the median. Build this into your evaluator script rather than trying to handle it in the conference configuration.

---

## Worktree Integration for Code Conferences

Worktrees activate automatically when `mode: metric` AND researchers make code changes (not prompt/config only). You don't need to configure anything — the Conference Chair detects this from your `Allowed Changes` section.

When worktrees are active:

```
main (your current branch — untouched)
  ├── conference/researcher-A    ← Researcher A's isolated workspace
  ├── conference/researcher-B    ← Researcher B's isolated workspace
  ├── conference/researcher-C    ← Researcher C's isolated workspace
  └── conference/best            ← Validated improvements cherry-picked here
```

Each round:
1. All researcher branches reset to `conference/best`
2. Researchers commit changes to their own branch
3. Validated changes are cherry-picked to `conference/best` in Phase 4
4. Conflicts resolved by metric delta (better metric wins the conflicting file)

### Monitoring worktrees during a live conference

```bash
# See all researcher branches and their latest commits
git branch -a | grep conference/

# Check what Researcher A has committed this round
git log conference/researcher-A --oneline -5

# Compare A's changes against current best
git diff conference/best conference/researcher-A

# Use worktree-dashboard (if available)
/worktree-dashboard
```

### Cleanup options after synthesis

The Chair offers 3 options:
1. **Merge best into main** — clean, one commit with all validated improvements
2. **Keep worktrees** — inspect each branch manually before merging
3. **Delete everything** — discard all conference branches and worktrees

---

## CI/CD Integration

The `conference_results.tsv` file is machine-readable and CI-friendly. Parse it to check whether the conference hit its target:

```python
import csv

def conference_passed(tsv_path, target, direction="minimize"):
    with open(tsv_path) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    
    validated_rows = [r for r in rows if r["peer_review_verdict"] == "validated"]
    if not validated_rows:
        return False
    
    values = [float(r["metric_value"]) for r in validated_rows]
    best = min(values) if direction == "minimize" else max(values)
    
    if direction == "minimize":
        return best < target
    else:
        return best > target

# Example: check if conference achieved < 100ms latency
passed = conference_passed("conference_results.tsv", target=100, direction="minimize")
print("PASS" if passed else "FAIL")
```

For tail-based monitoring during a live conference:

```bash
tail -f conference_events.jsonl | python -c "
import sys, json
for line in sys.stdin:
    event = json.loads(line)
    if event['event'] in ('round.completed', 'conference.converged', 'conference.completed'):
        print(f\"{event['event']}: {event['payload']}\")
"
```

---

## Custom Evaluators

The evaluator is any command that produces a number. The Conference Chair passes the command to researchers verbatim — it does not need to know what the command does.

### Evaluator contract

- Must be deterministic (or averaged over multiple runs)
- Must produce a single floating-point number on stdout (or a JSON object with a `metric` key)
- Must return exit code 0 on success, non-zero on failure
- Must complete within 5 minutes (the per-experiment timeout)

### Example: LLM judge evaluator

```python
#!/usr/bin/env python3
# evaluate_quality.py
import json, subprocess, sys

response_file = sys.argv[1]
prompt = open(response_file).read()

# Call LLM to judge quality on 1-10 scale
result = subprocess.run(
    ["claude", "-p", f"Rate this output 1-10 for clarity and completeness. Reply with only a number.\n\n{prompt}"],
    capture_output=True, text=True
)
score = float(result.stdout.strip())
print(score)
```

Use in `conference.md`:
```markdown
## Success Metric
name: quality_score
target: "> 8.5"
direction: maximize
evaluator: python evaluate_quality.py {output_file}
```

### Example: multi-component composite evaluator

```python
# score_composite.py
import json, sys

data = json.load(open(sys.argv[1]))

# Three sub-metrics, weighted
clarity = data["clarity_score"]       # 0-10
coverage = data["coverage_score"]     # 0-100
citations = data["citation_accuracy"] # 0-1

composite = 0.3 * (clarity / 10) + 0.5 * (coverage / 100) + 0.2 * citations
print(composite * 100)  # normalize to 0-100
```

---

## Multi-Conference Campaigns

Run a series of conferences where later conferences build on earlier ones. Useful for iterative research programs or when you want to explore multiple hypotheses sequentially.

### Pattern: Breadth-first then depth

```
Conference 1: 3 researchers, 2 rounds, free partitioning — identify which of 4 approaches 
              has the most potential
Conference 2: 3 researchers, 4 rounds, assigned — deep dive on the winning approach
Conference 3: 2 researchers, 3 rounds — fine-tune the best configuration from conference 2
```

### Pattern: Parallel campaigns with synthesis

Run 2–3 independent conferences on related problems, then manually combine the syntheses:

```
Conference A: optimize retrieval strategy
Conference B: optimize prompt format
Conference C: optimize response length constraints

Final synthesis: combine A+B+C findings into a full-system recommendation
```

### Sharing knowledge across campaigns

Pre-seed the `Shared Knowledge` section of a later conference with findings from an earlier one:

```markdown
## Shared Knowledge
[From previous conference on retrieval optimization]
- Dense retrieval (DPR) outperforms BM25 by 12% on long documents (validated)
- Hybrid retrieval adds 3% on top of dense retrieval at 2x latency cost (validated)
- Chunk size 512 tokens optimal for this corpus (validated)
```

---

## FAQ

**Q: How many researchers should I use?**

Start with 3. Fewer than 3 reduces the value of cross-pollination in Phase 4. More than 4 adds cost without proportional benefit unless the search space is very wide.

**Q: How many rounds?**

Start with 3. If the metric is still clearly improving after round 3, add more. If it converges in round 1, the search space was too narrow or the problem too easy — consider expanding allowed changes.

**Q: My conference uses qualitative mode but the Reviewer keeps scoring everything 6-7. How do I get convergence?**

The most common cause: the `Success Criteria` section is too vague. Tighten it. Instead of "a comprehensive review," write "a taxonomy with at least 15 patterns, 3 identified research gaps, and explicit cross-domain connections." The Reviewer scores against the criteria you write.

**Q: The Reviewer is overturning almost everything. Is something wrong?**

Not necessarily. Check `peer_review_round_N.md` for the overturn reasons. Common causes: evaluator has high noise (warm cache, non-deterministic results), researchers are making changes that don't actually affect the metric, or the baseline is unusually good and improvements are marginal.

**Q: Can I run autoconference without Python?**

Yes. Python is only needed for `scripts/init_conference.py` (the scaffolding helper). You can write `conference.md` manually using `assets/conference_template.md` as a reference. The conference loop itself is pure LLM orchestration.

**Q: Can multiple people run conferences in the same repository simultaneously?**

Not recommended without worktrees. If worktrees are active, each researcher has an isolated branch. But multiple concurrent conferences in the same directory will conflict on shared files (`conference_results.tsv`, `conference.md`). Use separate directories for concurrent conferences.

**Q: What happens if the evaluator script changes during the conference?**

The evaluation results before and after the change are no longer comparable. Avoid changing the evaluator mid-conference. If you must, log the change in `conference.md` and treat it as a new baseline row.
