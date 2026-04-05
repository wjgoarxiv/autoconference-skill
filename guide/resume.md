# :resume

The `:resume` subcommand recovers an interrupted conference and continues from the last fully completed round. No work is lost, and no completed rounds are re-run.

---

## When Conferences Get Interrupted

Conferences can be interrupted by:

- Network or CLI timeout during a long round
- System shutdown or sleep during an overnight run
- Manual Ctrl+C to pause and inspect progress
- A researcher agent crashing mid-round
- The `time_budget` being hit partway through a round

Because all per-round artifacts are written to disk incrementally, the conference state is always recoverable. The `:resume` command scans the working directory, determines exactly where execution stopped, and picks up from there.

---

## How Checkpoint Recovery Works

On startup, the Conference Chair scans for existing round artifacts in the conference directory:

| Artifact | Indicates |
|----------|-----------|
| `poster_session_round_N.md` | Phase 2 complete for round N |
| `peer_review_round_N.md` | Phase 3 complete for round N |
| Row in `conference_results.tsv` for round N | Phase 4 partially or fully complete |
| `round.completed` event in `conference_events.jsonl` | Round N fully complete (all 4 phases) |

The authoritative source is `conference_events.jsonl`. A `round.completed` event for round N means all 4 phases of round N finished successfully. Everything else is a secondary indicator.

---

## Recovery Point Mapping

| What was found | Where resume starts |
|----------------|---------------------|
| No round artifacts | Round 1, Phase 1 (fresh start — not a resume situation) |
| `round.completed` for round 3, nothing for round 4 | Round 4, Phase 1 |
| `poster_session_round_4.md` exists, no `peer_review_round_4.md` | Round 4, Phase 3 (Phase 2 artifacts kept; peer review re-run) |
| `peer_review_round_4.md` exists, no `round.completed` event for round 4 | Round 4, Phase 4 (knowledge transfer re-run) |
| `round.completed` for round 4, nothing for round 5 | Round 5, Phase 1 |

**Partial round rule:** If a round is incomplete (no `round.completed` event), the Chair discards any incomplete artifacts from that round and re-runs all phases of that round from Phase 1. This ensures every round has a consistent set of artifacts.

**Safe to re-run:** Completed round artifacts are never overwritten. The filenames include the round number (`poster_session_round_N.md`, `peer_review_round_N.md`) which makes them idempotent across restarts.

---

## Shared Knowledge Recovery

When resuming, the Chair re-reads the `Shared Knowledge` section from `conference.md`. This section is updated after each round's Phase 4. All validated findings from completed rounds are already present in the file — no reconstruction needed.

Researchers in the resumed round receive the same `Shared Knowledge` they would have received if the conference had run without interruption.

---

## Stale Checkpoint Warnings

The Chair flags these conditions as warnings (not errors) on resume:

**Time budget exceeded:** If `time_budget` has already elapsed based on the timestamps in `conference_events.jsonl`, the Chair warns:
```
WARNING: time_budget of 4h elapsed (5h23m actual). Proceeding to synthesis from current state.
```
In this case, the Chair skips remaining rounds and goes directly to synthesis.

**Researcher divergence:** If researcher worktrees (for code-change conferences) are out of sync with `conference_results.tsv`, the Chair reports which researcher branches are ahead or behind `conference/best` and asks whether to reset or preserve the divergent state.

**Missing researcher log:** If `researcher_B_log.md` is absent but `conference_results.tsv` has rows for Researcher B, the Chair notes this discrepancy in the resume summary. Researcher B is re-spawned normally for the next round.

---

## Example Usage

To resume a conference that was interrupted overnight:

```
Resume the autoconference in ./my-conference/
```

Claude reads the directory, reports what it found, and continues:

```
Found conference artifacts in ./my-conference/
  Round 1: COMPLETE (poster session + peer review + knowledge transfer)
  Round 2: COMPLETE
  Round 3: PARTIAL — poster session done, peer review not started
  
Resuming from Round 3, Phase 3 (Peer Review).
Shared Knowledge from rounds 1–2 loaded.
```

If you want to resume and also change the researcher count or max rounds:

```
Resume the autoconference in ./my-conference/ with 4 researchers instead of 3
```

The Chair applies the override to the resumed run. The round 1–2 artifacts from 3 researchers are kept; round 3 onward uses 4 researchers (adding Researcher D).

---

## Using the Loop Script for Automatic Resume

The `autoconference-loop.sh` script handles resume automatically. If the loop is interrupted and restarted, it detects the existing conference state and resumes without being told:

```bash
# Start (or restart) a conference — the script resumes if state exists
bash scripts/autoconference-loop.sh ./my-conference/
```

This is the recommended approach for overnight runs. The script handles:
- Detecting whether the conference is in progress, complete, or fresh
- Restarting the CLI tool after crashes
- Exiting cleanly when `synthesis.md` and `final_report.md` appear

---

## What Resume Does NOT Do

- Does not re-run completed rounds (completed means `round.completed` event present)
- Does not merge or delete researcher worktrees automatically
- Does not change the conference goal, metric, or success criteria
- Does not reset researchers who reached `STALLED_L3` before interruption (they are re-spawned with a new strategy in the resumed round, same as normal operation)
