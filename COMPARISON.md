# autoconference vs Alternatives

When to use autoconference, autoresearch-skill, team mode, or manual multi-agent orchestration.

---

## autoconference vs autoresearch-skill

autoresearch-skill runs a single autonomous agent through a sequential experiment-evaluate-iterate loop. autoconference layers multi-agent orchestration, adversarial review, and synthesis on top of that same loop.

| Feature | autoresearch-skill | autoconference |
|---------|-------------------|----------------|
| Researchers | 1 | N (2–5) |
| Exploration | Sequential strategy switching | Parallel search space partitioning |
| Peer review | Self-evaluation only | Adversarial Opus reviewer per round |
| Knowledge transfer | N/A (single agent) | Cross-pollination after each round |
| Noise handling | Single trajectory | Ensemble — outliers get challenged |
| Synthesis | Best result wins | Complementary insights combined |
| Best for | Focused, bounded search spaces | Broad or multi-modal search spaces |
| Cost | Lower (1 agent) | Higher (N researchers + reviewer + synthesizer) |
| Setup | Single `research.md` | `conference.md` with researcher partitions |

**Rule of thumb:** if one agent can cover the search space within the iteration budget, use autoresearch-skill. Add autoconference when the space is wide enough to partition, when self-evaluation has blind spots, or when you want external validation.

---

## autoconference vs Team Mode

Both use multiple agents, but for fundamentally different purposes.

| Dimension | Team Mode | autoconference |
|-----------|-----------|----------------|
| Task structure | Different sub-tasks (division of labor) | Same problem, different approaches (diversity) |
| Agent independence | Agents work on separate concerns | Agents work on the same goal |
| Integration | Per-subtask results merged | Synthesis — insights combined across agents |
| Review | Build/test pass or manual check | Adversarial Opus reviewer each round |
| Round structure | None (one-shot dispatch) | Poster session → peer review → knowledge transfer |
| When findings conflict | Each agent owns its subtask | Reviewer adjudicates; knowledge transfer resolves |

**Use team mode when** the work decomposes cleanly into independent subtasks (frontend + backend, analysis + writeup, data cleaning + modeling). Use autoconference when multiple agents need to tackle the **same problem** and you want their findings to inform each other.

---

## autoconference vs Manual Multi-Agent

Manual multi-agent means spawning agents yourself, reading their outputs, and deciding what to do next.

| Dimension | Manual Orchestration | autoconference |
|-----------|---------------------|----------------|
| Orchestration | User decides each step | Conference Chair manages rounds automatically |
| Reviewer | User judges quality | Opus adversarial reviewer (consistent, documented) |
| Knowledge transfer | User manually copies findings | Automatic shared knowledge section each round |
| Convergence | User decides when to stop | Automatic plateau and budget detection |
| Audit trail | Whatever the user saves | Per-researcher logs, TSVs, poster sessions, reviews |
| Reproducibility | Hard — depends on user choices | High — full JSONL event stream + structured logs |
| Flexibility | Maximum | Within the conference format |

**Use manual orchestration** when your problem is unusual enough that no structured protocol fits. Use autoconference when the conference protocol (partition → research → review → transfer → synthesize) matches your problem structure, and you want the overhead managed automatically.

---

## Decision Guide

```
Is your search space small enough for one agent to cover?
  YES → autoresearch-skill

Does your work decompose into independent sub-tasks?
  YES → team mode

Do you need multiple agents exploring the SAME problem
with adversarial review and cross-agent synthesis?
  YES → autoconference

Do you need a custom protocol that doesn't fit any of the above?
  YES → manual multi-agent
```

### More detailed heuristics

**Use autoresearch-skill when:**
- You have a clear single metric and mechanical evaluator
- The search space has < ~20 plausible approaches
- Token cost is a constraint
- You trust self-evaluation for your domain

**Use autoconference when:**
- The search space is wide enough that parallel partitioning makes sense (N researchers explore N different regions simultaneously)
- Self-evaluation has known blind spots (Goodhart's Law, overfitting, measurement noise)
- You need synthesis — the final answer should combine complementary insights, not just pick the best score
- You're doing qualitative research (literature surveys, debate, hypothesis generation) that benefits from multiple perspectives converging on a shared taxonomy

**Use team mode when:**
- Tasks are clearly separable with minimal dependencies
- Agents produce artifacts that combine cleanly (files, modules, sections)
- You don't need agents to learn from each other

**Use manual multi-agent when:**
- The problem requires custom orchestration logic
- You need dynamic team composition (spawn agents based on prior results)
- The conference format doesn't match your workflow

---

## Cost Model

autoconference is inherently more expensive than a single-agent approach. Rough cost multipliers relative to one autoresearch run:

| Setup | Relative Cost |
|-------|--------------|
| autoresearch-skill (1 agent) | 1× |
| autoconference (2 researchers, 2 rounds) | ~5–6× |
| autoconference (3 researchers, 3 rounds) | ~11–12× |
| autoconference (5 researchers, 4 rounds) | ~22–25× |

The reviewer (Opus) and synthesizer (Opus) add a fixed overhead per round regardless of researcher count. For qualitative conferences, actual cost depends heavily on context length accumulated in Shared Knowledge.
