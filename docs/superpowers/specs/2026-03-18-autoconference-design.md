# Autoconference — Design Specification

> Spawn a conference of autonomous researchers that compete, collaborate, and synthesize breakthroughs.

**Date:** 2026-03-18
**Status:** Approved
**Extends:** [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill)

---

## 1. Overview

Autoconference is a skill that orchestrates multiple autonomous researchers (each running the autoresearch loop) in a structured conference format. Researchers work independently, then periodically share findings, challenge each other's claims through adversarial peer review, and ultimately produce a synthesized result that combines the best insights from all participants.

### Core Interaction Model: Symposium + Debate

- **Symposium**: Researchers share findings periodically. After each round, they read each other's logs, learn from failures, and adapt.
- **Debate**: Researchers' claims are actively challenged by a reviewer agent. Only validated findings propagate to the next round.

### Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Interaction model | Symposium + Debate (B+D) | Sharing + adversarial review catches what self-evaluation misses |
| Research scope | Adaptive (metric or qualitative) | `conference.md` mode field determines behavior |
| Infrastructure | Subagent-first | Works in Claude Code today; Gemini/Codex CLI subagent support needs research |
| Output | Synthesized result | Combining insights > picking a winner |
| Scale | 2-N researchers, adaptive rounds | Convergence-based stopping, not fixed rounds |
| Structure | Conference Rounds | Predictable, debuggable, clear separation of concerns |

---

## 2. Naming & Identity

**Skill name:** `autoconference`
**Repo:** `autoconference-skill`
**Tagline:** *"Spawn a conference of autonomous researchers that compete, collaborate, and synthesize breakthroughs."*

Naming lineage: `autoresearch` → `autoconference` — clear parentage, immediately communicative.

---

## 3. The Conference Round

The fundamental unit of execution is a **Round**. A conference consists of multiple rounds until convergence or budget exhaustion.

```
┌─────────────────────────────────────────────────────────┐
│                    CONFERENCE ROUND                       │
│                                                           │
│  Phase 1: INDEPENDENT RESEARCH (parallel)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │Researcher│ │Researcher│ │Researcher│  Each runs N     │
│  │    A     │ │    B     │ │    C     │  autoresearch     │
│  │ (iter×N) │ │ (iter×N) │ │ (iter×N) │  iterations      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                 │
│       │             │            │                        │
│  Phase 2: POSTER SESSION                                 │
│  ┌──────────────────────────────────────┐                │
│  │ Session Chair collects all logs,     │                │
│  │ surfaces key findings & deltas       │                │
│  └──────────────────┬───────────────────┘                │
│                     │                                     │
│  Phase 3: PEER REVIEW (adversarial)                      │
│  ┌──────────────────────────────────────┐                │
│  │ Reviewer agent challenges claims:    │                │
│  │ - "Did metric actually improve?"     │                │
│  │ - "Is this overfitting?"             │                │
│  │ - "Could this be measurement noise?" │                │
│  └──────────────────┬───────────────────┘                │
│                     │                                     │
│  Phase 4: KNOWLEDGE TRANSFER                             │
│  ┌──────────────────────────────────────┐                │
│  │ Validated findings shared back to    │                │
│  │ all researchers for next round       │                │
│  └──────────────────────────────────────┘                │
│                                                           │
└─────────────────────────────────────────────────────────┘
          │
          ▼  Convergence check → next round or final synthesis
```

### Phase Details

**Phase 1 — Independent Research (parallel):**
Each researcher is a full autoresearch subagent running the 5-stage loop (Understand → Hypothesize → Experiment → Evaluate → Log) for `iterations_per_round` iterations within their assigned search space partition.

**Phase 2 — Poster Session:**
Session Chair (Haiku) collects all researcher logs and produces a structured summary: what each researcher tried, what worked, what failed, metric deltas.

**Phase 3 — Peer Review (adversarial):**
Reviewer (Opus) reads the poster session summary and challenges claims. Checks for overfitting, measurement noise, invalid comparisons, logical gaps. Assigns verdicts: `validated`, `challenged`, or `overturned`.

**Phase 4 — Knowledge Transfer:**
Conference Chair appends validated findings to each researcher's `Shared Knowledge` section. Researchers can build on each other's discoveries in the next round.

---

## 4. The `conference.md` Format

User-authored configuration file that drives the entire conference.

