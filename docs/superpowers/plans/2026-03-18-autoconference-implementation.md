# Autoconference Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use subagent-driven-development (if subagents available) or executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `autoconference-skill` — a Claude Code skill that orchestrates multiple autoresearch agents in a structured conference format with symposium sharing, adversarial peer review, and synthesis.

**Architecture:** A SKILL.md file drives the conference orchestration. Reference documents define agent prompt contracts and protocols. Templates provide ready-to-use `conference.md` configs. A Python scaffolding script initializes new conference projects.

**Tech Stack:** Markdown (SKILL.md, references, templates), Python 3.8+ (init_conference.py, tests)

**Spec:** `docs/superpowers/specs/2026-03-18-autoconference-design.md`

---

## File Structure

```
autoconference-skill/
├── SKILL.md                              # Main skill — conference orchestration loop
├── README.md                             # Public documentation
├── LICENSE                               # MIT license
├── .gitignore                            # Python, OS, editor ignores
│
├── references/
│   ├── core-principles.md                # 7 inherited + 3 new conference principles
│   ├── agent-prompts.md                  # Prompt contracts for all 5 agent roles
│   ├── conference-protocol.md            # Round structure, convergence, failure modes
│   └── results-logging.md               # TSV logging protocol (per-researcher + conference-level)
│
├── assets/
│   ├── conference_template.md            # Template for user's conference.md
│   ├── synthesis_template.md             # Template for synthesis.md output
│   └── report_template.md               # Template for final_report.md output
│
├── templates/
│   ├── prompt-optimization.md            # Pre-built: optimize LLM prompts
│   ├── code-performance.md               # Pre-built: optimize code speed
│   └── research-synthesis.md             # Pre-built: qualitative literature exploration
│
├── scripts/
│   └── init_conference.py                # Scaffolding tool
│
├── tests/
│   └── test_init_conference.py           # Tests for scaffolding script
│
└── evals/
    └── evals.json                        # Skill evaluation scenarios
```

---

## Chunk 1: Foundation

Repository scaffold, conference.md template, core principles, and results logging.

### Task 1: Repository Scaffold

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`

- [ ] **Step 1: Create .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*.swo

# Research outputs (generated, not committed)
*_log.md
*_results.tsv
conference_events.jsonl
synthesis.md
final_report.md
poster_session_*.md
peer_review_*.md
```

- [ ] **Step 2: Create LICENSE**

Use MIT license with copyright holder `wjgoarxiv` and year `2026`.

- [ ] **Step 3: Commit**

```bash
git add .gitignore LICENSE
git commit -m "chore: add .gitignore and MIT license"
```

---

### Task 2: Conference Template (`assets/conference_template.md`)

**Files:**
- Create: `assets/conference_template.md`

This is the template users copy to start a new conference. Must match the format defined in spec Section 4.

- [ ] **Step 1: Write the conference template**

```markdown
# Conference: {Title}

## Goal
{Describe what the conference should achieve. Be specific and measurable.}

## Mode
{metric | qualitative}

## Success Metric
- **Metric:** {e.g., "accuracy on test set", "p95 latency", "LLM judge score 1-10"}
- **Target:** {e.g., "> 95%", "< 50ms", "> 8/10"}
- **Direction:** {maximize | minimize}

## Success Criteria
{For qualitative mode: natural language description of what "good" looks like.}
{For metric mode: leave blank or delete this section.}

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 4

## Search Space
- **Allowed changes:** {What researchers CAN modify}
- **Forbidden changes:** {What researchers CANNOT modify — e.g., test data, eval scripts}

## Search Space Partitioning
- **Strategy:** {assigned | free}

### Researcher A Focus
{For assigned strategy: describe this researcher's exploration area}

### Researcher B Focus
{For assigned strategy: describe this researcher's exploration area}

### Researcher C Focus
{For assigned strategy: describe this researcher's exploration area}

## Constraints
- **Max total iterations:** 60
- **Time budget:** 2h
- **Researcher timeout:** 30m

## Current Approach
{Describe the baseline. What exists now?}

## Shared Knowledge
<!-- Auto-populated after each round with validated findings -->

## Context & References
{Background material — papers, docs, URLs, code files}

---

## Conference Log
<!-- Auto-maintained by Conference Chair. Do not edit manually. -->
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
```

- [ ] **Step 2: Commit**

