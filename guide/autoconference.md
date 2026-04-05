# autoconference

Core reference for the main `autoconference` command. This is the conference loop itself — it reads a `conference.md` and orchestrates all researchers through structured rounds to synthesis.

---

## When to Use

Use `autoconference` when you already have a `conference.md` ready and want to run it. If you need to create the configuration file interactively, use [`:plan`](plan.md) first.

---

## Pre-Flight Setup

Before the conference starts, the Conference Chair asks 4 questions. These are not optional — the Chair waits for your explicit answers.

### Question 1: Researcher Count

How many parallel researchers should run? Options:

- **2 researchers** — A/B comparison. Good when you have two specific strategies to pit against each other.
- **3 researchers** (recommended) — Balanced diversity without excessive overhead. Suitable for most problems.
- **4–5 researchers** — Wide search space coverage. Expect higher token cost and wall-clock time.

If your `conference.md` already specifies `count`, the Chair confirms it rather than asking fresh.

### Question 2: Devil's Advocate

Should one researcher deliberately pursue contrarian strategies?

- **Yes** — One researcher is assigned to challenge mainstream assumptions, try the opposite of what seems obvious, and stress-test what other researchers take for granted. This catches blind spots and occasionally finds breakthroughs by invalidating a shared assumption.
- **No** — All researchers pursue constructive strategies in their assigned partitions.

If you have 3 researchers and add a Devil's Advocate, one of the 3 fills that role — no additional agent is spawned.

### Question 3: Overnight Execution

If you want the conference to run unattended:

```bash
# Foreground (simplest — Ctrl+C to stop)
bash scripts/autoconference-loop.sh ./my-conference/

# Background with nohup (no tmux needed)
nohup bash scripts/autoconference-loop.sh ./my-conference/ > conference.log 2>&1 &

# Background with tmux (best experience)
tmux new-session -d -s conference 'bash scripts/autoconference-loop.sh ./my-conference/'

# Check progress anytime
bash scripts/check_conference.sh ./my-conference/
```

Set `pause_every: never` in your `conference.md` for fully unattended runs. The loop script auto-detects your CLI tool.

### Question 4: Search Space Strategy

- **Assigned** (recommended) — Each researcher gets a specific focus area. Less overlap, more search space coverage.
- **Free** — All researchers explore the full space. More competition, potential redundancy. Useful when you're unsure how to partition.

---

## The 4-Phase Round Structure

Each round runs all 4 phases in strict sequence. Parallelism only happens within Phase 1.

```
┌─────────────────────────────────────────────┐
│                CONFERENCE ROUND              │
│                                             │
│  Phase 1: INDEPENDENT RESEARCH (parallel)  │
│  Researcher A │ Researcher B │ Researcher C │
│   N iterations  N iterations   N iterations  │
│         ↓            ↓             ↓         │
│  Phase 2: POSTER SESSION (Haiku)            │
│  Session Chair summarizes all findings      │
│                    ↓                        │
│  Phase 3: PEER REVIEW (Opus)               │
│  Reviewer challenges every claim            │
│  Verdicts: validated / challenged / overturned │
│                    ↓                        │
│  Phase 4: KNOWLEDGE TRANSFER               │
│  Validated findings → Shared Knowledge     │
│  Shared Knowledge → all researchers        │
└─────────────────────────────────────────────┘
            ↓
    Convergence check → next round or synthesis
```

### Phase 1: Independent Research

All N researchers run simultaneously (parallel agents). Each runs the autoresearch 5-stage loop — Understand → Hypothesize → Experiment → Evaluate → Log — for `iterations_per_round` iterations within their assigned search space partition.

If a researcher times out or crashes, the conference continues with partial results. The failed researcher is re-spawned next round from its last known good state.

### Phase 2: Poster Session

A lightweight Session Chair (Haiku) collects the last 10 iterations from each researcher's log and produces `poster_session_round_N.md` — a cross-researcher summary showing who found what, what improved, and what failed.

Phase 2 is skipped for single-researcher conferences (no cross-comparison needed).

### Phase 3: Peer Review

A Reviewer (Opus) reads the poster session and challenges every claim:
- "Did the metric actually improve, or is this measurement noise?"
- "Is this result overfitting to the evaluation benchmark?"
- "Is the comparison valid — same baseline, same test conditions?"

Each finding receives a verdict: `validated`, `challenged`, or `overturned`. Only `validated` findings advance to Shared Knowledge.

### Phase 4: Knowledge Transfer

The Conference Chair reads the review verdicts and:
1. Appends all `validated` findings to the `Shared Knowledge` section of `conference.md`
2. If using worktrees (code-change conferences): cherry-picks validated code changes to the `conference/best` branch
3. Updates `conference_results.tsv` with peer review verdicts
4. Logs a `round.completed` event to `conference_events.jsonl`

All researchers receive the updated `Shared Knowledge` at the start of the next round.

---

## Convergence Detection