```markdown
# Conference: [Title]

## Goal
[What are we trying to achieve?]

## Mode
metric | qualitative
# metric → numeric optimization (like autoresearch)
# qualitative → reasoning quality judged by reviewer agent

## Success Metric (metric mode only)
name: [metric name]
target: [target value]
direction: maximize | minimize

## Success Criteria (qualitative mode only)
[Natural language description of what "good" looks like]
[The reviewer agent uses this to judge quality]

## Researchers
count: 3
iterations_per_round: 5
max_rounds: 4

## Search Space Partitioning
strategy: divergent | assigned | free
# divergent → system auto-assigns different strategies to each researcher
# assigned → user specifies each researcher's focus below
# free → all researchers explore freely (may overlap)

### Researcher A Focus (assigned mode only)
[e.g., "Explore architectural changes only"]

### Researcher B Focus (assigned mode only)
[e.g., "Explore hyperparameter tuning only"]

### Researcher C Focus (assigned mode only)
[e.g., "Explore data augmentation only"]

## Constraints
max_total_iterations: 60
token_budget: optional
time_budget: 2h

## Current Approach
[Baseline description]

## Shared Knowledge
[Auto-populated after each round with validated findings]

## Context & References
[Background, papers, URLs]

## Conference Log
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
[Auto-populated by Conference Chair]
```

### Key Differences from `research.md`

- **`Mode`** — switches between numeric optimization and qualitative deliberation
- **`Researchers`** — configures agent count, iterations per round, max rounds
- **`Search Space Partitioning`** — controls whether researchers explore different or overlapping areas
- **`Shared Knowledge`** — grows each round as validated findings accumulate
- **`Conference Log`** — tracks cross-researcher progress

---

## 5. TSV Logging

Two levels of machine-readable logs for analysis and CI integration.

### Per-Researcher TSV (`researcher_A_results.tsv`, etc.)

Same format as autoresearch:

```
iteration	metric_value	delta	delta_pct	status	description	timestamp
```

### Conference-Level TSV (`conference_results.tsv`)

Adds researcher identity, round context, and peer review verdicts:

```
round	researcher	iteration	metric_value	delta	delta_pct	status	description	peer_review_verdict	timestamp
```

- `peer_review_verdict`: `validated` | `challenged` | `overturned`
- **Qualitative mode**: `metric_value` is replaced with a reviewer-assigned quality score (1-10) so the TSV remains machine-readable

This enables:
- Convergence curve plotting per researcher
- Cross-researcher strategy comparison
- CI integration (same as autoresearch)
- Post-hoc analysis of peer review accuracy

---

## 6. Agent Roles

Five distinct roles with clear responsibilities and model tier assignments.

| Role | Model Tier | Count | Responsibility |
|------|-----------|-------|----------------|
| **Conference Chair** | Sonnet | 1 | Orchestrator. Spawns researchers, manages rounds, detects convergence, triggers synthesis. The main loop. |
| **Researcher** | Sonnet | N (user-defined) | Runs the autoresearch 5-stage loop independently within assigned search space. Produces per-researcher logs and TSV. |
| **Session Chair** | Haiku | 1 | Lightweight summarizer. Collects all researcher logs after each round and produces a structured poster session summary. |
| **Reviewer** | Opus | 1 | Adversarial critic. Challenges claims from poster session. Checks for overfitting, noise, invalid comparisons. Assigns verdicts. |
| **Synthesizer** | Opus | 1 | Runs once at the end. Reads all validated findings, identifies complementary insights, produces a unified synthesis — not just picking a winner. |

### Tier Rationale

- **Researchers at Sonnet** — high iteration volume; Opus would be cost-prohibitive
- **Reviewer at Opus** — adversarial reasoning requires the deepest model to catch subtle flaws
- **Session Chair at Haiku** — pure summarization, no deep reasoning needed
- **Synthesizer at Opus** — combining insights from multiple researchers requires strongest reasoning
- **Conference Chair at Sonnet** — orchestration logic, not deep analysis

---

## 7. Output Files

```
conference.md                    # User input (config)
conference_results.tsv           # Master conference-level TSV log

researcher_A_log.md              # Detailed per-researcher iteration logs
researcher_A_results.tsv         # Per-researcher TSV
researcher_B_log.md
researcher_B_results.tsv
researcher_C_log.md
researcher_C_results.tsv
...

poster_session_round_1.md        # Session Chair summaries per round
poster_session_round_2.md
...

peer_review_round_1.md           # Reviewer verdicts per round
peer_review_round_2.md
...

synthesis.md                     # Final synthesized output (Synthesizer)
final_report.md                  # Executive summary with full conference history
```

