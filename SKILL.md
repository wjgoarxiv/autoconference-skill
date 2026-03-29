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
  - WebFetch
  - WebSearch
---

# Autoconference — Multi-Agent Research Conference

*Spawn a conference of autonomous researchers that compete, collaborate, and synthesize breakthroughs.*

## Conference Persistence Directive

**The Conference Chair is relentless.** Once the conference begins:

1. **NEVER STOP** a round prematurely. Each round runs all 4 phases to completion.
2. **NEVER ASK** "should I continue to the next round?" Advance automatically.
3. **Use the full budget.** If `max_rounds` is 5, run 5 rounds. Stopping at round 2 wastes 60% of the exploration budget.
4. **The conference runs until one of these conditions is met:**
   - Target metric achieved (convergence)
   - `max_rounds` or `max_total_iterations` exhausted (budget spent — this is normal, not failure)
   - All researchers simultaneously stalled at Level 2+ (early synthesis)
   - The user manually interrupts
5. **If none of these conditions are true, begin the next round immediately.**

Think of `max_rounds` as a budget to *spend*, not a limit to *fear*.

## When to Use This Skill

Use autoconference when:
- The **search space is large enough to partition** — multiple researchers exploring different regions find more than one exploring sequentially
- The **problem benefits from diverse approaches** — different strategies cross-pollinate
- **Self-evaluation has blind spots** — adversarial reviewer catches what single-agent autoresearch misses (Goodhart's Law mitigation)
- **Synthesis > selection** — combining insights from multiple researchers produces results none could reach alone

Do NOT use when:
- A single autoresearch loop would suffice (use `autoresearch-skill` instead)
- The problem is trivial or has a tiny search space
- No clear metric or success criteria is defined
- A single approach is obviously correct

## How It Works

Each conference consists of multiple **Rounds** until convergence or budget exhaustion:

```
┌─────────────────────────────────────────────────────────┐
│                    CONFERENCE ROUND                       │
│                                                           │
│  Phase 1: INDEPENDENT RESEARCH (parallel)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │Researcher│ │Researcher│ │Researcher│  Each runs N     │
│  │    A     │ │    B     │ │    C     │  autoresearch    │
│  │ (iter×N) │ │ (iter×N) │ │ (iter×N) │  iterations     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                 │
│       │             │            │                        │
│  Phase 2: POSTER SESSION                                 │
│  ┌──────────────────────────────────────┐                │
│  │ Session Chair (Haiku) collects logs, │                │
│  │ surfaces key findings & deltas       │                │
│  └──────────────────┬───────────────────┘                │
│                     │                                     │
│  Phase 3: PEER REVIEW (adversarial)                      │
│  ┌──────────────────────────────────────┐                │
│  │ Reviewer (Opus) challenges claims:   │                │
│  │ validated | challenged | overturned  │                │
│  └──────────────────┬───────────────────┘                │
│                     │                                     │
│  Phase 4: KNOWLEDGE TRANSFER                             │
│  ┌──────────────────────────────────────┐                │
│  │ Validated findings → Shared Knowledge│                │
│  │ in all researchers for next round    │                │
│  └──────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────┘
          │
          ▼  Convergence check → next round or final synthesis
```

## The conference.md Format

Copy `assets/conference_template.md` to start a new conference (or scaffold with `python scripts/init_conference.py`). Key sections:

| Section | Purpose |
|---------|---------|
| `Goal` | What to achieve (specific and measurable) |
| `Mode` | `metric` (numeric optimization) or `qualitative` (reasoned judgment) |
| `Success Metric` | Metric name, target, direction — metric mode only |
| `Success Criteria` | Natural language description of "good" — qualitative mode only |
| `Researchers` | count, iterations_per_round, max_rounds |
| `Search Space` | Allowed and forbidden changes (inherited by all researchers) |
| `Search Space Partitioning` | `assigned` (each researcher has a focus) or `free` (overlap allowed) |
| `Constraints` | max_total_iterations, time_budget, researcher_timeout |
| `Current Approach` | Baseline description |
| `Shared Knowledge` | Auto-populated each round with validated findings |
| `Conference Log` | Auto-maintained table by Conference Chair |

## Conference Orchestration Protocol

This is the master loop. Follow it exactly as the Conference Chair.

### STARTUP

**1. Read conference.md**
Parse all sections. If any required field is missing or invalid, stop and tell the user what needs fixing before proceeding.

**2. Validate configuration**
- `mode` must be `metric` or `qualitative`
- `count` must be >= 1
- Metric mode: `Success Metric` must have name, target, and direction
- Qualitative mode: `Success Criteria` must be non-empty
- `max_total_iterations` and `max_rounds` must be positive integers

**3. Detect worktree need**
If `mode == metric` AND researchers will make code changes → create per-researcher git worktrees (branches: `conference/researcher-{ID}`, plus `conference/best`). For prompt/config-only or qualitative mode, file-based isolation is sufficient. See `references/conference-protocol.md` §5 for full worktree lifecycle.

**4. Initialize output files**
For each researcher `{ID}` in `[A, B, C, ...]` (up to `count`):
- Create `researcher_{ID}_log.md` (empty with header)
- Create `researcher_{ID}_results.tsv` (header + baseline row)

Create `conference_results.tsv` (header only) and `conference_events.jsonl` (empty).
Log `conference.started` event to JSONL.

**5. Partition search space**
- `strategy: assigned` → read Researcher A/B/C Focus sections from conference.md
- `strategy: free` → all researchers receive the full search space

### ROUND LOOP

**6. Phase 1 — Spawn N Researcher agents in parallel**
Spawn all N researchers simultaneously using the `Agent` tool with `run_in_background: true`. Log `round.started` event.

Each Researcher prompt MUST include (see `references/agent-prompts.md` §Researcher for full contract):
- The autoresearch 5-stage loop protocol: Understand → Hypothesize → Experiment → Evaluate → Log
- This researcher's search space partition (assigned focus OR full space for `free`)
- The conference's Allowed Changes and Forbidden Changes
- Shared Knowledge from prior rounds (empty for round 1)
- Path to this researcher's log file and TSV file
- Path to this researcher's worktree (if worktree mode)
- `iterations_per_round` count
- Mode-specific evaluation: numeric metric (metric mode) OR self-assessment 1-10 against Success Criteria (qualitative mode)
- If this is the last round: explicit instruction "ENDGAME MODE — switch from EXPLORE to EXPLOIT only"

Wait for all researchers to complete (respect `researcher_timeout`). If a researcher crashes or times out, proceed with partial results from completed researchers; log status `failed` in `conference_results.tsv`. Re-spawn failed researchers next round from their last known good state.

**7. Phase 2 — Spawn Session Chair (Haiku) to produce poster session**
Spawn one Session Chair agent. Prompt MUST include:
- Paths to all researcher TSV files + last 10 log entries per researcher (not full logs — context size management)
- Worktree diff summaries (if worktree mode)
- Output path: `poster_session_round_{N}.md`
- Instruction: for each researcher, summarize approach taken, iterations run, best metric, key findings, notable failures

Log `round.poster_session` event.

**8. Phase 3 — Spawn Reviewer (Opus) for adversarial peer review**
Spawn one Reviewer agent. Prompt MUST include:
- Path to `poster_session_round_{N}.md`
- The conference's Success Metric or Success Criteria
- Paths to researcher worktrees (for running validation tests, if applicable)
- Output path: `peer_review_round_{N}.md`
- Instruction: challenge every claim — check for overfitting, measurement noise, invalid comparisons, logical gaps. Assign verdict per finding: `validated` | `challenged` | `overturned`

Log `round.peer_review` event.

**9. Phase 4 — Knowledge Transfer**
Read `peer_review_round_{N}.md` verdicts:
- Append all `validated` findings to the `Shared Knowledge` section in conference.md
- If worktree mode: cherry-pick validated code changes to `conference/best` branch (see `references/conference-protocol.md` §5 for conflict resolution rules)
- Update `conference_results.tsv` rows for this round with `peer_review_verdict` values
- Log `round.completed` event with best metric and convergence status

**10. Check convergence**
See `references/conference-protocol.md` §2 for full convergence implementation. Summary:

| Condition | Trigger |
|-----------|---------|
| Metric mode: best metric unchanged for 2 consecutive rounds | CONVERGED |
| Qualitative mode: all outputs rated ≥ 8/10 for 2 consecutive rounds | CONVERGED |
| `max_total_iterations` or `max_rounds` or `time_budget` hit | BUDGET STOP |
| All researchers at stuck Level 2+ simultaneously | STALLED → early synthesis |

- If converged / budget stop / stalled → exit loop → go to SYNTHESIS (Step 11)
- If next round will be the last before `max_rounds` → signal ENDGAME to researchers in Step 6
- Else → increment round counter → return to Step 6

### SYNTHESIS

**11. Spawn Synthesizer (Opus)**
Spawn one Synthesizer agent. Prompt MUST include:
- Paths to ALL `poster_session_round_*.md` and `peer_review_round_*.md` files
- Paths to ALL researcher log files and TSV files
- The conference's Goal and Success Metric/Criteria
- Output paths: `synthesis.md` and `final_report.md`
- Instruction: combine complementary insights from multiple researchers — not just pick the winner. Use `assets/synthesis_template.md` and `assets/report_template.md`.

**12. Worktree cleanup (if worktree mode)**
Offer three options to the user:
1. Merge `conference/best` into original branch
2. Keep worktrees for manual inspection
3. Delete all conference worktrees and branches

**13. Log completion**
Log `conference.completed` event with links to `synthesis.md` and `final_report.md`. Report summary to user: rounds run, total iterations, final best metric/score, synthesis location.

## Agent Roles

Five roles with distinct model tiers. Full prompt contracts in `references/agent-prompts.md`.

| Role | Model | Count | Responsibility |
|------|-------|-------|----------------|
| **Conference Chair** | Sonnet | 1 | Orchestrator — follows this protocol end-to-end |
| **Researcher** | Sonnet | N | Runs autoresearch 5-stage loop within assigned search space partition |
| **Session Chair** | Haiku | 1/round | Lightweight summarizer — produces poster session from all researcher logs |
| **Reviewer** | Opus | 1/round | Adversarial critic — challenges claims, assigns verdicts |
| **Synthesizer** | Opus | 1 | Combines all validated findings into unified synthesis (not just picks a winner) |

**Tier rationale:** Researchers at Sonnet (high iteration volume; Opus cost-prohibitive). Reviewer and Synthesizer at Opus (adversarial reasoning and cross-researcher synthesis require the deepest model). Session Chair at Haiku (pure summarization, no deep reasoning needed).

## Output Files

```
conference.md                    # Config (updated: Shared Knowledge + Conference Log)
conference_results.tsv           # Master conference-level TSV (all rounds, all researchers)
conference_events.jsonl          # Append-only event log

researcher_A_log.md              # Per-researcher detailed iteration logs
researcher_A_results.tsv         # Per-researcher TSV
researcher_B_log.md
researcher_B_results.tsv
...

poster_session_round_1.md        # Session Chair summary (one per round)
peer_review_round_1.md           # Reviewer verdicts (one per round)
...

synthesis.md                     # Final synthesized output (Synthesizer)
final_report.md                  # Executive summary with full conference history
```

See `references/results-logging.md` for TSV column schemas and JSONL event format.

**Visualization:** All conference visualizations (convergence plots, researcher heatmaps, synthesis diagrams) MUST use `scripts/style_presets.py`. Call `rcparams()` before any plotting. See `references/visualization-guide.md` for the 7 mandatory rules: white background, Okabe-Ito palette, DPI 600, no titles, colored legend text.

## Safety & Guardrails

- **`max_total_iterations`** — hard cap on total iterations across all researchers. Prevents runaway execution.
- **`max_rounds`** — hard cap on conference rounds.
- **`time_budget`** — wall-clock limit for the entire conference.
- **`researcher_timeout`** — per-researcher time limit (default: `time_budget / researcher_count`, or set explicitly). If exceeded, the researcher is marked `failed` and the conference proceeds with partial results.
- **Automatic rollback** — inherited from autoresearch. Each researcher reverts failed experiments before the next iteration.
- **Forbidden changes enforcement** — inherited from autoresearch. The `Forbidden Changes` list is passed verbatim to every researcher's prompt.

## Stuck Detection

**Per-researcher (inherited from autoresearch-skill):**
- Level 1 — Plateau (3 consecutive non-improving): switch to a fundamentally different strategy
- Level 2 — Deep Stuck (5 consecutive non-improving): DEEP PIVOT — radical paradigm shift. Adopt strategy from Shared Knowledge that differs most from current approach. If still non-improving after 2 more attempts, signal STALLED_L2 to Conference Chair (researcher continues but may be re-assigned next round).
- Level 3 — Irrecoverable (7 consecutive non-improving): Signal STALLED_L3 — researcher has exhausted its search space. Conference Chair re-spawns with fundamentally different strategy from Shared Knowledge next round. **The conference does NOT stop** — only this researcher pauses.

**Conference-level:**
- If all researchers simultaneously reach stuck Level 2+ in the same round → Conference Chair logs `conference.stalled` event and proceeds directly to SYNTHESIS (Step 11) without waiting for convergence.
- A Level 3 self-terminated researcher is marked `STALLED` in `conference_results.tsv`. On the next round, it is re-spawned with a fundamentally different strategy derived from other researchers' Shared Knowledge.

## Convergence Logic

| Condition | Mode | Result |
|-----------|------|--------|
| Best metric across all researchers unchanged for 2 consecutive rounds | Metric | CONVERGED |
| Reviewer rates all researcher outputs ≥ 8/10 for 2 consecutive rounds | Qualitative | CONVERGED |
| `max_total_iterations` hit | Both | BUDGET STOP |
| `max_rounds` hit | Both | BUDGET STOP |
| `time_budget` hit | Both | BUDGET STOP |
| All researchers stuck Level 2+ simultaneously | Both | STALLED → early synthesis |

Full convergence implementation in `references/conference-protocol.md` §2.

## Qualitative Mode

When `mode: qualitative`, there is no numeric metric. Researchers use **self-assessment** as a proxy:

1. After each iteration, the researcher rates their result 1-10 against the Success Criteria: *"Does this output better satisfy the Success Criteria than the previous best?"*
2. The self-assessed score drives keep/revert decisions within Phase 1 (the inner loop)
3. The Reviewer (Opus) in Phase 3 provides the **authoritative** judgment — it may overturn self-assessments
4. Self-assessment scores are logged to the per-researcher TSV as `metric_value`

This is an acknowledged departure from autoresearch's Principle #2 (Mechanical Verification). The tradeoff enables broader research tasks (literature synthesis, hypothesis generation) at the cost of less reliable inner-loop evaluation. The adversarial Reviewer compensates by providing rigorous external judgment each round. See `references/conference-protocol.md` §6.

## Git Worktree Integration

Worktrees activate **only when `mode == metric` AND researchers make code changes**.

| Mode | Change type | Worktrees? |
|------|------------|-----------|
| Metric | Code changes | Yes — each researcher gets own branch |
| Metric | Prompt/config only | No — file isolation is sufficient |
| Qualitative | Any | No — researchers produce analysis, not code |

**Branch structure:**
```
main (user's current branch)
  ├── conference/researcher-A    ← per-researcher worktree
  ├── conference/researcher-B
  ├── conference/researcher-C
  └── conference/best            ← validated improvements cherry-picked here
```

Per-round lifecycle: create/reset from `conference/best` → research → cherry-pick validated → next round.

Use `/worktree-dashboard` to monitor researcher worktrees in real-time during a conference. The Reviewer agent uses `/compare-worktrees` for cross-worktree static analysis and behavioral comparison. Full lifecycle and conflict resolution in `references/conference-protocol.md` §5.

## Event Hooks

Events are written to `conference_events.jsonl` (append-only JSONL). Format:
```jsonl
{"event": "conference.started", "timestamp": "2026-03-18T10:00:00Z", "payload": {"researchers": 3, "mode": "metric"}}
{"event": "round.completed", "timestamp": "2026-03-18T10:15:00Z", "payload": {"round": 1, "best_metric": 0.82}}
```

| Event | When |
|-------|------|
| `conference.started` | Conference Chair initializes |
| `round.started` | Each round begins |
| `researcher.iteration` | Researcher completes an iteration |
| `round.poster_session` | Poster session complete |
| `round.peer_review` | Peer review complete |
| `round.completed` | Round finishes |
| `researcher.stuck` | Researcher hits stuck Level 2+ |
| `conference.converged` | Convergence detected |
| `conference.completed` | Synthesis done |

External tools can `tail -f conference_events.jsonl` for real-time monitoring. See `references/results-logging.md` §3 for full schema.

## Dependencies

- **Required:** Any LLM CLI with subagent support (Claude Code, Codex CLI, OpenCode, Gemini CLI)
- **Extends:** `autoresearch-skill` — each Researcher runs the autoresearch 5-stage loop. Autoconference adds multi-agent orchestration, peer review, and synthesis on top.
- **Optional:** `/worktree-dashboard` (real-time researcher monitoring), `/compare-worktrees` (cross-worktree review by Reviewer agent)

Python 3.8+ is required only for `scripts/init_conference.py` (scaffolding helper). It is not required to run a conference.

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `autoresearch-skill` | Parent. Each Researcher runs the autoresearch inner loop. Autoconference adds multi-agent orchestration, peer review, and synthesis on top. Single-agent? Use autoresearch. Multi-agent with review? Use autoconference. |
| `worktree-dashboard` | Complementary. Use to monitor all researcher worktrees in real-time during a running conference. |
| `compare-worktrees` | Complementary. Reviewer agent uses this for cross-worktree static analysis and behavioral comparison when verifying claims. |
