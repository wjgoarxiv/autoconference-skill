<p align="center"><img src="./cover.png" width="100%" /></p>

<h1 align="center">autoconference-skill</h1>
<p align="center">
  <em>Spawn a conference of autonomous researchers that compete, collaborate, and synthesize breakthroughs.</em>
</p>
<p align="center">
  <a href="#commands">Commands</a> · <a href="#when-to-use">When to Use</a> · <a href="#quick-start">Quick Start</a> · <a href="#how-it-works">How It Works</a> · <a href="#templates">Templates</a> · <a href="#guide">Guide</a> · <a href="./README-Ko-KR.md">한국어</a>
</p>
<p align="center">
  <img src="https://img.shields.io/github/stars/wjgoarxiv/autoconference-skill?style=social" />
  <img src="https://img.shields.io/badge/license-MIT-blue" />
  <img src="https://img.shields.io/badge/python-3.8+-green" />
  <img src="https://img.shields.io/badge/version-2.0.0-orange" />
  <img src="https://img.shields.io/badge/skill-Claude%20Code%20%7C%20Codex%20%7C%20OpenCode%20%7C%20Gemini-blueviolet" />
</p>

---

> [!NOTE]
> A Claude Code skill that orchestrates N parallel autoresearch agents in structured conference rounds -- with adversarial peer review and cross-researcher synthesis. Write a `conference.md` defining your research goal, and the conference handles hypothesis generation, experimentation, evaluation, and multi-agent iteration. Built on [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill). Works with Claude Code, Codex CLI, and Gemini CLI.

### Example: sII Hydrate + Water .gro Generation

| Round 1 (Naive) | Final (Converged) |
|:---:|:---:|
| ![Round 1](./examples/sii-hydrate-generation/snapshot_round1.png) | ![Final](./examples/sii-hydrate-generation/snapshot_final.png) |
| Composite: 34.5 — water in slab | Composite: 99.9 — clean separation |

| Convergence | Sub-metrics |
|:---:|:---:|
| ![Convergence](./examples/sii-hydrate-generation/plot_composite_convergence.png) | ![Sub-metrics](./examples/sii-hydrate-generation/plot_submetric_breakdown.png) |

> 33 iterations across 3 researchers and 3 rounds. The conference learns to preserve crystal structure and exclude water from the hydrate slab. [See full example →](./examples/sii-hydrate-generation/)

## Commands

autoconference v2.0 provides 7 commands through a subcommand architecture:

| Command | Description | Use Case |
|---------|-------------|----------|
| `/autoconference` | Core conference loop | Run N researchers through structured rounds with peer review |
| `/autoconference:plan` | 8-step setup wizard | Interactively create a `conference.md` with dry-run evaluator gate |
| `/autoconference:resume` | Checkpoint recovery | Resume an interrupted conference from last completed phase |
| `/autoconference:analyze` | Post-conference analysis | Extract insights, failure modes, and transferable learnings |
| `/autoconference:debate` | Adversarial debate | 2-researcher pro/con format with Opus judge |
| `/autoconference:survey` | Literature survey | Multi-database systematic review with citation chains |
| `/autoconference:ship` | Ship results | 8-phase pipeline to format results for publication |

**Command chaining:**
```
plan ──> autoconference ──> ship              (standard pipeline)
plan ──> autoconference ──> analyze ──> ship  (with post-analysis)
debate ──> autoconference                     (debate-informed experiment)
survey ──> autoconference                     (literature-guided experiment)
resume ──> autoconference                     (continuation)
```

## Features

- **Multi-Agent Orchestration** -- N researchers explore different parts of the search space in parallel, then share findings after each round.
- **Adversarial Peer Review** -- Opus-powered Reviewer agent challenges claims each round, catching overfitting and measurement noise before results propagate.
- **Synthesis Over Selection** -- Final output combines complementary insights from multiple researchers, not just picks the winner.
- **Dual Mode** -- Metric mode for numeric optimization, Qualitative mode for literature review and hypothesis generation.
- **7 Subcommands** -- Plan, run, resume, analyze, debate, survey, and ship — chainable into full research pipelines.
- **Guard Parameters** -- Conference-level safety constraints that override metric improvements when violated.
- **Automatic Convergence** -- Detects plateau, budget exhaustion, or stall and triggers final synthesis automatically.
- **Crash Recovery** -- 5-type recovery matrix for interrupted conferences (mid-research, mid-poster, mid-review, mid-transfer, pre-synthesis).
- **Full Audit Trail** -- Per-researcher logs, poster sessions, peer reviews, conference-level TSV, and JSONL event stream.
- **Built on autoresearch-skill** -- Each researcher runs the proven 5-stage experiment-evaluate-iterate loop.
- **Safety Built In** -- Max iterations, time budgets, researcher timeouts, forbidden-change boundaries, and automatic rollback.