---

## 8. Lifecycle & Flow

### Complete Conference Lifecycle

```
USER writes conference.md
         │
         ▼
┌─ STARTUP ──────────────────────────────┐
│ Conference Chair:                       │
│ 1. Parse conference.md                  │
│ 2. Validate config (mode, count, etc.)  │
│ 3. Partition search space per strategy  │
│ 4. Initialize researcher log files      │
│ 5. Initialize conference_results.tsv    │
│ 6. Create worktrees (if metric + code)  │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │  ROUND LOOP    │◄──────────────────────┐
         └───────┬────────┘                        │
                 │                                  │
┌─ PHASE 1: INDEPENDENT RESEARCH (parallel) ──┐   │
│ Spawn N Researcher agents simultaneously     │   │
│ Each runs iterations_per_round iterations    │   │
│ Each writes to own log + TSV                 │   │
│ Each works in own worktree (if applicable)   │   │
└────────────────┬─────────────────────────────┘   │
                 │                                  │
┌─ PHASE 2: POSTER SESSION ───────────────────┐   │
│ Session Chair (Haiku) reads all logs         │   │
│ Produces poster_session_round_N.md           │   │
└────────────────┬─────────────────────────────┘   │
                 │                                  │
┌─ PHASE 3: PEER REVIEW ─────────────────────┐   │
│ Reviewer (Opus) reads poster session         │   │
│ Challenges claims, assigns verdicts          │   │
│ Produces peer_review_round_N.md              │   │
│ Updates conference_results.tsv verdicts       │   │
└────────────────┬─────────────────────────────┘   │
                 │                                  │
┌─ PHASE 4: KNOWLEDGE TRANSFER ───────────────┐   │
│ Conference Chair:                             │   │
│ - Appends validated findings to Shared        │   │
│   Knowledge in each researcher's context     │   │
│ - Cherry-picks validated code to best branch │   │
│ - Checks convergence criteria                │   │
└────────────────┬─────────────────────────────┘   │
                 │                                  │
          ┌──────▼──────┐                           │
          │ Converged?  │── no ─────────────────────┘
          └──────┬──────┘
                 │ yes
                 ▼
┌─ FINAL SYNTHESIS ──────────────────────────┐
│ Synthesizer (Opus):                         │
│ - Reads ALL round logs, reviews, findings  │
│ - Identifies complementary insights        │
│ - Produces synthesis.md                    │
│ - Produces final_report.md                 │
│ - Offers worktree merge/cleanup options    │
└─────────────────────────────────────────────┘
```

### Convergence Logic

| Condition | Mode | Trigger |
|-----------|------|---------|
| **Converged** | Metric | Best metric across all researchers didn't improve for 2 consecutive rounds |
| **Converged** | Qualitative | Reviewer rates all researcher outputs >= 8/10 for 2 consecutive rounds |
| **Budget stop** | Both | `max_total_iterations` or `max_rounds` or `time_budget` hit |
| **Stalled** | Both | All researchers at stuck Level 2+ simultaneously (early stop, triggers synthesis anyway) |

### Endgame Behavior (last round detected)

- Researchers switch from EXPLORE to EXPLOIT (micro-optimizations only)
- Reviewer focuses on validating final claims rather than challenging

---

## 9. Git Worktree Strategy

Worktrees activate **only for metric mode with code changes**. For prompt/config-only optimization or qualitative mode, separate files suffice.

### When Worktrees Activate

| Mode | Changes | Worktrees? |
|------|---------|-----------|
| Metric + code changes | Yes | Each researcher gets own worktree |
| Metric + prompt/config only | No | Separate files suffice |
| Qualitative | No | Researchers produce analysis, not code |

### Worktree Branch Structure

```
main (or user's current branch)
  ├── conference/researcher-A    ← worktree branch
  ├── conference/researcher-B    ← worktree branch
  ├── conference/researcher-C    ← worktree branch
  └── conference/best            ← validated improvements cherry-picked here
```

### Per-Round Worktree Lifecycle

1. **Round start**: Conference Chair creates/resets worktrees from `conference/best` (or current branch for round 1)
2. **Research phase**: Each researcher works in their isolated worktree
3. **Poster session**: Session Chair reads diffs from all worktrees (not just logs)
4. **Peer review**: Reviewer can run tests across worktrees via `/compare-worktrees` to verify claims
5. **Knowledge transfer**: Validated improvements cherry-picked to `conference/best`
6. **Next round**: Worktrees reset from `conference/best`

