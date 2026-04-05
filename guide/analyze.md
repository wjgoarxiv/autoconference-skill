# :analyze

The `:analyze` subcommand extracts structured insights from completed conference artifacts. Run it after any completed conference to understand what worked, what failed, and where the most leverage was.

---

## When to Run

Run `:analyze` after:

- A conference has finished (i.e., `synthesis.md` and `final_report.md` exist)
- You want to understand the trajectory across rounds before running a follow-up conference
- You have multiple completed conferences and want to compare strategies across them
- The `synthesis.md` summary is not detailed enough and you want deeper failure mode analysis

You can also run `:analyze` on a partially completed conference (mid-run), though the insights will be limited to completed rounds.

---

## What Insights It Extracts

### 1. Per-Researcher Trajectory

For each researcher, `:analyze` computes:

- Starting metric value (baseline)
- Best metric achieved and at which iteration
- Final metric value
- Number of `kept` vs `reverted` iterations (keep rate)
- Improvement curve shape: fast-start, slow-start, plateau, late-breakthrough

Example output:

```
Researcher A: baseline 2.40 → best 0.98 at iter 4 → final 1.05
  Keep rate: 4/5 (80%)
  Trajectory: fast-start (60% improvement in first 2 iterations)

Researcher B: baseline 2.40 → best 1.80 at iter 3 → final 1.95
  Keep rate: 2/5 (40%)
  Trajectory: plateau (no improvement after iter 3)

Researcher C: baseline 2.40 → best 0.82 at iter 5 → final 0.82
  Keep rate: 3/5 (60%)
  Trajectory: slow-start, late-breakthrough (best in final iteration)
```

### 2. Cross-Researcher Comparison

- Which search space partition produced the most improvement?
- Which researcher's findings were most frequently validated by the Reviewer?
- Which findings were overturned — and does the overturn pattern reveal a measurement issue?

### 3. Peer Review Accuracy

- Ratio of validated : challenged : overturned verdicts per round
- Findings that were `validated` by the Reviewer but not reflected in the final synthesis
- Findings that were `overturned` in early rounds but a different researcher later independently confirmed the same approach

### 4. Convergence Analysis

- Which round produced the largest improvement?
- How many rounds remained when convergence was declared?
- Was the conference budget well-spent, or did most improvement happen in round 1 (suggesting fewer rounds were needed)?

### 5. Failure Mode Inventory

- Iterations that were reverted: what was tried and why did it fail?
- Researchers who hit stuck Level 2 or Level 3: at what round, and what did re-spawn produce?
- Conferences that ended in `STALLED` rather than `CONVERGED` or `BUDGET_STOP`

---

## Trajectory Comparison

When you have two or more conferences on the same problem (e.g., a baseline conference and a follow-up with different researcher count or partitioning), `:analyze` can compare them side by side:

```
Compare analyses for ./conference-run-1/ and ./conference-run-2/
```

Output includes:

- Which run achieved better final metric
- Which run converged faster (rounds to 90% of final improvement)
- Whether the same strategies appeared in both (cross-run replication)
- Whether overturned claims in run 1 were independently validated in run 2

---

## Failure Mode Analysis

`:analyze` classifies each failed iteration into a failure category:

| Category | Description | Implication |
|----------|-------------|-------------|
| `measurement_noise` | Metric improved but Reviewer flagged as within noise threshold | Tighten noise_threshold or increase test set size |
| `overfitting` | Metric improved on training distribution, Reviewer flagged overfitting | Add held-out evaluation set |
| `search_space_exhausted` | Researcher hit Level 3 stuck | Partition was too narrow — consider expanding allowed changes |
| `evaluator_mismatch` | Metric improved but Reviewer used a different criterion | Evaluator and Reviewer criteria are misaligned |
| `timeout` | Researcher timed out | Increase researcher_timeout or reduce iterations_per_round |

---

## Insight Taxonomy Format

`:analyze` structures its output as a taxonomy with four tiers:

```
TIER 1: VALIDATED CONSENSUS
  Findings that were validated by the Reviewer AND appeared in synthesis
  → These are the most reliable results

TIER 2: VALIDATED, NOT SYNTHESIZED
  Findings validated by the Reviewer but missing from synthesis
  → May be worth explicitly highlighting in a follow-up

TIER 3: CHALLENGED (inconclusive)
  Findings the Reviewer flagged as questionable; not enough evidence to confirm or overturn
  → Candidates for targeted investigation in a follow-up conference or debate

TIER 4: OVERTURNED
  Findings the Reviewer determined were invalid
  → Document these as known-bad approaches; exclude from future search spaces
```

This taxonomy helps you build a structured record of what the conference learned, not just what the final synthesis says.

---

## Output

`:analyze` produces a single file: `conference_analysis.md` in the conference directory. The file includes:

- Trajectory table (all researchers, all rounds)
- Per-researcher failure inventory
- Peer review accuracy metrics
- Insight taxonomy (Tiers 1–4)
- Recommendations for follow-up (based on Tier 3 challenged findings and failure patterns)

If comparing multiple conferences, the output goes to `multi_conference_analysis.md` in the parent directory.

---

## Example

```
Analyze the conference in ./sorting-conference/
```

```
Analyzing ./sorting-conference/ (3 researchers, 3 rounds, 45 iterations)

TRAJECTORY
  Round 1: best improvement from Researcher C (radix sort: -59.1%)
  Round 2: convergence plateau — no improvement across all researchers
  Round 3: Researcher A late-breakthrough (hybrid merge+radix: -63.4%)
  
PEER REVIEW
  Total verdicts: 32 validated, 6 challenged, 2 overturned
  Overturn pattern: both overturns were "measurement noise" — sorting on warm cache

INSIGHT TAXONOMY
  Tier 1: radix sort base-256 (-59%), hybrid merge+radix (-63%)
  Tier 2: insertion sort threshold tuning (validated, not in final synthesis)
  Tier 3: SIMD-vectorized comparison (challenged — needs hardware validation)
  Tier 4: natural merge sort with run detection (overturned — cache-thrashing)

RECOMMENDATIONS
  Follow-up: run a targeted conference on SIMD vectorization with cold-cache benchmarking
  Expand allowed changes: memory alignment (currently forbidden)
```
