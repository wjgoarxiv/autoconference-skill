# Getting Started

Get your first conference running in under 60 seconds.

---

## Prerequisites

- A supported LLM CLI with subagent support (Claude Code is the primary target)
- Python 3.8+ (only needed for the `init_conference.py` scaffolding helper — not to run conferences)
- Git (only needed for code-change conferences that use worktree isolation)

The skill itself requires no external packages. Python stdlib only.

---

## Install

### Option A: Copy-paste (Claude Code)

Paste this block directly into Claude Code. It clones, installs, and verifies in one shot.

```
I want to install the autoconference-skill. Do these steps:
1. git clone https://github.com/wjgoarxiv/autoconference-skill.git /tmp/autoconference-skill
2. mkdir -p ~/.claude/skills/autoconference-skill && cp -r /tmp/autoconference-skill/SKILL.md /tmp/autoconference-skill/scripts /tmp/autoconference-skill/assets /tmp/autoconference-skill/references ~/.claude/skills/autoconference-skill/
3. Test: python ~/.claude/skills/autoconference-skill/scripts/init_conference.py --goal "test" --metric "score" --direction minimize --researchers 2 --output /tmp/test-conference && echo "OK: autoconference-skill installed"
4. Say "autoconference-skill installed successfully"
```

### Option B: Symlink (manual)

```bash
git clone https://github.com/wjgoarxiv/autoconference-skill.git
cd autoconference-skill
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/autoconference-skill
```

### Option C: Other tools

| Tool | Skills Path | Install Command |
|------|-------------|-----------------|
| Claude Code | `~/.claude/skills/autoconference-skill/` | See Option A above |
| Codex CLI | `~/.codex/skills/autoconference-skill/` | `mkdir -p ~/.codex/skills && ln -s "$(pwd)" ~/.codex/skills/autoconference-skill` |
| OpenCode | `~/.config/opencode/skills/autoconference-skill/` | `mkdir -p ~/.config/opencode/skills && ln -s "$(pwd)" ~/.config/opencode/skills/autoconference-skill` |
| Gemini CLI | `~/.gemini/skills/autoconference-skill/` | `mkdir -p ~/.gemini/skills && ln -s "$(pwd)" ~/.gemini/skills/autoconference-skill` |

---

## Your First Conference in 3 Steps

### Step 1: Scaffold a conference directory

```bash
python scripts/init_conference.py \
  --goal "Optimize sort performance on integer arrays" \
  --metric "wall_time_ms" \
  --direction minimize \
  --target "< 100" \
  --researchers 3 \
  --output ./my-first-conference/
```

This creates `my-first-conference/conference.md` with the full template pre-filled.

### Step 2: Edit `conference.md`

Open the generated file and fill in three sections:

- **Current Approach** — describe what you start with (e.g., "stdlib `sorted()` with default comparator")
- **Search Space** — what researchers are allowed and forbidden to change
- **Researcher Focus Areas** (if using assigned strategy) — what each researcher should specialize in

Everything else is already set by the scaffold. You can leave defaults for your first run.

### Step 3: Tell Claude to run it

```
Run the autoconference on my-first-conference/conference.md
```

Claude loads `SKILL.md`, reads your conference config, asks 4 pre-flight questions, and orchestrates all rounds through to final synthesis. You don't need to do anything else unless you chose interactive mode.

---

## Domain Cheat Sheet

These domains work well with autoconference. Use them to decide if your problem is a good fit.

| Domain | Mode | What to measure |
|--------|------|-----------------|
| **Code optimization** (sorting, inference, compilation) | metric | wall-clock time, throughput, peak memory |
| **Prompt engineering** (accuracy, faithfulness, format) | metric | LLM judge score 1-10, exact-match rate, BLEU |
| **Literature synthesis** (survey, meta-analysis) | qualitative | Coverage, novelty, connection density |
| **Algorithm design** (scheduling, routing, packing) | metric | Solution quality score, constraint violations |
| **Data pipeline optimization** (throughput, latency) | metric | Records/second, p95 latency ms |
| **ML hyperparameter tuning** | metric | Validation accuracy, F1, loss |
| **Writing quality improvement** | qualitative | Clarity, structure, evidence quality |
| **API design evaluation** | qualitative | Usability, consistency, completeness |
| **Security hardening** | metric | Vulnerability scan score, test pass rate |
| **Configuration optimization** | metric | Benchmark score, resource utilization |
| **Scientific simulation** (molecular dynamics, hydrates) | metric | Composite score, constraint satisfaction |
| **Skill / prompt elaboration** (improving LLM skills) | qualitative | Completeness, coverage of edge cases |

### Quick decision rule

- Does success produce a **number** you can compute automatically? → use `metric` mode
- Is success about **reasoning quality or document completeness**? → use `qualitative` mode
- Is your search space **small enough for one agent**? → use `autoresearch-skill` instead

---

## What Happens Next

After you run `autoconference`, you'll find these files in your conference directory:

```
conference.md                  ← updated with round log and shared knowledge
conference_results.tsv         ← machine-readable results (all rounds, all researchers)
conference_progress.png        ← live convergence plot (updated each round)
researcher_A_log.md            ← per-researcher detailed iteration log
poster_session_round_1.md      ← Session Chair summary after round 1
peer_review_round_1.md         ← Reviewer verdicts after round 1
synthesis.md                   ← final synthesized output
final_report.md                ← executive summary
```

Read `synthesis.md` first. It combines the best findings from all researchers. Then read `final_report.md` for the full audit trail.

---

## Next Steps

- [autoconference.md](autoconference.md) — full reference for the conference loop
- [plan.md](plan.md) — interactive wizard for complex setups
- [chains-and-combinations.md](chains-and-combinations.md) — how to chain commands
- [examples-by-domain.md](examples-by-domain.md) — concrete configurations by domain
