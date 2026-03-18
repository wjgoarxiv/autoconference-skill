# HANDOFF: autoconference-skill

**Date:** 2026-03-19
**Branch:** `main` at `96502a4`
**Repo:** https://github.com/wjgoarxiv/autoconference-skill
**Status:** Pushed to GitHub, fully functional

---

## What Was Built (This Session)

### 1. Full Skill Implementation
Built the entire `autoconference-skill` from scratch — a Claude Code skill that orchestrates multiple autoresearch agents in structured conference rounds (Symposium + Debate model).

**Key files:**
- `SKILL.md` (348 lines) — core skill, conference orchestration loop
- `references/agent-prompts.md` — prompt contracts for 5 agent roles
- `references/conference-protocol.md` — round structure, convergence, failure modes
- `references/core-principles.md` — 7 inherited + 3 new principles
- `references/results-logging.md` — TSV + JSONL logging protocols
- `assets/conference_template.md` — user-facing conference.md template
- `assets/synthesis_template.md`, `assets/report_template.md` — output templates
- `templates/` — 4 shipped templates (quick, prompt-opt, code-perf, research-synthesis)
- `scripts/init_conference.py` — scaffolding tool (5/5 tests passing)
- `evals/evals.json` — 6 trigger accuracy scenarios

### 2. Repo Decoration
- `cover.png` — 2560x1024, amber/gold + teal gradient, JetBrains Mono, 400 DPI
- `generate_cover.py` — PIL/NumPy cover generator
- `README.md` — decorated with badges, features, copy-paste install, usage examples
- `README-Ko-KR.md` — full Korean translation

### 3. sII Hydrate Example (v3, crystal-preserving)
`examples/sii-hydrate-generation/` — real-execution autoconference example:

**Pipeline:**
- `generate_hydrate.py` — GenIce2 crystal → slab cut → z-exclusive water → PBC
- `evaluate.py` — 6-sub-metric composite scorer (structural 20%, density 15%, geometric 15%, PBC 10%, slab_exclusion 20%, crystal_integrity 20%)
- `run_iterations.py` — 33 iterations across 3 researchers, 3 rounds

**Two critical constraints enforced:**
1. Water exclusion: zero water molecules in slab z-range (Z-axis sandwich)
2. Crystal preservation: hydrate coords identical to GenIce2 output (max deviation 0.000098 nm)

**Visualization:**
- `visualize.py` — 4 individual plots (600 DPI, Okabe-Ito palette, scientific-visualization rcparams)
- `render_snapshots_3dmol.py` — py3Dmol orthographic snapshots via Selenium headless Chrome (1600x1600 viewport)
- All plots embedded in example README + main README via markdown tables

**Conference artifacts:** All standard files (conference.md, TSVs, researcher logs, poster sessions, peer reviews, synthesis, final_report, events JSONL, 33 iteration .gro files + score JSONs)

**Results:** Composite converged from ~25-65 (Round 1: crystal deformation + water overlap) to 99.9 (Round 3: both constraints satisfied).

---

## What Worked Well

- **Team mode (4 parallel executors)** built the initial skill repo in parallel — each chunk (foundation, protocol, SKILL.md, tooling) ran simultaneously
- **Deep-interview → autopilot pipeline** produced clear specs before execution, avoiding rework
- **Real GenIce2 execution** gave authentic iteration data — not hand-crafted
- **py3Dmol + Selenium** produced proper molecular renderings after matplotlib 3D scatter was insufficient
- **Scientific-visualization rcparams** elevated plot quality to publication standard

## What Didn't Work / Required Iteration

1. **v1 missed water exclusion** — water was placed everywhere including in the hydrate slab. Fixed in v2.
2. **v2 missed crystal preservation** — coordinates were scaled to fit 3.6 nm box, deforming the crystal. Fixed in v3 by using crystal-native box dimensions (3.424 nm).
3. **py3Dmol `png()` doesn't work headlessly** — falls back to HTML + Selenium screenshot
4. **Playwright browsers not installed** — used Selenium with existing Chrome instead
5. **`.gitignore` excluded conference artifacts** — needed `git add -f` for example files
6. **Snapshot whitespace** — py3Dmol renders molecule centered with large margins; required post-processing crop with PIL

## What Remains / Next Steps

1. **More examples** — user mentioned wanting to explore more examples beyond sII hydrate (the `examples/` directory currently only has the one example after squash merge removed the old placeholder examples)
2. **Push to `17_autoconference-skill` copy** — the copy at `../17_autoconference-skill` is outdated (pre-example)
3. **Push to `064_autoconference-skill` skill copy** — the copy at `~/.claude/skills/064_autoconference-skill` is outdated
4. **WIP commits on main** — there are 8 WIP commits on main before the squash merge; could be cleaned up with interactive rebase if desired
5. **GitHub social preview** — could set cover.png as the repo's social preview image via GitHub settings

## Key Technical Details for Next Agent

- **GenIce2 CS2 unit cell:** 1.7121 nm (cubic, Fd3m). Rep 2 = 3.4242 nm.
- **Box dimensions:** 3.4242 x 3.4242 x 5.0 nm (x,y = crystal-native, z = slab + water)
- **Slab z-range:** 0.788 to 4.212 nm (centered in 5.0 nm box)
- **py3Dmol rendering:** Requires Selenium headless Chrome with `--enable-webgl --use-gl=angle --enable-unsafe-swiftshader` flags
- **Scientific-visualization rcparams:** at `/Users/woojin/.claude/skills/045_scientific-visualization/scripts/style_presets.py`
- **Working directory:** `/Users/woojin/Desktop/02_Areas/01_Codes_automation/15_autoconference-skill`
