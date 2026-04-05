# :survey

The `:survey` subcommand orchestrates a systematic literature coverage operation across multiple databases and time periods. Each researcher covers a distinct slice of the literature, and citation chains carry findings across researchers between rounds.

---

## What It Does

A `:survey` conference runs in qualitative mode with researchers explicitly partitioned by literature source rather than by strategy. The goal is comprehensive coverage of an existing body of literature, not optimization of a metric.

Use `:survey` when you need:
- A systematic literature review covering multiple databases (arXiv, PubMed, Semantic Scholar, ACM DL, IEEE Xplore)
- Chronological coverage across multiple time periods with a researcher per period
- Methodology-based partitioning (e.g., one researcher covers experimental studies, another covers meta-analyses)
- A synthesis that combines findings across partitions into a unified taxonomy

---

## Multi-Database Coverage Strategy

Researchers are assigned to specific databases. Each researcher searches their assigned database(s) and reports findings in a structured format: paper, year, key claim, method, connection to adjacent work.

Example 3-researcher partition:

| Researcher | Coverage |
|------------|----------|
| A | arXiv (cs.LG, cs.CL) — 2022–2025 |
| B | PubMed + Nature/Science journals — all years |
| C | ACM DL + IEEE Xplore + conference proceedings — 2020–2025 |

Example time-period partition:

| Researcher | Coverage |
|------------|----------|
| A | Foundational work: pre-2018 (seminal papers, original proposals) |
| B | Development period: 2018–2022 (scaling, refinement, benchmarks) |
| C | Recent work: 2023–2025 (state of the art, open problems) |

---

## Partitioning Options

### By Database

Good when: Different communities use different publication venues. Ensures no venue is missed.

```markdown
## Search Space Partitioning
strategy: assigned

## Researcher A Focus
Database: arXiv (cs.LG, stat.ML)
Years: 2020–2025
Query terms: [your topic]
Minimum papers to review: 15

## Researcher B Focus
Database: PubMed, bioRxiv
Years: all
Query terms: [your topic — biology/medicine framing]
Minimum papers to review: 10

## Researcher C Focus
Database: ACM Digital Library, IEEE Xplore, NeurIPS/ICML/ICLR proceedings
Years: 2019–2025
Query terms: [your topic]
Minimum papers to review: 15
```

### By Time Period

Good when: The field has distinct historical phases that should be understood separately before integration.

```markdown
## Researcher A Focus
Period: Pre-2018 (foundational)
Task: Identify the seminal papers that established the core ideas.
Report: Original proposals, key assumptions made, open problems identified at the time.

## Researcher B Focus
Period: 2018–2022 (scaling and benchmarks)
Task: Track how the field developed — what scaling discoveries, what benchmark definitions.
Report: Milestones, benchmark papers, major competing approaches.

## Researcher C Focus
Period: 2023–2025 (current state)
Task: State of the art — what works, what is still unsolved, what the field debates.
Report: SOTA results, open controversies, emerging directions.
```

### By Methodology

Good when: The same topic is studied with fundamentally different methods that need separate treatment before integration.

```markdown
## Researcher A Focus
Methodology: Empirical / experimental studies
Focus on: Papers reporting benchmark results, ablations, controlled experiments.

## Researcher B Focus
Methodology: Theoretical / formal analysis
Focus on: Papers with proofs, complexity bounds, formal convergence guarantees.

## Researcher C Focus
Methodology: Survey and meta-analysis
Focus on: Systematic reviews, meta-analyses, position papers, benchmark papers.
```

---

## Citation Chain Knowledge Transfer

After each round's poster session, the Session Chair extracts:

1. **High-citation papers** — papers that appear in multiple researchers' reference lists (cross-database convergence signal)
2. **Citation bridges** — paper A cited by researcher A that also cites papers in researcher B's coverage (connection across partitions)
3. **Blind spots** — papers expected to appear in a partition based on citation chains but not yet found

These are added to `Shared Knowledge` and given to all researchers for the next round. Researchers use citation bridges to pursue cross-partition connections they would not have found alone.

Example shared knowledge entry:

```
CITATION BRIDGE (Round 1):
  Researcher A found: "Attention Is All You Need" (Vaswani et al., 2017)
  This paper is cited by 3 papers in Researcher C's ACM proceedings coverage.
  Researcher B should check if biomedical NLP work cites this paper chain.
```

---

## Coverage Metrics

After each round, the Session Chair computes:

- **Total papers reviewed** (across all researchers and rounds)
- **Unique papers** (deduplicated by DOI or arXiv ID)
- **Coverage by year** (histogram of paper publication years)
- **Coverage by venue** (which venues have been sampled)
- **Citation overlap** (papers found independently by 2+ researchers — high confidence)

These appear in `poster_session_round_N.md` and help you assess whether the survey is approaching saturation.

A survey is typically saturated when: new rounds produce few papers not already in the corpus, and citation bridges between partitions are mostly already mapped.

---

## Example Survey Configuration

```
Run a survey conference on: retrieval-augmented generation for long-document summarization.
3 researchers, partition by database.
Researcher A: arXiv cs.CL 2022–2025
Researcher B: ACM DL + EMNLP/ACL/NAACL proceedings
Researcher C: cross-domain (non-NLP RAG applications — biomedical, legal, scientific)
2 rounds. Synthesize into a unified taxonomy of retrieval strategies.
```

Expected output: `synthesis.md` containing a taxonomy of retrieval strategies, coverage gaps, and cross-domain connections. `final_report.md` with full citation list and per-researcher coverage summary.

---

## When to Chain with autoconference

A survey naturally feeds into a conference when the literature review reveals competing approaches worth empirically testing:

```
survey → autoconference
```

Example: A `:survey` on sorting algorithm literature identifies 4 competing approaches with theoretical advantages. A `:autoconference` then empirically tests all 4 with researchers assigned to each approach.

See [chains-and-combinations.md](chains-and-combinations.md) for the full `survey → autoconference` chain.
