# Troubleshooting

Common failure modes, their root causes, and fixes. If your conference is not behaving as expected, check this page first.

---

## Researcher Timeout

**Symptom:** One or more researchers are marked `FAILED` in `conference_results.tsv` for a round. The round completes but with partial results.

**Root cause options:**
1. `researcher_timeout` is too short for the number of iterations
2. `iterations_per_round` is too high relative to the timeout
3. A specific experiment is hanging (infinite loop, blocked network call)

**Fix:**

First, check whether the timeout is systematic or sporadic. Open `conference_events.jsonl` and search for `researcher.stuck` events:

```bash
grep "researcher.stuck" conference_events.jsonl
```

If all researchers time out in the same round, the experiment itself is hanging — check your evaluator for blocking calls. If only one researcher times out inconsistently, increase `researcher_timeout`:

```markdown
## Constraints
researcher_timeout: 90m    # was 45m
```

Or reduce `iterations_per_round`:

```markdown
## Researchers
iterations_per_round: 3    # was 5
```

If a specific experiment consistently hangs, add a timeout to the evaluator script directly:

```bash
timeout 300 python expensive_eval.py "$@"
```

---

## All Researchers Stalled

**Symptom:** Conference ends early with status `STALLED`. The `conference_events.jsonl` contains `conference.stalled`. Final metric is below target.

**Root cause:** All researchers simultaneously hit stuck Level 2 or Level 3 — the search space is exhausted.

**Diagnosis:** Check `researcher_*_log.md` files. If all researchers are trying variations of the same approach and none are improving, the search space is too narrow.

**Fix options:**

1. **Expand `Allowed Changes`** — the most common fix. Add more of the codebase, more hyperparameters, or more configuration options to what researchers can touch.

2. **Enable Devil's Advocate** — if not already enabled, add a researcher whose mandate is to challenge the current search space boundary. Sometimes the real improvement is outside the current allowed region.

3. **Re-run with different partitioning** — if using `assigned` strategy, try `free`. The partitions may have been too restrictive.

4. **Broaden the problem definition** — if researchers have genuinely exhausted the allowed search space and hit a real limit, the target may be unreachable with the current approach. Consider re-framing the problem.

---

## Worktree Conflicts

**Symptom:** Conference Chair reports merge conflicts during Phase 4 (Knowledge Transfer). Cherry-picks fail for some files.

**Root cause:** Two researchers modified the same file with validated but incompatible changes.

**How it is resolved automatically:**

The Conference Chair resolves file-level conflicts by metric delta — the researcher with the better metric improvement wins the conflicting file. Non-conflicting files from both researchers are kept. The resolution is logged in `peer_review_round_N.md` under "Conflict Resolution."

**If automatic resolution fails:**

```bash
# See current conflict state
git -C ./worktrees/conference-best status

# See what A and B changed for the conflicting file
git diff conference/researcher-A -- src/conflicted_file.py
git diff conference/researcher-B -- src/conflicted_file.py

# Manually resolve and commit
git -C ./worktrees/conference-best checkout --theirs src/conflicted_file.py
git -C ./worktrees/conference-best add src/conflicted_file.py
git -C ./worktrees/conference-best commit -m "conference: resolve conflict, prefer researcher-A"
```

Then tell the Chair to continue from Phase 4.

**Prevention:** Assign researchers to non-overlapping code regions in `conference.md`:

```markdown
## Researcher A Focus
Files: src/models/*.py (model architecture changes only)
Do NOT touch: src/training.py, src/data.py

## Researcher B Focus
Files: src/training.py, src/optimizer.py
Do NOT touch: src/models/
```

---

## Evaluator Produces Unexpected Output

**Symptom:** Researcher logs show metric values that do not match expectations. Metric may be going the wrong direction, producing NaN, or oscillating randomly.

**Diagnosis:** Run the evaluator manually on the baseline and on a known-good change:

```bash
# Baseline
python evaluate.py --input baseline.py
# Expected: 2.39 (seconds)
# Got: 0.002 (wrong scale — milliseconds vs seconds?)

# After a known improvement
python evaluate.py --input improved.py
# Expected: better than baseline
```

**Common causes and fixes:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| Metric in wrong direction | `direction: minimize` but evaluator returns higher = better | Flip direction in conference.md, or negate the metric in evaluator |
| Metric oscillating ±10% | Benchmark noise (warm/cold cache, garbage collection) | Average 3+ runs in evaluator; use `median` not `mean` |
| Metric is NaN or None | Evaluator crashes silently | Add explicit error handling and `sys.exit(1)` on failure |
| Metric always equals baseline | Researcher changes not reaching evaluator | Check that evaluator reads from the correct path |
| Metric improves then suddenly drops | Non-determinism in experiment (random seed) | Fix random seed in all scripts |