## When to Use

Autoconference builds on [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill)'s single-agent loop by adding parallel exploration, adversarial review, and cross-researcher synthesis. Use it when one agent exploring sequentially isn't enough -- either because the search space is too wide, or because self-evaluation alone can't be trusted.

### autoconference vs alternatives

|  | autoresearch-skill | Agent harness modes (team, /batch, ouroboros, etc.) | autoconference |
|:---|:---|:---|:---|
| **Agents** | 1 | N, each on a different subtask | N, all on the same problem with different strategies |
| **Exploration** | Sequential strategy switching | Independent subtask decomposition | Search space partitioning + knowledge transfer between rounds |
| **Validation** | Mechanical evaluator or agent self-judgment | Build/test pass | Opus adversarial reviewer (catches overfitting, noise, invalid claims) |
| **Result integration** | Single best result | Per-subtask results merged | Synthesis -- combines complementary insights, not just picks a winner |
| **Round structure** | None (continuous iteration) | None (one-shot dispatch) | Poster session → peer review → knowledge transfer per round |

### Pick autoconference when

- The **search space is wide enough to partition** -- N researchers exploring different regions in parallel cover more ground than one agent switching strategies sequentially
- **Self-evaluation has blind spots** -- the adversarial Reviewer (Opus) catches overfitting, measurement noise, and Goodhart's Law effects that a single agent's evaluator misses
- You need **synthesis, not selection** -- the final output should combine complementary findings from multiple approaches, not just take the best score
- The research is **qualitative** (literature synthesis, hypothesis generation) and benefits from multiple perspectives converging on a shared taxonomy

### Use autoresearch-skill instead when

- The search space is **small enough for one agent** to cover within the iteration budget
- You have a **mechanical evaluator** and trust its keep/revert decisions without external review
- **Token cost matters** -- autoconference runs N researchers + reviewer + synthesizer per round, roughly N+2x the cost of a single autoresearch loop

## Quick Start

### 1. Copy-Paste Install

> [!TIP]
> Paste the block below directly into Claude Code. It clones the repo, installs the skill, and verifies the setup in one shot.

```
I want to install the autoconference-skill. Do these steps:
1. git clone https://github.com/wjgoarxiv/autoconference-skill.git /tmp/autoconference-skill
2. mkdir -p ~/.claude/skills/autoconference-skill && cp -r /tmp/autoconference-skill/SKILL.md /tmp/autoconference-skill/scripts /tmp/autoconference-skill/assets /tmp/autoconference-skill/references ~/.claude/skills/autoconference-skill/
3. Test: python ~/.claude/skills/autoconference-skill/scripts/init_conference.py --goal "test" --metric "score" --direction minimize --researchers 2 --output /tmp/test-conference && echo "OK: autoconference-skill installed"
4. Say "autoconference-skill installed successfully"
```

### 2. Manual Install

```bash
git clone https://github.com/wjgoarxiv/autoconference-skill.git
cd autoconference-skill

# Symlink into your skills directory
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/autoconference-skill
```

### 3. Other Tools

| Tool | Install Command |
|------|----------------|
| Claude Code | Paste the copy-paste block above, or use the manual install |
| Codex CLI | Copy `SKILL.md` into your Codex instructions directory |
| Gemini CLI | Copy `SKILL.md` into your Gemini context directory |

### Other Platforms

| Platform | Skills Path | Install Command |
|----------|-------------|-----------------|
| **Claude Code** | `~/.claude/skills/autoconference-skill/` | See above |
| **Codex CLI** | `~/.codex/skills/autoconference-skill/` | `mkdir -p ~/.codex/skills && ln -s "$(pwd)" ~/.codex/skills/autoconference-skill` |
| **OpenCode** | `~/.config/opencode/skills/autoconference-skill/` | `mkdir -p ~/.config/opencode/skills && ln -s "$(pwd)" ~/.config/opencode/skills/autoconference-skill` |
| **Gemini CLI** | `~/.gemini/skills/autoconference-skill/` | `mkdir -p ~/.gemini/skills && ln -s "$(pwd)" ~/.gemini/skills/autoconference-skill` |

