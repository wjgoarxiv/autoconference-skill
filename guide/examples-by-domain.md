# Examples by Domain

Concrete, ready-to-adapt conference configurations across domains. Each entry includes the recommended mode, researcher count, partitioning strategy, and expected behavior.

---

## Code Performance Optimization

### Sorting Algorithm Competition

**Goal:** Minimize wall-clock time on a benchmark suite of 10,000–1,000,000 integer arrays.

**Mode:** metric  
**Researchers:** 3  
**Partitioning:** assigned  
**Evaluator:** `python benchmark.py --sort {algorithm}`

| Researcher | Focus |
|------------|-------|
| A | Algorithmic approach: algorithm family choice (merge, radix, hybrid) |
| B | Data structure optimizations: memory layout, cache line alignment, branch prediction |
| C (Devil's Advocate) | Challenge assumptions: try the simplest possible baseline, verify benchmarking conditions are fair |

**Search Space:**
- Allowed: any code in `sort.py`, sorting algorithm choice, memory allocation strategy
- Forbidden: benchmark script, test data generation, evaluation harness

**Expected:** 3 rounds typical. Round 1 often sees a large jump (algorithm switch). Rounds 2–3 produce micro-optimizations (cache tuning, threshold tuning). Convergence usually by round 3.

**Template:** `templates/code-performance.md`

---

### Inference Latency Optimization

**Goal:** Minimize p95 latency (ms) for a model serving endpoint under realistic load.

**Mode:** metric  
**Researchers:** 3  
**Partitioning:** assigned

| Researcher | Focus |
|------------|-------|
| A | Model-level: quantization, pruning, layer fusion |
| B | Serving-level: batching strategy, request queuing, async I/O |
| C | Infrastructure-level: hardware selection, memory bandwidth, kernel optimization |

**Evaluator:** `python load_test.py --duration 60 --rps 100 --p95`

**Expected:** 4 rounds for a complex system. High variance between researchers early (different levels of the stack find different improvements). Shared Knowledge transfer is high-value here — infrastructure wins from Researcher C often amplify model wins from Researcher A when combined.

---

## Prompt Engineering

### Classification Accuracy Improvement

**Goal:** Maximize accuracy on a binary classification benchmark using prompt changes only.

**Mode:** metric  
**Researchers:** 3  
**Partitioning:** assigned  
**Evaluator:** `python evaluate.py --prompt {prompt_file} --benchmark classification_test.jsonl`

| Researcher | Focus |
|------------|-------|
| A | Instruction phrasing: word choice, framing, explicit vs implicit instructions |
| B | Few-shot selection: which examples to include, example ordering, format of examples |
| C | Chain-of-thought: whether to include reasoning steps, format of reasoning, placement |

**Forbidden:** evaluation script, test set, model selection

**Template:** `templates/prompt-optimization.md`

**Expected:** 3 rounds typical. Shared Knowledge often reveals that instruction phrasing (A) and few-shot format (B) interact — a combined approach that neither researcher found alone emerges in round 2.

---

### Prompt Faithfulness (RAG System)

**Goal:** Maximize faithfulness score — ensure model responses stay grounded in retrieved context.

**Mode:** metric  
**Researchers:** 2  
**Partitioning:** free (both researchers explore the full prompt space)

**Evaluator:** `python faithfulness_eval.py --responses responses.jsonl --contexts contexts.jsonl`

**Note:** Use `free` partitioning when the search space is small enough that 2 researchers exploring independently is better than artificial partition.

**Expected:** 2 rounds sufficient for prompt-only optimization. If score plateaus, consider switching to a conference with `retrieval_strategy` as an allowed change.

---

## Literature Review

### Systematic Survey

**Goal:** Produce a comprehensive taxonomy of LLM agent architectures from 2022–2025.

**Mode:** qualitative  
**Researchers:** 3  
**Partitioning:** assigned (by database)

| Researcher | Coverage |
|------------|----------|
| A | arXiv cs.AI, cs.CL, cs.LG — 2022–2025 |
| B | ACM DL, NeurIPS/ICML/ICLR/EMNLP proceedings |
| C | Cross-domain: robotics, game-playing, scientific discovery applications |

**Success Criteria:**
```
A comprehensive taxonomy covering:
- At least 15 distinct architectural patterns
- Clear identification of 3+ open research gaps
- Cross-domain connections to non-LLM agent systems
- Actionable recommendations for practitioners
```

**Expected:** 2 rounds. Round 1: each researcher surveys their partition independently. Round 2: citation bridges identified in Round 1 are followed; researchers integrate cross-partition connections. Synthesis produces unified taxonomy.

**Template:** `templates/research-synthesis.md`

---

### Meta-Analysis (Quantitative)

**Goal:** Synthesize reported benchmark results across papers to establish a reliable performance picture for [method X].

**Mode:** qualitative (the synthesis requires judgment; raw numbers vary too much across evaluation setups to treat as a single metric)  
**Researchers:** 3  
**Partitioning:** by time period

| Researcher | Period |
|------------|--------|
| A | Pre-2021 (foundational results, original benchmarks) |
| B | 2021–2023 (scaling results, standardized benchmarks) |
| C | 2024–2025 (current SOTA, recent challenges to earlier results) |

**Expected:** 2 rounds. The value is in Researcher C identifying where earlier claimed results were not replicated — this is the most common finding in meta-analyses and requires explicit tracking.

---

## Scientific Simulation

### Molecular Dynamics: sII Hydrate Generation

**Goal:** Generate a clean sII hydrate + water `.gro` file with high composite score (crystal structure preserved, water excluded from hydrate slab).

**Mode:** metric  
**Researchers:** 3  
**Partitioning:** assigned

| Researcher | Focus |
|------------|-------|
| A | Water molecule placement and exclusion algorithm |
| B | Crystal structure parameter tuning (lattice constants, cage occupancy) |
| C | Post-processing and validation pipeline (composite score components) |

**Evaluator:** `python score_hydrate.py --structure output.gro`  
**Target:** composite_score > 95.0

**Reference:** See `examples/sii-hydrate-generation/` for a full completed conference (33 iterations, 3 researchers, 3 rounds, final score 99.9).

**Expected:** 3 rounds. This type of problem often shows the pattern: Round 1 establishes which component of the composite score is hardest to satisfy. Rounds 2–3 focus on the bottleneck component. The conference is particularly valuable here because the composite score has multiple sub-metrics that interact in non-obvious ways.

---

## Skill Elaboration

### Improving an LLM Skill Document

**Goal:** Improve the completeness and coverage of a skill document (e.g., an LLM prompt file, a SKILL.md, a system prompt).

**Mode:** qualitative  
**Researchers:** 3  
**Partitioning:** assigned

| Researcher | Focus |
|------------|-------|
| A | Coverage: what edge cases or scenarios are missing from the current skill? |
| B | Clarity: are the instructions unambiguous? Where might an LLM misinterpret? |
| C | Robustness: what adversarial inputs or unexpected situations does the skill not handle? |

**Success Criteria:**
```
An improved skill document that:
- Covers all common use cases explicitly
- Has unambiguous instructions (no two reasonable interpretations)
- Handles at least 5 edge cases not in the original
- Preserves the concise style of the original
```

**Expected:** 2–3 rounds. Qualitative mode; Reviewer (Opus) is the authoritative judge. This is a meta-use of the conference format — using autoconference to improve the skills that run inside autoconference.

**Template:** `templates/research-synthesis.md` (adapt for qualitative mode)

---

## Quick Configuration Reference

| Domain | Mode | Researchers | Rounds | Partitioning |
|--------|------|-------------|--------|--------------|
| Code optimization | metric | 3 | 3–4 | assigned (algorithmic / data-structure / low-level) |
| Inference latency | metric | 3 | 4 | assigned (model / serving / infra) |
| Prompt engineering | metric | 3 | 3 | assigned (instruction / few-shot / chain-of-thought) |
| Prompt faithfulness | metric | 2 | 2 | free |
| Literature survey | qualitative | 3 | 2 | assigned (by database or time period) |
| Meta-analysis | qualitative | 3 | 2 | assigned (by time period) |
| Scientific simulation | metric | 3 | 3 | assigned (by composite score component) |
| Skill elaboration | qualitative | 3 | 2–3 | assigned (coverage / clarity / robustness) |