**Use the dry-run gate:** If you run `:plan`, Step 3 runs the evaluator before the conference starts. This catches most evaluator issues before they waste compute. If you skipped `:plan`, run the dry-run manually:

```bash
python evaluate.py --input current_baseline.py
```

---

## Conference Interrupted

**Symptom:** The conference stopped mid-run due to network timeout, system shutdown, or manual interruption. You want to continue without losing completed work.

**Fix:** Simply tell Claude to run the conference again on the same directory:

```
Resume the autoconference in ./my-conference/
```

The Chair reads `conference_events.jsonl`, finds the last `round.completed` event, and resumes from there. Completed rounds are never re-run.

See [resume.md](resume.md) for complete recovery documentation.

---

## Reviewer Overturns Everything

**Symptom:** Each round, the Reviewer marks most or all findings as `challenged` or `overturned`. `Shared Knowledge` stays empty. No progress across rounds.

**Root cause options:**

1. **Evaluator and Reviewer use different criteria** — the Reviewer expects success to mean X, but the evaluator measures Y.
2. **Measurement noise** — improvements are within the noise floor; the Reviewer correctly flags them.
3. **Overfitting** — improvements work on the training/benchmark set but the Reviewer detects they would not generalize.
4. **Reviewer prompt mismatch** — the Reviewer's criteria in the prompt does not match the `Success Metric` or `Success Criteria` in `conference.md`.

**Diagnosis:** Read `peer_review_round_1.md` carefully. The Reviewer states its reasons for overturning. The most common reasons are:

- "This improvement is within measurement noise" → reduce noise (see above)
- "This appears to overfit to the benchmark" → add a held-out evaluation set
- "The success criteria requires X but this result achieves Y" → align evaluator and Success Criteria

**Fix:**

If evaluator and Reviewer criteria are misaligned, update the `Success Metric` section to be explicit:

```markdown
## Success Metric
name: accuracy
target: "> 0.95"
direction: maximize
evaluator: python evaluate.py --split holdout
note: The evaluator uses the holdout split. Do not use the train split for evaluation.
```

If the Reviewer is too aggressive for your use case (e.g., you want fast iteration and accept some noise), you can lower the bar in the `Success Criteria` for qualitative mode, or accept `challenged` findings as valid for Shared Knowledge by updating the conference.md instructions.

---

## Poor Convergence

**Symptom:** The conference runs all `max_rounds` without converging. The final metric is better than baseline but did not hit the target. Synthesis is produced but the goal was not achieved.

**This is not a failure.** Budget exhaustion (`BUDGET_STOP`) is a valid outcome. The synthesis documents what was learned and how close you got. The question is how to improve in a follow-up run.

**Common causes and fixes:**

| Cause | Evidence | Fix |
|-------|----------|-----|
| Target is too aggressive | Progress curve shows diminishing returns well above target | Lower target or accept the achieved result |
| Search space too narrow | All researchers converge on similar approaches early | Expand `Allowed Changes` |
| Not enough rounds | Progress is still clearly improving at `max_rounds` | Increase `max_rounds` or resume |
| Wrong partitioning | One researcher finds all improvements; others are redundant | Re-partition based on what worked |
| `min_consensus_delta` too loose | Conference converges despite metric still improving | Tighten noise threshold |

**Using `:analyze` to diagnose:**

```
Analyze ./my-conference/ — why did it not converge?
```

The analysis will show which round produced the most improvement, whether any researcher plateaued early, and whether the Reviewer's overturns reduced effective exploration.

---

## Quick Reference

| Symptom | First action |
|---------|-------------|
| Researcher timeout | Check `conference_events.jsonl` for pattern; increase `researcher_timeout` or reduce `iterations_per_round` |
| All stalled | Expand `Allowed Changes` in `conference.md` |
| Worktree conflicts | Read resolution in `peer_review_round_N.md`; resolve manually if needed |
| Evaluator broken | Run evaluator manually on baseline; use `:plan` dry-run gate |
| Conference interrupted | Re-run on same directory; Chair auto-resumes |
| Reviewer overturns everything | Read overturn reasons in `peer_review_round_1.md`; align evaluator with Success Criteria |
| Poor convergence | Run `:analyze`; expand search space or increase rounds |