## Usage

### Prompt Optimization Tournament

Three researchers compete on prompt accuracy — each specializing in instruction phrasing, few-shot selection, and chain-of-thought formatting.

```
Run an autoconference using templates/prompt-optimization.md.
Goal: maximize accuracy on my classification benchmark.
3 researchers, 3 rounds.
```

### Code Performance Competition

Algorithmic, data-structure, and low-level researchers independently optimize the same codebase, then cross-pollinate validated wins each round.

```
Run an autoconference using templates/code-performance.md.
Metric: wall-clock time on my benchmark suite.
Direction: minimize. Target: < 200ms.
```

### Literature Synthesis Conference

Qualitative mode. Three researchers survey the same topic from foundational, recent, and cross-domain angles, then synthesize a unified taxonomy.

```
Run an autoconference in qualitative mode.
Goal: survey LLM agent papers from 2022-2025.
3 researchers, 2 rounds. Synthesize findings into a taxonomy.
```

### Scaffold a New Conference

```bash
python scripts/init_conference.py \
  --goal "Optimize inference latency" \
  --metric "p95_latency_ms" \
  --direction minimize \
  --target "< 50" \
  --researchers 3 \
  --strategy assigned \
  --output ./latency-conference/
```

Then edit the generated `conference.md` to fill in your `Current Approach`, `Search Space`, and researcher focus areas. When ready:

```
Run the autoconference on my conference.md
```

Claude loads `SKILL.md`, reads `conference.md`, and orchestrates the full conference -- all rounds, peer review, and final synthesis.

## How It Works

```
+----------------------------------------------------------+
|                     CONFERENCE ROUND                     |
|                                                          |
|  Phase 1: INDEPENDENT RESEARCH (parallel)               |
|  +----------+  +----------+  +----------+               |
|  |Researcher|  |Researcher|  |Researcher|  Each runs N  |
|  |    A     |  |    B     |  |    C     |  autoresearch |
|  | (iter x N)|  | (iter x N)|  | (iter x N)|  iterations |
|  +----+-----+  +----+-----+  +----+-----+               |
|       |              |             |                     |
|  Phase 2: POSTER SESSION                                 |
|  +----------------------------------------------+       |
|  | Session Chair collects all logs,             |       |
|  | surfaces key findings & deltas               |       |
|  +----------------------+-----------------------+       |
|                         |                               |
|  Phase 3: PEER REVIEW (adversarial)                     |
|  +----------------------------------------------+       |
|  | Reviewer agent challenges claims:            |       |
|  | - "Did metric actually improve?"             |       |
|  | - "Is this overfitting?"                     |       |
|  | - "Could this be measurement noise?"         |       |
|  +----------------------+-----------------------+       |
|                         |                               |
|  Phase 4: KNOWLEDGE TRANSFER                            |
|  +----------------------------------------------+       |
|  | Validated findings shared back to            |       |
|  | all researchers for next round               |       |
|  +----------------------------------------------+       |
|                                                          |
+----------------------------------------------------------+
          |
          v  Convergence check -> next round or final synthesis
```

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
| **Conference Chair** | Sonnet | 1 | Orchestrator -- manages rounds, spawns researchers, detects convergence, triggers synthesis |
| **Researcher** | Sonnet | N | Runs the autoresearch 5-stage loop within assigned search space |
| **Session Chair** | Haiku | 1 | Lightweight summarizer -- collects logs and produces poster session summary after each round |
| **Reviewer** | Opus | 1 | Adversarial critic -- challenges claims, checks for overfitting/noise, assigns verdicts |
| **Synthesizer** | Opus | 1 | Runs once at end -- combines complementary insights from all researchers |

## Templates

Ready-to-use `conference.md` configs for common tasks:

| Template | Mode | Use Case |
|----------|------|----------|
| `templates/quick-conference.md` | metric | 2 researchers, 2 rounds -- test if your problem benefits from the conference format |
| `templates/prompt-optimization.md` | metric | Optimize LLM prompt accuracy with 3 specialized researchers |
| `templates/code-performance.md` | metric | Optimize code speed with algorithmic, data-structure, and low-level researchers |
| `templates/research-synthesis.md` | qualitative | Literature exploration across foundational, recent, and cross-domain angles |
| `templates/debate-mode.md` | qualitative | 2-researcher adversarial debate with structured rounds and Opus judge |
| `templates/survey-mode.md` | qualitative | Multi-database literature survey with citation chain tracking |

