# :ship

The `:ship` subcommand takes a completed conference's artifacts and produces a polished, human-readable output document. It runs after synthesis and formats the findings for a specific audience and format.

---

## What It Does

After a conference finishes, you have `synthesis.md` and `final_report.md` — accurate but structured for audit rather than communication. `:ship` transforms these into a format suitable for sharing: a technical report, blog post, paper section, or executive summary.

`:ship` is an 8-phase pipeline that handles:
1. Reading all conference artifacts
2. Deciding on output format
3. Drafting the document
4. Citation verification
5. Reviewer pass (Opus checks for unsupported claims)
6. Presenting for your confirmation before finalizing
7. Writing the final document
8. Producing supplementary materials (charts, appendix)

---

## 8-Phase Pipeline

### Phase 1: Artifact Scan

`:ship` reads:
- `synthesis.md` — the primary source of findings
- `final_report.md` — full conference history
- `conference_results.tsv` — raw data for charts
- All `peer_review_round_N.md` files — to check which claims are validated

### Phase 2: Format Selection

Choose your output format:

| Format | Best for | Length |
|--------|----------|--------|
| **Technical report** | Internal documentation, full-fidelity output | 1,500–3,000 words |
| **Blog post** | Public communication, narrative style | 800–1,200 words |
| **Paper section** | Inserting into an academic paper (Related Work, Results, etc.) | 300–600 words |
| **Executive summary** | Stakeholders who want conclusions without details | 200–400 words |

### Phase 3: Draft

The Synthesizer (Opus) drafts the document in the chosen format. All claims are sourced from `synthesis.md` and cross-checked against `validated` verdicts in the peer review files. Claims marked `challenged` or `overturned` are either excluded or explicitly flagged as inconclusive.

### Phase 4: Citation Verification

For each external claim (citing a paper, dataset, or benchmark), `:ship` verifies:
- The citation appears in the conference artifacts (not hallucinated)
- The claim accurately represents what the cited source says
- The metric values match what appears in `conference_results.tsv`

Unverifiable citations are flagged with `[VERIFY]` markers in the draft for your review.

### Phase 5: Reviewer Pass

A second Opus pass reads the draft as a critical reviewer:
- Are any claims made without supporting evidence from the conference?
- Is the scope of claims appropriate? (e.g., does the draft generalize beyond what the conference actually tested?)
- Are limitations acknowledged?

The reviewer produces a list of suggested revisions. The draft is updated to incorporate them.

### Phase 6: CONFIRM Pause

Before writing the final document, `:ship` pauses and shows you the full draft with a summary of what was changed from the raw synthesis. This is the only mandatory pause in the pipeline.

```
DRAFT READY — Please review before finalizing.

Title: "Sorting Algorithm Performance: Conference Findings"
Format: Technical report (2,100 words)
Key claims included (all validated by Reviewer):
  - Radix sort (LSD, base-256): 59% improvement over baseline
  - Hybrid merge+radix: 63% improvement — best overall
  - Natural merge sort: overturned — cache-thrashing confirmed
  
Changes from raw synthesis:
  - Removed claim about SIMD vectorization (marked 'challenged', insufficient evidence)
  - Added limitation: benchmark tested only uniformly distributed inputs
  - Added 2 [VERIFY] markers for external citations

Proceed to write? (yes / request changes)
```

If you request changes, describe them and `:ship` revises the draft before the next confirmation.

### Phase 7: Write Final Document

After confirmation, `:ship` writes the final document to:
- `shipped/report.md` (or the format-appropriate filename)
- `shipped/report.pdf` (if a PDF converter is available)

### Phase 8: Supplementary Materials

`:ship` produces:
- Convergence chart (from `conference_progress.png` or re-generated at higher resolution)
- Results table (formatted from `conference_results.tsv`)
- Appendix with full methodology (rounds, researchers, evaluator command, peer review summary)

---

## Output Format Options

### Technical Report

Includes: Executive summary, methodology, results table, per-researcher findings, discussion, limitations, conclusion.

Good for: Internal documentation, sharing with collaborators, archival.

### Blog Post

Includes: Hook, problem framing, what we tried, what worked, what surprised us, takeaways.

Good for: Public communication. Omits raw data tables; links to full report instead.

### Paper Section

Structured as a Results or Experiments section ready to paste into a paper draft. Includes standard academic hedging ("we observe," "results suggest") and points to supplementary material for full data.

### Executive Summary

3–5 bullet points with the most important findings, confidence level, and recommended action. No methodology, no data tables, no caveats beyond one line per finding.

---

## Example Workflow

```
ship the results of ./sorting-conference/ as a technical report
```

`:ship` runs the 8-phase pipeline, pauses at Phase 6 for your confirmation, and writes:

```
shipped/
  sorting-conference-report.md
  sorting-conference-appendix.md
  convergence-chart.png
  results-table.csv
```

The report is ready to share, paste into a document, or convert to PDF.

---

## Citation Verification in Practice

For conferences in metric mode, all quantitative claims come from `conference_results.tsv` — they are verifiable by definition. `:ship` cross-checks every number in the draft against the TSV.

For qualitative mode, claims come from `synthesis.md` which is in turn grounded in `peer_review_round_N.md` verdicts. `:ship` traces each claim to its review verdict and marks untraced claims with `[VERIFY]`.

External citations (papers you provided in the `Current Approach` or `Shared Knowledge` sections) are not verified against the internet — only against the conference artifacts. Always review `[VERIFY]` markers before sharing the shipped document publicly.
