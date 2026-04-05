# Chains and Combinations

Commands compose. Each command produces artifacts that the next command consumes. This page documents the most useful chains, what flows between commands, and when to use each pattern.

---

## Standard Chains

### `plan → autoconference → ship`

The baseline pipeline. Use this for most problems.

```
plan         → produces conference.md (validated, evaluator verified)
autoconference → runs the conference (synthesis.md, final_report.md, conference_results.tsv)
ship         → formats findings for sharing (technical report, blog, paper section)
```

**What flows:**
- `plan` → `autoconference`: `conference.md` (complete configuration)
- `autoconference` → `ship`: `synthesis.md`, `final_report.md`, `conference_results.tsv`

**When to use:** You are starting fresh on a new problem and want to go from idea to shareable output in one session.

**Example:**
```
1. /plan — set up a conference on prompt accuracy optimization
2. Run the autoconference on the generated conference.md
3. /ship as a technical report
```

---

### `plan → autoconference → analyze → ship`

The standard pipeline with a post-conference analysis pass before shipping. Use this when the conference reveals unexpected findings you want to understand before committing to a report.

```
plan → autoconference → analyze → ship
```

**What flows:**
- `analyze` reads: all conference artifacts
- `analyze` → `ship`: `conference_analysis.md` (insight taxonomy, failure modes)
- `ship` incorporates analysis findings into the limitations and discussion sections

**When to use:**
- The convergence was slower than expected
- One researcher hit stuck Level 3 and you want to understand why
- The Reviewer overturned more findings than expected
- You want the shipped report to include a "lessons learned" section

**Example:**
```
1. Run conference on ./prompt-optimization/
2. Analyze ./prompt-optimization/ — produces conference_analysis.md
3. Ship as technical report — incorporates analysis findings in limitations section
```

---

### `debate → autoconference`

Run a debate first to understand the strongest arguments on both sides of a design question, then run a conference to empirically test the winning hypothesis.

```
debate       → produces verdict: strongest pro/con, recommended domain of truth
autoconference → tests the hypothesis in the domain where the verdict says it holds
```

**What flows:**
- `debate` produces a verdict with: strongest pro argument, strongest con argument, recommended restricted claim, confidence level
- The restricted claim from the debate verdict becomes the `Goal` in the conference's `conference.md`
- The `con` arguments inform the `Forbidden Changes` or `Search Space` constraints

**When to use:**
- You have a design choice between two approaches and want to understand the landscape before committing compute to testing
- You want to ensure the conference tests the right version of a hypothesis (one that accounts for the con arguments)

**Example:**
```
Debate: "Chain-of-thought prompting improves accuracy on multi-step reasoning tasks"

Verdict: TRUE for multi-step arithmetic (3+ steps); UNCERTAIN for single-step 
classification; FALSE for simple factual recall.

Conference: Optimize chain-of-thought prompting specifically for multi-step arithmetic.
Goal from verdict: maximize accuracy on 3+-step arithmetic benchmark (baseline: 67%).
```

---

### `survey → autoconference`

Use a literature survey to identify the most promising approaches, then run a conference to empirically compare them.

```
survey       → produces taxonomy of approaches from literature
autoconference → assigns each researcher to test one of the surveyed approaches
```

**What flows:**
- `survey` produces `synthesis.md` with: taxonomy of approaches, key papers, known limitations per approach
- Each researcher in the conference is assigned one approach from the taxonomy
- The `Current Approach` section in `conference.md` is populated from the survey's baseline findings
- The `Shared Knowledge` section is pre-seeded with the survey synthesis

**When to use:**
- You are entering a new domain and want to ground the conference in existing literature before experimenting
- The survey reveals that existing work has already tested some approaches — the conference can skip those and focus on the gaps

**Example:**
```
1. Survey: systematic review of RAG retrieval strategies (3 researchers, 2 rounds)
   Synthesis identifies: dense retrieval, sparse BM25, hybrid, hierarchical

2. Conference: 4 researchers, each testing one retrieval strategy on your document corpus
   Pre-seeded Shared Knowledge: survey findings on each strategy's known strengths/weaknesses
```

---

### `resume → autoconference`

Recover an interrupted conference and continue from the last completed round. This is not a separate command chain — it is what happens when you tell Claude to run a conference that already has artifacts in the directory.

```
resume → autoconference (continuation)
```

**What flows:**
- `resume` reads: `conference_events.jsonl` (determines last completed round), `conference.md` (reads Shared Knowledge), all researcher TSV files (reads last known good state)
- Continuation picks up exactly where the conference stopped

**When to use:** Any time a conference is interrupted before completion. See [resume.md](resume.md) for details.

---

### `analyze → debate`

Run analysis on a completed conference to find contentious findings (Tier 3: challenged, inconclusive), then run a debate to investigate the strongest version of each side.

```
analyze → identifies Tier 3 challenged findings
debate  → produces verdict on each contested finding
```

**What flows:**
- `analyze` produces `conference_analysis.md` with Tier 3 findings listed
- Each Tier 3 finding becomes a debate proposition
- The debate's verdict either promotes the finding to Tier 1 (validated) or demotes it to Tier 4 (overturned)

**When to use:**
- The Reviewer challenged several findings but did not overturn them (inconclusive)
- Two researchers reached opposite conclusions on the same question
- You want to understand why a finding was challenged before deciding whether to build on it

**Example:**
```
Conference on ML training optimization found: CHALLENGED — "Larger batch size consistently 
improves convergence speed." Reviewer flagged: "Contradicted by Goyal et al.; may require 
linear LR scaling."

Debate proposition: "Batch size scaling improves convergence speed when learning rate 
is scaled proportionally."

Verdict: TRUE for SGD with linear scaling rule; FALSE for Adam with fixed LR.
```

---

## Combining Multiple Chains

You can nest chains for complex research programs:

### Full research pipeline

```
plan → survey → autoconference → analyze → debate (on challenged findings) → ship
```

Use this for thorough, publication-quality research where you want literature grounding, empirical testing, rigorous analysis, and adversarial validation of contested findings before writing.

### Iterative improvement

```
autoconference (round 1) → analyze → autoconference (round 2, informed by analysis)
```

Run a short conference (2 rounds), analyze what worked, then run a deeper conference with the search space narrowed based on analysis findings. The second conference's `Shared Knowledge` is pre-seeded from the first conference's Tier 1 findings.

---

## What Each Command Produces (Quick Reference)

| Command | Key Output Files |
|---------|-----------------|
| `plan` | `conference.md` |
| `autoconference` | `synthesis.md`, `final_report.md`, `conference_results.tsv`, `conference_progress.png` |
| `analyze` | `conference_analysis.md` |
| `debate` | `debate_verdict.md` |
| `survey` | `synthesis.md`, `final_report.md` (survey-specific) |
| `ship` | `shipped/report.md`, supplementary charts and tables |
| `resume` | Continues existing conference; no new file type |