## Configuration Options

| Field | Default | Description |
|-------|---------|-------------|
| `mode` | `metric` | `metric` or `qualitative` |
| `count` | -- | Number of researcher agents |
| `iterations_per_round` | 5 | Autoresearch iterations each researcher runs per round |
| `max_rounds` | 4 | Maximum conference rounds before forced synthesis |
| `max_total_iterations` | -- | Hard cap across all researchers and rounds |
| `time_budget` | -- | Wall-clock limit for the entire conference |
| `researcher_timeout` | -- | Per-researcher timeout per round |
| `strategy` | `free` | `assigned` (focus areas) or `free` (open exploration) |
| `guard` | -- | Safety constraint enforced on ALL researchers (violations revert regardless of metric) |
| `noise_runs` | 1 | Repeated evaluations to average for noise reduction |
| `min_consensus_delta` | 0 | Minimum average improvement across kept researchers to advance |

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

## Overnight Runs

To run a conference overnight, use the universal loop script:

```bash
# Option A: Foreground (simplest)
bash scripts/autoconference-loop.sh ./my-conference/

# Option B: Background with nohup (no tmux needed)
nohup bash scripts/autoconference-loop.sh ./my-conference/ > conference.log 2>&1 &

# Option C: Background with tmux (best experience)
tmux new-session -d -s conference 'bash scripts/autoconference-loop.sh ./my-conference/'

# Check progress anytime
bash scripts/check_conference.sh ./my-conference/
```

The script auto-detects your CLI tool, handles round restarts, and checks for conference completion. Works with Claude Code, Codex CLI, OpenCode, and Gemini CLI.

## Relationship to autoresearch-skill

Each researcher in a conference runs the **autoresearch loop** -- the same autonomous experiment-evaluate-iterate cycle from [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill). Autoconference adds three layers on top:

1. **Multi-agent orchestration** -- N researchers explore different parts of the search space in parallel
2. **Adversarial peer review** -- A Reviewer agent challenges findings each round (catches what self-evaluation misses)
3. **Synthesis** -- A Synthesizer combines complementary insights rather than just picking the best result

Use autoresearch-skill for a single focused research loop. Use autoconference when your search space is large enough to partition, when diversity of approach matters, or when you want external validation of results.

## Guide

Comprehensive documentation is available in the `guide/` directory:

| Guide | Topic |
|-------|-------|
| [Getting Started](guide/getting-started.md) | 60-second quickstart + domain cheat sheet |
| [Core Conference](guide/autoconference.md) | 4-phase round structure, convergence, overnight runs |
| [Plan](guide/plan.md) | 8-step setup wizard |
| [Resume](guide/resume.md) | Checkpoint recovery |
| [Analyze](guide/analyze.md) | Post-conference insight extraction |
| [Debate](guide/debate.md) | Adversarial 2-researcher format |
| [Survey](guide/survey.md) | Multi-database literature survey |
| [Ship](guide/ship.md) | Conference results to publication |
| [Chains](guide/chains-and-combinations.md) | Command chaining patterns |
| [Advanced](guide/advanced-patterns.md) | Guards, noise, worktrees, CI/CD |
| [Troubleshooting](guide/troubleshooting.md) | Common failure modes and fixes |

See also: [COMPARISON.md](./COMPARISON.md) for autoconference vs alternatives.

## Cross-Platform Compatibility

| Platform | Status | Install |
|----------|--------|---------|
| Claude Code | Ready | Plugin install or manual symlink |
| Codex CLI | Ready | See `.codex/INSTALL.md` |
| OpenCode | Ready | See `.opencode/INSTALL.md` |
| Gemini CLI | Ready | Uses `gemini-extension.json` auto-discovery |

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.8+ (stdlib only — for `scripts/init_conference.py` only) |
| **LLM CLI** | Any CLI with subagent support (Claude Code, Codex CLI, OpenCode, Gemini CLI) |
| **autoresearch-skill** | Referenced by each researcher agent's prompt |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

MIT -- see [LICENSE](./LICENSE) for details.
