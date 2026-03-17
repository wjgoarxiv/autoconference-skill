# Autoconference — Design Specification

> Spawn a conference of autonomous researchers that compete, collaborate, and synthesize breakthroughs.

**Date:** 2026-03-18
**Status:** Approved (revised after spec review)
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
Session Chair (Haiku) collects all researcher logs and produces a structured summary: what each researcher tried, what worked, what failed, metric deltas. The Conference Chair passes all researcher log file paths, TSV file paths, and worktree paths (if applicable) in the Session Chair's prompt. To manage context size, the Session Chair receives **TSV summaries + the last N iteration entries from each log** (not full logs). Recommended cap: 5 researchers x 10 iterations max per round.

**Phase 3 — Peer Review (adversarial):**
Reviewer (Opus) reads the poster session summary and challenges claims. Checks for overfitting, measurement noise, invalid comparisons, logical gaps. Assigns verdicts: `validated`, `challenged`, or `overturned`.

**Phase 4 — Knowledge Transfer:**
Conference Chair appends validated findings to each researcher's `Shared Knowledge` section. Researchers can build on each other's discoveries in the next round.

### Mode-Specific Inner Loop Behavior

**Metric mode:** Each researcher runs the standard autoresearch 5-stage loop with the numeric metric from `conference.md`. Keep/revert decisions are mechanical — same as standalone autoresearch.

**Qualitative mode:** The autoresearch loop's Principle #2 (Mechanical Verification) cannot apply directly because there is no numeric metric. Instead, each researcher uses **self-assessment against the Success Criteria** as a proxy metric:

1. After each iteration, the researcher prompts itself: *"Rate this result 1-10 against the Success Criteria. Is it better than the previous best?"*
2. The self-assessed score drives keep/revert decisions during Phase 1 (the inner loop)
3. The Reviewer (Opus) in Phase 3 provides the **authoritative** judgment — it may overturn self-assessments
4. Self-assessment scores are logged to the per-researcher TSV as `metric_value`

This is an acknowledged departure from autoresearch's mechanical verification principle. The tradeoff: qualitative mode enables broader research tasks (literature synthesis, hypothesis generation) at the cost of less reliable inner-loop evaluation. The adversarial Reviewer in Phase 3 compensates by providing a rigorous external check each round.

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

## Search Space
### Allowed Changes
[What researchers CAN modify — inherited by all researchers]

### Forbidden Changes
[What researchers CANNOT modify — e.g., test data, evaluation scripts, API contracts]

## Search Space Partitioning
strategy: assigned | free
# assigned → user specifies each researcher's focus below
# free → all researchers explore freely (may overlap)
# (divergent → deferred to v2: auto-partitioning requires heuristic design)

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

### Parallel Execution Mechanism

Claude Code's `Agent` tool supports **multiple simultaneous tool calls in a single message block**. This is proven infrastructure — `ultrawork`, `dispatching-parallel-agents`, and OMC's team mode all use this pattern. The Conference Chair spawns N Researcher agents in a single message with N `Agent` tool calls, all with `run_in_background: true`. The Conference Chair is notified when each completes.

```
# Conference Chair sends ONE message with N parallel Agent calls:
Agent(subagent_type="executor", model="sonnet", prompt="[Researcher A prompt]", run_in_background=true)
Agent(subagent_type="executor", model="sonnet", prompt="[Researcher B prompt]", run_in_background=true)
Agent(subagent_type="executor", model="sonnet", prompt="[Researcher C prompt]", run_in_background=true)
```

**Fallback for environments without parallel support:** Run researchers sequentially with strict file-based isolation. Each researcher reads only its own log files and the shared knowledge section. Sequential execution is slower but functionally identical.

### Subagent Prompt Contracts

Each agent role receives a structured prompt from the Conference Chair. Required sections per role:

**Researcher prompt MUST include:**
- The full autoresearch 5-stage loop protocol (embedded from SKILL.md or referenced)
- This researcher's search space partition (from `assigned` focus or full space for `free`)
- The conference's `Allowed Changes` and `Forbidden Changes`
- Shared Knowledge from prior rounds (empty for round 1)
- Path to this researcher's log file and TSV file
- Path to this researcher's worktree (if applicable)
- `iterations_per_round` count
- Mode-specific evaluation instructions (numeric metric OR self-assessment criteria)

**Session Chair prompt MUST include:**
- Paths to ALL researcher log files and TSV files for the current round
- Paths to worktree diffs (if applicable)
- Output path for `poster_session_round_N.md`
- Instruction to summarize: what each researcher tried, results, metric deltas, notable failures