```bash
git add assets/conference_template.md
git commit -m "feat: add conference.md template"
```

---

### Task 3: Core Principles (`references/core-principles.md`)

**Files:**
- Create: `references/core-principles.md`

Inherits autoresearch's 7 principles and adds 3 conference-specific principles.

- [ ] **Step 1: Write core principles**

The file should contain:

**Section 1 — Inherited Principles (from autoresearch-skill):**
Reference the 7 original principles with a note: "These apply to each Researcher agent's inner loop. See [autoresearch-skill core-principles](https://github.com/wjgoarxiv/autoresearch-skill/blob/main/references/core-principles.md) for full explanations."

Briefly list them:
1. Single Metric
2. Mechanical Verification (with note: relaxed in qualitative mode — see Principle 9)
3. Atomic Changes
4. Keep or Revert
5. Full History
6. Constrained Search
7. Autonomous Loop

**Section 2 — Conference Principles (new):**

| # | Principle | Definition | conference.md Field |
|---|-----------|-----------|---------------------|
| 8 | **Knowledge Transfer** | Validated findings must propagate to all researchers between rounds. Without sharing, parallel research degenerates into N independent runs with no synergy. | `Shared Knowledge` section |
| 9 | **Adversarial Review** | Claims must survive challenge before propagating. Self-evaluation has blind spots (Goodhart's Law). An external reviewer with deep reasoning catches overfitting, noise, and invalid comparisons. | `peer_review_round_N.md` |
| 10 | **Synthesis Over Selection** | The final output combines complementary insights from multiple researchers, not just picks the winner. The conference's value is in cross-pollination — insights no single researcher would produce alone. | `synthesis.md` |

Include a "Why Each Principle Matters" section for principles 8-10, following the same format as autoresearch (Why, Violation consequence, Example).

- [ ] **Step 2: Commit**

```bash
git add references/core-principles.md
git commit -m "feat: add core principles (7 inherited + 3 conference)"
```

---

### Task 4: Results Logging Protocol (`references/results-logging.md`)

**Files:**
- Create: `references/results-logging.md`

Defines both per-researcher and conference-level TSV formats.

- [ ] **Step 1: Write the results logging protocol**

**Section 1 — Per-Researcher TSV (`researcher_{ID}_results.tsv`):**

Same schema as autoresearch's `autoresearch-results.tsv`:

| Column | Type | Description |
|--------|------|-------------|
| `iteration` | int | 0-indexed iteration number within the current round |
| `metric_value` | float | Measured metric value (or self-assessment score 1-10 in qualitative mode) |
| `delta` | float or `-` | Change from baseline |
| `delta_pct` | string | Percentage change from baseline |
| `status` | enum | `baseline`, `kept`, `reverted` |
| `description` | string | One-line description of the change |
| `timestamp` | ISO 8601 | When the experiment completed |

**Section 2 — Conference-Level TSV (`conference_results.tsv`):**

| Column | Type | Description |
|--------|------|-------------|
| `round` | int | Conference round number (1-indexed) |
| `researcher` | string | Researcher identifier (A, B, C, ...) |
| `iteration` | int | Iteration within the round |
| `metric_value` | float | Measured metric value |
| `delta` | float or `-` | Change from round baseline |
| `delta_pct` | string | Percentage change |
| `status` | enum | `baseline`, `kept`, `reverted`, `failed` |
| `description` | string | One-line description |
| `peer_review_verdict` | enum | `validated`, `challenged`, `overturned`, `-` |
| `timestamp` | ISO 8601 | When the experiment completed |

Include an example TSV block for each level, and a section on "Usage" (same as autoresearch: pandas analysis, CI integration, cross-project comparison).

**Section 3 — Event Log (`conference_events.jsonl`):**

Document the JSONL format with `{ event, timestamp, payload }` schema and list all event types from the spec.

- [ ] **Step 2: Commit**

```bash
git add references/results-logging.md
git commit -m "feat: add results logging protocol (per-researcher + conference TSV + JSONL events)"
```

---

## Chunk 2: Agent Contracts & Protocol

### Task 5: Agent Prompt Contracts (`references/agent-prompts.md`)

**Files:**
- Create: `references/agent-prompts.md`

Defines the exact prompt structure for each of the 5 agent roles. The SKILL.md will reference this file when spawning agents.

- [ ] **Step 1: Write agent prompt contracts**

For each role, define:
- **Role name and model tier**
- **System instruction** (the static part of the prompt)
- **Dynamic context** (what the Conference Chair injects per-round)
- **Expected output** (what files/artifacts the agent produces)

**Conference Chair (Sonnet):**
- System: "You are the Conference Chair orchestrating a multi-agent research conference. Your role is to manage rounds, spawn researchers, detect convergence, and trigger synthesis."
- Dynamic: conference.md content, current round number, researcher states
- Output: Updates to conference.md Conference Log, convergence decisions

**Researcher (Sonnet):**
- System: Embed the full autoresearch 5-stage loop protocol (from autoresearch-skill SKILL.md, sections "How It Works" through "Endgame Strategy")
- Dynamic: This researcher's search space partition, shared knowledge from prior rounds, paths to own log/TSV files, worktree path (if applicable), iterations_per_round, mode-specific evaluation (numeric metric OR self-assessment instructions)
- Output: `researcher_{ID}_log.md`, `researcher_{ID}_results.tsv`
- Special for qualitative mode: Include self-assessment prompt: "After each iteration, rate your result 1-10 against the Success Criteria. Use this as your keep/revert signal."

**Session Chair (Haiku):**
- System: "You are the Session Chair. Your job is to collect and summarize all researcher findings from this round into a structured poster session summary."
- Dynamic: Paths to all researcher TSV files and last N log entries, worktree diff summaries (if applicable)
- Output: `poster_session_round_{N}.md`
- Format: For each researcher: approach taken, iterations run, best metric, key findings, notable failures

**Reviewer (Opus):**
- System: "You are the Peer Reviewer. Your job is to critically evaluate claims from the poster session. Challenge anything that looks like overfitting, measurement noise, or invalid comparison. Assign verdicts."
- Dynamic: poster_session_round_{N}.md content, Success Metric/Criteria, worktree paths for running tests
- Output: `peer_review_round_{N}.md`
- Verdict format per finding: `validated` (claim holds), `challenged` (questionable, needs more evidence), `overturned` (claim is invalid)

**Synthesizer (Opus):**
- System: "You are the Synthesizer. Your job is to read all validated findings across all rounds and produce a unified result that combines the best insights — not just picks the winner."
- Dynamic: All poster_session and peer_review files, all researcher logs/TSVs, conference Goal and Success Metric/Criteria
- Output: `synthesis.md`, `final_report.md`

- [ ] **Step 2: Commit**

```bash
git add references/agent-prompts.md
git commit -m "feat: add agent prompt contracts for all 5 roles"
```

---

### Task 6: Conference Protocol (`references/conference-protocol.md`)

**Files:**
- Create: `references/conference-protocol.md`

The authoritative reference for round structure, convergence logic, failure handling, and worktree management. SKILL.md will reference this for detailed behavior.

- [ ] **Step 1: Write conference protocol**

**Section 1 — Round Structure:**
Document the 4-phase round (Independent Research → Poster Session → Peer Review → Knowledge Transfer) with exact entry/exit conditions for each phase.

**Section 2 — Convergence Logic:**
- Metric mode: Best metric across all researchers didn't improve for 2 consecutive rounds → CONVERGED
- Qualitative mode: Reviewer rates all outputs >= 8/10 for 2 consecutive rounds → CONVERGED
- Budget stop: max_total_iterations OR max_rounds OR time_budget hit
- Stalled: All researchers at stuck Level 2+ simultaneously → early synthesis

**Section 3 — Failure Modes:**
Copy the failure handling from spec Section 14:
- Researcher crash/timeout → proceed with partial results
- Researcher self-termination (Level 3 stuck or target reached) → mark status, proceed
- Merge conflicts in worktree mode → better-metric researcher wins conflicting files
- Conference resumption → detect existing round artifacts, resume from last complete round

**Section 4 — Endgame:**
- Conference-level endgame overrides researcher-level endgame
- Last round = all researchers in EXPLOIT mode

**Section 5 — Worktree Management:**
- When to create worktrees (metric mode + code changes only)
- Branch naming: `conference/researcher-{ID}`, `conference/best`
- Per-round lifecycle: create/reset → research → cherry-pick validated → next round
- Cleanup options after synthesis

**Section 6 — Qualitative Mode:**
- Self-assessment as proxy metric (1-10 scale)
- Reviewer provides authoritative scores
- Convergence threshold: reviewer >= 8/10 for all researchers, 2 consecutive rounds

- [ ] **Step 2: Commit**

```bash
git add references/conference-protocol.md
git commit -m "feat: add conference protocol reference (rounds, convergence, failure modes)"
```

---

## Chunk 3: SKILL.md — The Core Deliverable

### Task 7: Write SKILL.md

**Files:**
- Create: `SKILL.md`

This is the main skill file that Claude Code loads. It must be comprehensive enough that any Claude instance can orchestrate a full conference from reading this file alone, with references for detail.

- [ ] **Step 1: Write the SKILL.md frontmatter**

```yaml
---
name: autoconference-skill
description: |
  Multi-agent research conference that spawns parallel autoresearchers with
  symposium sharing, adversarial peer review, and insight synthesis.
  Reads a conference.md, orchestrates N researchers in structured rounds,
  and produces a synthesized result combining the best findings.
  TRIGGER when: user mentions "autoconference" or "conference" with research context;
  user wants multiple researchers competing or collaborating; user wants parallel
  autoresearch with peer review; user mentions "conference.md"; user wants
  research synthesis from multiple approaches; user wants adversarial evaluation
  of research results.
  DO NOT TRIGGER when: user wants a single autoresearch loop (use autoresearch-skill);
  user wants a simple one-shot answer; user wants to read a single paper.
allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---
```

- [ ] **Step 2: Write the skill body**

Structure the body following the autoresearch-skill pattern but adapted for conference orchestration:

**Section: "When to Use This Skill"**
- Parallel research with peer review
- Problems benefiting from diverse approaches
- Any task where autoresearch alone has blind spots
- Large search spaces that benefit from partitioning
- NOT for: trivial problems, tiny search spaces, single-approach problems

**Section: "How It Works"**
The conference round diagram from the spec, plus brief descriptions of each phase.

**Section: "The conference.md Format"**
Reference `assets/conference_template.md` for the full template. Briefly describe each section.

**Section: "Conference Orchestration Protocol"**

This is the main loop. Structure it as a numbered protocol the Conference Chair follows:

```
STARTUP:
1. Read conference.md
2. Validate: mode, researcher count, constraints
3. Detect worktree need (metric mode + code changes → create worktrees)
4. Initialize output files (per-researcher logs, TSVs, conference_results.tsv, conference_events.jsonl)
5. Partition search space per strategy

ROUND LOOP:
6. Phase 1 — Spawn N Researcher agents in parallel (see references/agent-prompts.md)
   - Use Agent tool with run_in_background: true
   - Each researcher gets: autoresearch loop protocol, their search space, shared knowledge, file paths
   - Wait for all to complete (or timeout)
7. Phase 2 — Spawn Session Chair (Haiku) to summarize findings
   - Pass: all researcher TSVs + last N log entries + worktree diffs
   - Output: poster_session_round_{N}.md
8. Phase 3 — Spawn Reviewer (Opus) for adversarial review
   - Pass: poster session summary, success metric/criteria, worktree paths
   - Output: peer_review_round_{N}.md with verdicts
9. Phase 4 — Knowledge Transfer
   - Read peer review verdicts
   - Append validated findings to Shared Knowledge
   - Cherry-pick validated code to conference/best (if worktree mode)
   - Update conference_results.tsv with verdicts
   - Log round.completed event
10. Check convergence (see references/conference-protocol.md)
    - If converged/budget/stalled → exit loop
    - If last round → signal endgame to researchers
    - Else → next round

SYNTHESIS:
11. Spawn Synthesizer (Opus)
    - Pass: all round artifacts, all researcher logs, goal/criteria
    - Output: synthesis.md, final_report.md
12. If worktree mode → offer cleanup options
13. Log conference.completed event
```

**Section: "Agent Roles"**
Table of 5 roles with model tier and responsibility (from spec Section 6). Reference `references/agent-prompts.md` for full prompt contracts.

**Section: "Output Structure"**
List all output files (from spec Section 7).

**Section: "Safety & Guardrails"**
- max_total_iterations hard cap
- max_rounds hard cap
- time_budget wall-clock limit
- researcher_timeout per-researcher limit
- Automatic rollback per researcher (inherited from autoresearch)
- Forbidden changes enforcement (inherited)

**Section: "Stuck Detection"**
- Per-researcher: inherited from autoresearch (Level 1/2/3)
- Conference-level: all researchers at Level 2+ → trigger synthesis early

**Section: "Convergence Logic"**
Table from spec Section 8.

**Section: "Qualitative Mode"**
Self-assessment proxy metric explanation. Reference `references/conference-protocol.md` Section 6.

**Section: "Git Worktree Integration"**
When worktrees activate, branch structure, per-round lifecycle. Reference `/worktree-dashboard` and `/compare-worktrees` skills.

**Section: "Event Hooks"**
Event table + JSONL format. Reference `references/results-logging.md` Section 3.

**Section: "Dependencies"**
- Required: Claude Code with Agent tool support
- Extends: autoresearch-skill (each researcher runs the autoresearch loop)
- Optional: `/worktree-dashboard`, `/compare-worktrees` for worktree monitoring

**Section: "Relationship to Other Skills"**
| Skill | Relationship |
|-------|-------------|
| autoresearch-skill | Parent. Each researcher runs the autoresearch loop. |
| worktree-dashboard | Complementary. Monitor researcher worktrees during conference. |
| compare-worktrees | Complementary. Reviewer uses this for cross-worktree analysis. |

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat: add SKILL.md — main conference orchestration skill"
```

---

## Chunk 4: Templates, Tooling & Docs

### Task 8: Report Templates

**Files:**
- Create: `assets/synthesis_template.md`
- Create: `assets/report_template.md`

- [ ] **Step 1: Write synthesis template**

```markdown
# Conference Synthesis: {Title}

**Generated:** {date}
**Conference Rounds:** {n}
**Researchers:** {count}
**Mode:** {metric | qualitative}

---

## Unified Result

{The synthesizer's combined result — not just the winner, but a fusion of complementary insights from multiple researchers.}

## Key Insights by Researcher

### Researcher A: {Focus Area}
- **Best finding:** {description}
- **Contribution to synthesis:** {how this insight was incorporated}

### Researcher B: {Focus Area}
- **Best finding:** {description}
- **Contribution to synthesis:** {how this insight was incorporated}

{repeat for each researcher}

## Cross-Pollination

{Insights that emerged from combining approaches — things no single researcher would have found alone.}

## Validated vs. Overturned Claims

| Claim | Researcher | Verdict | Reason |
|-------|-----------|---------|--------|
{rows from peer review}

## Recommendations

- {Next steps if the user wants to continue}
- {Ideas that emerged but weren't fully explored}
```

- [ ] **Step 2: Write report template**

```markdown
# Conference Report: {Title}

**Generated:** {date}
**Total Rounds:** {n}
**Total Iterations:** {sum across all researchers}
**Best Metric:** {value} ({direction}: {metric name})
**Status:** {converged | budget_stop | stalled}

---

## Executive Summary

{2-3 sentences: what was researched, the best result, and the key insight from synthesis.}

## Best Result

- **Source:** Researcher {ID}, Round {n}, Iteration {i}
- **Change:** {what was different from baseline}
- **Metric Value:** {value} (baseline: {baseline}, improvement: {delta})

## Conference Timeline

| Round | Phase | Key Event | Metric |
|-------|-------|-----------|--------|
{rows}

## Per-Researcher Summary

| Researcher | Focus | Iterations | Best Metric | Kept Changes | Stuck Level |
|-----------|-------|------------|-------------|-------------|-------------|
{rows}

## Peer Review Summary

| Round | Validated | Challenged | Overturned |
|-------|-----------|------------|------------|
{rows}

## Key Findings

1. {Pattern discovered across researchers}
2. {What worked consistently}
3. {Surprising result from synthesis}

## Failed Approaches

1. {Approaches tried by multiple researchers that consistently failed}
2. {Dead ends worth documenting}

## Recommendations

- {Next steps}
- {Unexplored areas identified during synthesis}
```

- [ ] **Step 3: Commit**

```bash
git add assets/synthesis_template.md assets/report_template.md
git commit -m "feat: add synthesis and report templates"
```

---

### Task 9: Shipped Conference Templates

**Files:**
- Create: `templates/prompt-optimization.md`
- Create: `templates/code-performance.md`
- Create: `templates/research-synthesis.md`

- [ ] **Step 1: Write prompt-optimization template**

A pre-filled `conference.md` for optimizing LLM prompts:
- Mode: metric
- Metric: accuracy on test cases (direction: maximize)
- Researchers: 3 (assigned strategy)
  - A: Structural changes (few-shot, CoT, output format)
  - B: Content changes (phrasing, examples, persona)
  - C: Meta-optimization (temperature, sampling, prompt length)
- Constraints: max_total_iterations 45, time_budget 1h
- Search space: allowed = system prompt text, forbidden = test cases, model choice

- [ ] **Step 2: Write code-performance template**

A pre-filled `conference.md` for optimizing code speed:
- Mode: metric
- Metric: execution_time_seconds (direction: minimize)
- Researchers: 3 (assigned strategy)
  - A: Algorithmic changes
  - B: Data structure optimization
  - C: Low-level optimization (caching, memory layout, vectorization)
- Constraints: max_total_iterations 45, time_budget 2h
- Search space: allowed = implementation code, forbidden = test harness, input data

- [ ] **Step 3: Write research-synthesis template**

A pre-filled `conference.md` for qualitative literature exploration:
- Mode: qualitative
- Success Criteria: "Comprehensive taxonomy of the research area with >=15 papers, clear identification of research gaps, and novel cross-domain connections"
- Researchers: 3 (assigned strategy)
  - A: Foundational papers and surveys
  - B: Recent advances (last 2 years)
  - C: Adjacent fields and cross-domain connections
- Constraints: max_total_iterations 30, max_rounds 3
- No worktrees (qualitative mode)

- [ ] **Step 4: Commit**

```bash
git add templates/
git commit -m "feat: add shipped conference templates (prompt, code-perf, research-synthesis)"
```

---

### Task 10: Scaffolding Script (`scripts/init_conference.py`)

**Files:**
- Create: `scripts/init_conference.py`
- Create: `tests/test_init_conference.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for init_conference.py scaffolding script."""
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "init_conference.py"


def run_init(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    """Helper to invoke init_conference.py."""
    return subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--goal", "Optimize inference latency",
            "--metric", "p95_latency_ms",
            "--direction", "minimize",
            "--target", "< 50",
            "--researchers", "3",
            "--strategy", "assigned",
            "--output", str(tmp_path / "my-conference"),
            *extra_args,
        ],
        capture_output=True,
        text=True,
    )


def test_creates_conference_md(tmp_path):
    result = run_init(tmp_path)
    assert result.returncode == 0
    conf = tmp_path / "my-conference" / "conference.md"
    assert conf.exists()
    text = conf.read_text()
    assert "Optimize inference latency" in text
    assert "p95_latency_ms" in text
    assert "minimize" in text
    assert "< 50" in text


def test_creates_tsv_files(tmp_path):
    run_init(tmp_path)
    base = tmp_path / "my-conference"
    assert (base / "conference_results.tsv").exists()
    for rid in ["A", "B", "C"]:
        assert (base / f"researcher_{rid}_results.tsv").exists()
        assert (base / f"researcher_{rid}_log.md").exists()


def test_creates_events_jsonl(tmp_path):
    run_init(tmp_path)
    events = tmp_path / "my-conference" / "conference_events.jsonl"
    assert events.exists()
    assert events.read_text() == ""  # empty at init


def test_qualitative_mode(tmp_path):
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--goal", "Survey LLM agent papers",
            "--mode", "qualitative",
            "--criteria", "Comprehensive taxonomy with 15+ papers",
            "--researchers", "2",
            "--output", str(tmp_path / "qual-conf"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    conf = tmp_path / "qual-conf" / "conference.md"
    text = conf.read_text()
    assert "qualitative" in text
    assert "Comprehensive taxonomy" in text


def test_rejects_missing_metric_in_metric_mode(tmp_path):
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--goal", "Something",
            "--output", str(tmp_path / "bad"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd /Users/woojin/Desktop/02_Areas/01_Codes_automation/15_autoconference-skill
python -m pytest tests/test_init_conference.py -v
```

Expected: FAIL (script doesn't exist yet)

- [ ] **Step 3: Write init_conference.py**

Follows the pattern of autoresearch's `init_research.py` but extended for conferences:

- `--goal` (required): Conference goal
- `--mode` (default: `metric`): `metric` or `qualitative`
- `--metric` (required for metric mode): Metric name
- `--direction` (required for metric mode): `maximize` or `minimize`
- `--target` (default: `TBD`): Target value
- `--criteria` (required for qualitative mode): Success criteria text
- `--researchers` (default: `3`): Number of researchers
- `--strategy` (default: `free`): `assigned` or `free`
- `--iterations-per-round` (default: `5`): Iterations per round
- `--max-rounds` (default: `4`): Maximum rounds
- `--output` (default: `./conference/`): Output directory

Creates:
- `conference.md` (from template, filled in)
- `researcher_{A,B,...}_log.md` (empty log headers)
- `researcher_{A,B,...}_results.tsv` (header + baseline row)
- `conference_results.tsv` (header only)
- `conference_events.jsonl` (empty)
- `workspace/` directory

- [ ] **Step 4: Run tests — verify they pass**

```bash
python -m pytest tests/test_init_conference.py -v
```

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/init_conference.py tests/test_init_conference.py
git commit -m "feat: add init_conference.py scaffolding script with tests"
```

---

### Task 11: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

Follow the autoresearch-skill README pattern:

- **Title + tagline** with badge links (GitHub stars, license)
- **TL;DR:** 3-sentence explanation
- **How It Works:** The conference round diagram
- **Quick Start:**
  1. Install: `claude skills add /path/to/autoconference-skill`
  2. Scaffold: `python scripts/init_conference.py --goal "..." --metric "..." --direction maximize`
  3. Edit `conference.md` to fill in details
  4. Run: tell Claude "Run the autoconference on my conference.md"
- **The conference.md Format:** Brief section descriptions
- **Agent Roles:** Table of 5 roles
- **Output Files:** What gets produced
- **Templates:** List the 3 shipped templates
- **Configuration Options:** Table of all conference.md fields
- **Relationship to autoresearch-skill:** "Each researcher runs the autoresearch loop. Autoconference adds multi-agent orchestration, peer review, and synthesis on top."
- **Cross-Platform Compatibility:** Claude Code (ready), Gemini CLI / Codex CLI (future)
- **License:** MIT

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "feat: add README with quick start and documentation"
```

---

### Task 12: Evaluation Scenarios

**Files:**
- Create: `evals/evals.json`

- [ ] **Step 1: Write eval scenarios**

Create 5-6 evaluation scenarios that test the skill's trigger accuracy:

```json
[
  {
    "input": "Run an autoconference with 3 researchers to optimize my sorting algorithm",
    "expected_skill": "autoconference-skill",
    "should_trigger": true
  },
  {
    "input": "Set up a conference.md and have multiple researchers compete on prompt quality",
    "expected_skill": "autoconference-skill",
    "should_trigger": true
  },
  {
    "input": "I want parallel research with peer review on my ML pipeline",
    "expected_skill": "autoconference-skill",
    "should_trigger": true
  },
  {
    "input": "Optimize my prompt iteratively until accuracy exceeds 90%",
    "expected_skill": "autoresearch-skill",
    "should_trigger": false,
    "note": "Single researcher loop — should trigger autoresearch, not autoconference"
  },
  {
    "input": "Summarize this paper for me",
    "expected_skill": "scientific-reading",
    "should_trigger": false
  },
  {
    "input": "Review my conference.md and start the research conference with adversarial review",
    "expected_skill": "autoconference-skill",
    "should_trigger": true
  }
]
```

- [ ] **Step 2: Commit**

```bash
git add evals/evals.json
git commit -m "feat: add skill evaluation scenarios"
```

---

### Task 13: Final Verification

- [ ] **Step 1: Run all tests**

```bash
cd /Users/woojin/Desktop/02_Areas/01_Codes_automation/15_autoconference-skill
python -m pytest tests/ -v
```

Expected: ALL PASS

- [ ] **Step 2: Verify file structure**

```bash
find . -type f -not -path './.git/*' -not -path './.omc/*' -not -path './docs/*' | sort
```

Verify all files from the File Structure section exist.

- [ ] **Step 3: Verify SKILL.md references are valid**

Check that all file paths referenced in SKILL.md (`references/`, `assets/`, `templates/`) actually exist.

- [ ] **Step 4: Final commit (if any cleanup needed)**

```bash
git add -A
git commit -m "chore: final cleanup and verification"
```

---

*Plan complete. 13 tasks across 4 chunks. Estimated: ~30 files created.*
