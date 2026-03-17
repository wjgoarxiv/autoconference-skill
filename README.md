<h1 align="center">autoconference-skill</h1>
<p align="center">
  <em>Spawn a conference of autonomous researchers that compete, collaborate, and synthesize breakthroughs.</em>
</p>
<p align="center">
  <a href="#quick-start">Quick Start</a> · <a href="#how-it-works">How It Works</a> · <a href="#templates">Templates</a> · <a href="#relationship-to-autoresearch-skill">autoresearch-skill</a>
</p>
<p align="center">
  <img src="https://img.shields.io/github/stars/wjgoarxiv/autoconference-skill?style=social" />
  <img src="https://img.shields.io/badge/license-MIT-blue" />
  <img src="https://img.shields.io/badge/python-3.8+-green" />
  <img src="https://img.shields.io/badge/skill-Claude%20Code-blueviolet" />
</p>

---

## TL;DR

Write a `conference.md` describing your research goal, and autoconference spawns N parallel autoresearch agents that compete in structured rounds. After each round, a reviewer agent adversarially challenges the findings, and validated insights are shared across all researchers. At the end, a synthesizer produces a unified result that combines complementary discoveries — not just picks a winner.

## How It Works

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

## Quick Start

### 1. Install

```bash
# Clone the repo
git clone https://github.com/wjgoarxiv/autoconference-skill.git
cd autoconference-skill

# Symlink into your skills directory
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/autoconference-skill
```

### 2. Scaffold a conference project

```bash
python scripts/init_conference.py \
  --goal "Optimize inference latency" \
  --metric "p95_latency_ms" \
  --direction minimize \
  --target "< 50" \
  --researchers 3 \
  --strategy assigned \
  --output ./my-conference/
```

For qualitative mode (literature review, hypothesis generation):

```bash
python scripts/init_conference.py \
  --goal "Survey LLM agent papers" \
  --mode qualitative \
  --criteria "Comprehensive taxonomy with 15+ papers and 3 research gaps" \
  --researchers 3 \
  --output ./lit-review/
```

### 3. Edit `conference.md`

Fill in the `Current Approach`, `Search Space`, and researcher focus areas. The scaffold pre-populates everything else.

### 4. Run the conference

Tell Claude:
```
Run the autoconference on my conference.md
```

Claude loads `SKILL.md`, reads your `conference.md`, and orchestrates the full conference — including all rounds, peer review, and final synthesis.

## The `conference.md` Format

| Section | Purpose |
|---------|---------|
| `Goal` | What the conference should achieve |
| `Mode` | `metric` (numeric optimization) or `qualitative` (reasoning quality) |
| `Success Metric` | Metric name, target, direction (metric mode only) |
| `Success Criteria` | Natural language description of "good" (qualitative mode only) |
| `Researchers` | Count, iterations per round, max rounds |
| `Search Space` | What researchers can and cannot modify |
| `Search Space Partitioning` | `assigned` (each researcher has a focus) or `free` (overlap allowed) |
| `Constraints` | Max iterations, time budget, researcher timeout |
| `Current Approach` | Baseline description |
| `Shared Knowledge` | Auto-populated after each round with validated findings |
| `Conference Log` | Auto-maintained round-by-round history |

See `assets/conference_template.md` for the full template.

## Agent Roles

| Role | Model | Count | Responsibility |
|------|-------|-------|----------------|
| **Conference Chair** | Sonnet | 1 | Orchestrator — manages rounds, spawns researchers, detects convergence, triggers synthesis |
| **Researcher** | Sonnet | N | Runs the autoresearch 5-stage loop within assigned search space |
| **Session Chair** | Haiku | 1 | Lightweight summarizer — collects logs and produces poster session summary after each round |
| **Reviewer** | Opus | 1 | Adversarial critic — challenges claims, checks for overfitting/noise, assigns verdicts |
| **Synthesizer** | Opus | 1 | Runs once at end — combines complementary insights from all researchers |

## Output Files

| File | Description |
|------|-------------|
| `conference.md` | User config (updated with log entries each round) |
| `conference_results.tsv` | Master conference-level TSV with all iterations and peer review verdicts |
| `researcher_A_log.md` | Detailed per-researcher iteration log |
| `researcher_A_results.tsv` | Per-researcher TSV (same format as autoresearch) |
| `poster_session_round_N.md` | Session Chair summary for each round |
| `peer_review_round_N.md` | Reviewer verdicts for each round |
| `synthesis.md` | Final synthesized output from Synthesizer |
| `final_report.md` | Executive summary with full conference history |

## Templates

Ready-to-use `conference.md` configs for common tasks:

| Template | Mode | Use Case |
|----------|------|----------|
| `templates/quick-conference.md` | metric | 2 researchers, 2 rounds — test if your problem benefits from the conference format |
| `templates/prompt-optimization.md` | metric | Optimize LLM prompt accuracy with 3 specialized researchers |
| `templates/code-performance.md` | metric | Optimize code speed with algorithmic, data-structure, and low-level researchers |
| `templates/research-synthesis.md` | qualitative | Literature exploration across foundational, recent, and cross-domain angles |

## Configuration Options

| Field | Default | Description |
|-------|---------|-------------|
| `mode` | `metric` | `metric` or `qualitative` |
| `count` | — | Number of researcher agents |
| `iterations_per_round` | 5 | Autoresearch iterations each researcher runs per round |
| `max_rounds` | 4 | Maximum conference rounds before forced synthesis |
| `max_total_iterations` | — | Hard cap across all researchers and rounds |
| `time_budget` | — | Wall-clock limit for the entire conference |
| `researcher_timeout` | — | Per-researcher timeout per round |
| `strategy` | `free` | `assigned` (focus areas) or `free` (open exploration) |

## Relationship to autoresearch-skill

Each researcher in a conference runs the **autoresearch loop** — the same autonomous experiment-evaluate-iterate cycle from [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill). Autoconference adds three layers on top:

1. **Multi-agent orchestration** — N researchers explore different parts of the search space in parallel
2. **Adversarial peer review** — A Reviewer agent challenges findings each round (catches what self-evaluation misses)
3. **Synthesis** — A Synthesizer combines complementary insights rather than just picking the best result

Use autoresearch-skill for a single focused research loop. Use autoconference when your search space is large enough to partition, when diversity of approach matters, or when you want external validation of results.

## Cross-Platform Compatibility

| Platform | Status |
|----------|--------|
| Claude Code | Ready — uses `Agent` tool for parallel researcher spawning |
| Gemini CLI | Future — subagent API needs research |
| Codex CLI | Future — subagent API needs research |

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.8+ (stdlib only) |
| **Claude Code** | With `Agent` tool support for parallel execution |
| **autoresearch-skill** | Referenced by each researcher agent's prompt |

## License

MIT — see [LICENSE](./LICENSE) for details.