**Reviewer prompt MUST include:**
- Path to the poster session summary for this round
- The conference's Success Metric or Success Criteria
- Paths to researcher worktrees (for running tests, if applicable)
- Instructions to challenge claims: check for overfitting, measurement noise, invalid comparisons
- Output path for `peer_review_round_N.md`
- Verdict format: `validated` | `challenged` | `overturned` per finding

**Synthesizer prompt MUST include:**
- Paths to ALL poster session summaries and peer review documents
- Paths to ALL researcher logs and TSV files
- The conference's Goal and Success Metric/Criteria
- Instructions to combine complementary insights (not just pick a winner)
- Output paths for `synthesis.md` and `final_report.md`

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
- **Precedence rule:** Conference-level endgame overrides researcher-level endgame. If the Conference Chair signals "last round," ALL researchers switch to EXPLOIT regardless of their individual remaining iterations.

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

### Implementation (v1)

**v1 scope:** Events are written to `conference_events.jsonl` (append-only, one JSON object per line). Each line is a JSON object with `{ event, timestamp, payload }`. External tools can tail this file for real-time monitoring.

```jsonl
{"event":"conference.started","timestamp":"2026-03-18T10:00:00Z","payload":{"researchers":3,"mode":"metric","goal":"Optimize inference latency"}}
{"event":"round.started","timestamp":"2026-03-18T10:00:05Z","payload":{"round":1}}
{"event":"round.completed","timestamp":"2026-03-18T10:15:00Z","payload":{"round":1,"best_metric":0.82,"converged":false}}
```

**v2 (future):** Map events to Claude Code hooks and OMC's `/configure-notifications` for push notifications (Slack/Discord/Telegram). Would add a `notify_on` field to `conference.md`.

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

## 14. Failure Modes & Edge Cases

### Researcher Crash or Timeout

- Each researcher has a **per-researcher timeout** of `time_budget / researcher_count` (or a configurable `researcher_timeout` field)
- If a researcher crashes or times out, the Conference Chair proceeds to Phase 2 with partial results from completed researchers
- The failed researcher is logged in `conference_results.tsv` with status `FAILED` and excluded from that round's poster session
- On the next round, the failed researcher is re-spawned from its last known good state

### Researcher Self-Termination (Level 3 Stuck or Target Reached)

The autoresearch inner loop may terminate a researcher before `iterations_per_round` completes:
- **Target reached:** Researcher hit the success metric target. Conference Chair marks this researcher as `CONVERGED` and proceeds. If ALL researchers converge, skip to synthesis.
- **Level 3 stuck (7 consecutive non-improving):** Researcher produces its own `final_report.md`. Conference Chair marks it as `STALLED`, proceeds to Phase 2 with available results. On the next round, this researcher is re-spawned with a fundamentally different strategy derived from other researchers' shared knowledge.

### Merge Conflicts in Worktree Mode

When cherry-picking validated improvements to `conference/best`:
1. Conference Chair attempts automatic merge via `git merge --no-edit`
2. If conflicts arise, **only the researcher with the better metric delta gets their changes picked** for the conflicting files
3. Non-conflicting changes from both researchers are kept
4. Conflicts and resolutions are logged in `peer_review_round_N.md`

### Conference Resumption After Interruption

All per-round artifacts are persisted to disk as they are generated (logs, TSVs, poster sessions, reviews). On startup, the Conference Chair:
1. Checks for existing round artifacts in the working directory
2. Determines the last fully completed round (all 4 phases done)
3. Resumes from the next round, re-reading shared knowledge from the last completed round
4. If interrupted mid-round, discards incomplete round artifacts and re-runs from round start

### Single-Researcher Conference (count: 1)

Degrades gracefully to enhanced autoresearch with peer review:
- Phase 1 runs one researcher
- Phase 2 is skipped (nothing to compare)
- Phase 3 still runs (reviewer still challenges claims — this is the value-add over plain autoresearch)
- Per-researcher TSV uses `researcher_A_results.tsv` naming (not `autoresearch-results.tsv`) for consistency

---

## 15. Open Questions

1. **Gemini/Codex CLI subagent API** — What's the exact interface? Can they run parallel subagents with model routing?
2. **Token budget estimation** — Can we predict total token cost from `conference.md` config before starting?
3. **Researcher memory across rounds** — Should researchers remember their own full history across rounds, or start fresh with only shared knowledge? (Current design: fresh start + shared knowledge, to keep context windows manageable)
4. **`divergent` partitioning algorithm (v2)** — How should the system auto-assign different strategies? Requires heuristic design based on the search space description.

---

*Design approved 2026-03-18. Revised after spec review. Ready for implementation planning.*