The conference stops automatically when any of these conditions is met (checked after each round's Phase 4):

| Condition | Mode | Result |
|-----------|------|--------|
| Any researcher hit the target metric | metric | `CONVERGED` → synthesis |
| Best metric unchanged for 2 consecutive rounds | metric | `CONVERGED` → synthesis |
| Reviewer scores all outputs ≥ 8/10 for 2 consecutive rounds | qualitative | `CONVERGED` → synthesis |
| `max_rounds` reached | both | `BUDGET_STOP` → synthesis |
| `max_total_iterations` reached | both | `BUDGET_STOP` → synthesis |
| `time_budget` elapsed | both | `BUDGET_STOP` → synthesis |
| All researchers simultaneously at stuck Level 2+ | both | `STALLED` → early synthesis |

**The conference runs to completion automatically.** The Chair never asks "should I continue?" between rounds. Think of `max_rounds` as a budget to spend, not a limit to fear.

### Last Round (ENDGAME)

When the Chair knows this is the final round (budget limit approaching or convergence about to trigger), it signals `LAST_ROUND` to all researchers. They switch from EXPLORE to EXPLOIT mode — micro-optimizations only, no new risky strategies.

---

## Overnight Execution

For unattended runs, use the loop script:

```bash
bash scripts/autoconference-loop.sh ./my-conference/
```

The script:
- Auto-detects your CLI tool (Claude Code, Codex, OpenCode, Gemini)
- Handles round restarts if a round is interrupted
- Checks for conference completion between rounds
- Exits cleanly when the conference finishes

Check progress without stopping the conference:

```bash
bash scripts/check_conference.sh ./my-conference/
tail -f ./my-conference/conference_events.jsonl
```

---

## Output Files

| File | Updated | Description |
|------|---------|-------------|
| `conference.md` | Each round | Config + growing Shared Knowledge + Conference Log table |
| `conference_results.tsv` | Each iteration | All rounds, all researchers, with peer review verdicts |
| `conference_progress.png` | Each round | Live convergence plot (one line per researcher) |
| `conference_events.jsonl` | Continuously | Append-only event stream for monitoring |
| `researcher_{ID}_log.md` | Each iteration | Detailed per-researcher reasoning log |
| `researcher_{ID}_results.tsv` | Each iteration | Per-researcher TSV (compatible with autoresearch format) |
| `poster_session_round_N.md` | Each round | Session Chair's cross-researcher summary |
| `peer_review_round_N.md` | Each round | Reviewer verdicts for all claims |
| `synthesis.md` | End | Final combined output from Synthesizer (Opus) |
| `final_report.md` | End | Executive summary with full conference history |

---

## Common Configuration Patterns

### Fast iteration (prototyping)

```markdown
## Researchers
count: 2
iterations_per_round: 3
max_rounds: 2
```

Good for testing whether a problem benefits from the conference format before committing to a full run.

### Standard conference

```markdown
## Researchers
count: 3
iterations_per_round: 5
max_rounds: 4

## Constraints
max_total_iterations: 60
time_budget: 4h
researcher_timeout: 45m
```

### Overnight deep search

```markdown
## Researchers
count: 3
iterations_per_round: 10
max_rounds: 6

## Constraints
max_total_iterations: 180
time_budget: 12h
researcher_timeout: 90m
pause_every: never
```

### Single researcher with adversarial review

```markdown
## Researchers
count: 1
iterations_per_round: 8
max_rounds: 4
```

Degrades gracefully: Phase 2 (Poster Session) is skipped, but Phase 3 (Peer Review) still runs. You get autoresearch's optimization loop plus an Opus adversarial reviewer at the cost of one extra Opus call per round.

---

## Agent Roles and Models

| Role | Model | Count | What they do |
|------|-------|-------|--------------|
| Conference Chair | Sonnet | 1 | Orchestrates all rounds, manages convergence, triggers synthesis |
| Researcher | Sonnet | N | Runs the autoresearch 5-stage loop in their search space partition |
| Session Chair | Haiku | 1/round | Summarizes all researcher logs into the poster session |
| Reviewer | Opus | 1/round | Adversarial critic — challenges every claim, assigns verdicts |
| Synthesizer | Opus | 1 | Combines all validated findings at the end |

Opus is used only for Reviewer and Synthesizer — the roles that require the deepest reasoning. Researchers run at Sonnet because they iterate many times and Opus cost would be prohibitive.

---

## Relationship to autoresearch-skill

Each researcher runs the `autoresearch-skill` inner loop. Autoconference adds three layers on top:

1. **Multi-agent orchestration** — N researchers in parallel, each exploring a different region
2. **Adversarial peer review** — an Opus Reviewer challenges findings that self-evaluation would miss
3. **Synthesis** — a Synthesizer combines complementary insights rather than just picking the winner

If your problem is small enough for one agent, use `autoresearch-skill` directly. Autoconference's overhead (N researchers + reviewer + synthesizer per round) only pays off when the search space is large enough to partition, or when you need external validation of results.