### Integration with Existing Skills

- **`/worktree-dashboard`** — user can monitor all researcher worktrees in real-time during a conference
- **`/compare-worktrees`** — used by Reviewer agent for static analysis + behavioral comparison between researcher branches

### Cleanup (after synthesis)

Conference Chair offers three options:
1. Merge `conference/best` into original branch
2. Keep worktrees for manual inspection
3. Clean up everything (delete worktrees and conference branches)

---

## 10. Hook Design

Event-based hooks for observability. Users wire these to notifications (Telegram/Discord/Slack) or custom scripts.

### Conference Events

| Event | When | Payload |
|-------|------|---------|
| `conference.started` | Conference Chair initializes | researcher count, mode, config summary |
| `round.started` | Each round begins | round number, researcher states |
| `researcher.iteration` | Researcher completes an iteration | researcher ID, iteration #, metric delta, kept/reverted |
| `round.poster_session` | Poster session complete | summary of findings |
| `round.peer_review` | Peer review complete | verdicts (validated/challenged/overturned counts) |
| `round.completed` | Round finishes | best metric, convergence status |
| `researcher.stuck` | Researcher hits stuck Level 2+ | researcher ID, stuck level |
| `conference.converged` | Convergence detected | final metrics, round count |
| `conference.completed` | Synthesis done | link to synthesis.md, final_report.md |

### Implementation

Events are written to `conference_events.jsonl` (append-only, one JSON object per line). External tools can tail this file for real-time monitoring.

Additionally, events map to Claude Code hooks (`PostToolUse`, `Stop`, etc.) for integration with OMC's notification system.

### Example: Slack Notification Setup

```
User runs: /configure-notifications slack
Then in conference.md:
  notify_on: round.completed, conference.converged, researcher.stuck
```

---

## 11. Value Assessment

### When Autoconference Adds Value

1. **Search space is large enough to partition** — multiple researchers exploring different regions find more than one exploring sequentially
2. **Problem benefits from diversity of approach** — different strategies cross-pollinate
3. **Self-evaluation has blind spots** — adversarial reviewer catches what single-agent autoresearch misses (Goodhart's Law mitigation)
4. **Synthesis > selection** — combining insights from multiple researchers produces results none could reach alone

### When Autoconference is Wasteful

- Trivial problems (single researcher converges in < 5 iterations)
- Tiny search spaces (nothing meaningful to partition)
- No clear metric or success criteria defined
- Problems where a single approach is obviously correct

### Token Efficiency

Not "more tokens" but "better tokens" — structured rounds with knowledge transfer mean later iterations are informed by earlier ones. Token efficiency improves over time within a conference.

---

## 12. Templates & Quick Conference

### Quick Conference Mode

Lightweight preset for testing whether a problem benefits from the conference format:

```markdown
## Researchers
count: 2
iterations_per_round: 3
max_rounds: 2
```

~12 total iterations + review overhead. Fast enough to validate the approach before committing to a full run.

### Shipped Templates

| Template | Mode | Use Case |
|----------|------|----------|
| `templates/prompt-optimization.md` | metric | Optimizing LLM prompts for accuracy/quality |
| `templates/code-performance.md` | metric | Optimizing code speed/efficiency/memory |
| `templates/research-synthesis.md` | qualitative | Literature exploration and hypothesis generation |

---

## 13. Cross-Platform Compatibility

### Current State

| Platform | Subagent Support | Status |
|----------|-----------------|--------|
| Claude Code | Full (Agent tool) | Ready |
| Gemini CLI | Recently added | Needs research |
| Codex CLI | Recently added | Needs research |

### Strategy

Build for Claude Code's `Agent` tool first. Abstract the subagent spawning interface so Gemini CLI and Codex CLI backends can be added without changing the core conference logic.

---

## 14. Open Questions

1. **Gemini/Codex CLI subagent API** — What's the exact interface? Can they run parallel subagents with model routing?
2. **Token budget estimation** — Can we predict total token cost from `conference.md` config before starting?
3. **Partial results on interruption** — If the user cancels mid-conference, how do we preserve what's been learned?
4. **Researcher memory across rounds** — Should researchers remember their own history across rounds, or start fresh with only shared knowledge?

---

*Design approved 2026-03-18. Ready for implementation planning.*
