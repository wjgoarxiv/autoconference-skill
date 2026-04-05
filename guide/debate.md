# :debate

The `:debate` subcommand runs a structured adversarial debate between two positions on a research question. Unlike a conference (which seeks convergence), a debate is designed to surface the strongest possible arguments on both sides before convergence is allowed.

---

## When to Use Debate vs Conference

| Situation | Use |
|-----------|-----|
| You want to explore a large search space and synthesize what works | `:autoconference` |
| You have a specific binary question or contentious finding and want the strongest arguments on each side | `:debate` |
| The Reviewer overturned a finding you expected to hold — you want to understand why | `:debate` |
| Two researchers in a conference converged on opposite conclusions | `:debate` |
| You want to stress-test a specific hypothesis before building on it | `:debate` |

A debate is not about finding the truth — it is about surfacing the strongest version of each position. Use it when you need to understand the space of disagreement, not just the current best answer.

---

## Pro/Con Structured Format

Each debate has two sides:

- **Pro** — argues in favor of the proposition
- **Con** — argues against it

Both sides are assigned to researcher agents who must argue their assigned position, regardless of personal preference. This is the anti-convergence enforcement: the agents are not allowed to switch sides or reach a premature consensus.

Example proposition: "Radix sort is the superior general-purpose sorting algorithm for integer arrays in production systems."

- Pro researcher: defends radix sort across all reasonable inputs and contexts
- Con researcher: attacks radix sort's assumptions (memory overhead, non-comparative limitations, cache behavior, parallelism)

---

## Round Structure

A debate runs 4 phases per round, similar to a conference but with adversarial framing:

### Phase 1: Opening Statements

Both researchers independently produce their strongest opening argument for their assigned position. No cross-pollination — they write independently.

### Phase 2: Challenge

Each researcher reads the other's opening statement and produces a targeted challenge:
- "Your claim assumes X, but X fails when Y"
- "Your evidence is drawn from Z benchmark, which does not represent production conditions"
- "The cost you attribute to Pro is actually attributable to implementation, not the algorithm"

### Phase 3: Rebuttal

Each researcher responds to the challenges they received. They may concede on narrow points but must maintain their core position unless the evidence clearly forces abandonment.

### Phase 4: Verdict

The Reviewer (Opus) reads all arguments and challenges and produces a structured verdict:

```
VERDICT on: "Radix sort is the superior general-purpose sorting algorithm"

STRONGEST PRO ARGUMENT: Cache-aligned LSD radix sort achieves O(n) on uniformly
  distributed integer data; in the benchmark suite, outperforms comparison-based
  sorts by 40–60% on arrays > 10,000 elements.

STRONGEST CON ARGUMENT: "General-purpose" is the problem. Radix sort's performance
  degrades on non-uniform distributions (e.g., sorted or nearly-sorted input) and
  requires O(n + k) space, which is unacceptable in memory-constrained environments.
  The benchmark did not test these conditions.

VERDICT: The proposition is TRUE for the specific benchmark conditions (uniformly
  distributed integers, array size 10k–1M, memory-unconstrained). The proposition is
  FALSE as a general claim. Recommend restricting the claim to its valid domain.

CONFIDENCE: High (both sides produced strong, well-evidenced arguments)
```

---

## Anti-Convergence Enforcement

The Reviewer explicitly checks for and penalizes premature convergence:

- If both researchers reach the same conclusion before the rebuttal phase, the Reviewer flags this as "insufficient adversarial exploration" and asks the Con researcher to produce 3 additional counter-arguments before issuing a verdict.
- If a researcher abandons their position in the Challenge phase without sufficient evidence, the Reviewer notes this as "concession without evidence" and asks them to defend the strongest possible version of their original position.

The goal is not to force false disagreement — it is to ensure each position gets its strongest possible representation before the Reviewer adjudicates.

---

## Example Topics

Well-suited for debate:

- "Few-shot prompting outperforms fine-tuning for domain adaptation when labeled data is < 1000 examples"
- "Graph neural networks are the right architecture for molecular property prediction"
- "Quantization to 4-bit always degrades model quality beyond acceptable thresholds for production use"
- "The retrieval step in RAG systems introduces more latency than it saves in accuracy"
- "Structured output prompting produces more reliable JSON than function calling for nested schemas"
- Any finding from a completed conference that the Reviewer marked `challenged` or `overturned`

Poor fit for debate:

- Questions with obvious answers where one side has no serious argument
- Questions where the answer depends entirely on unmeasured empirical data (run a conference instead)
- Questions about preferences or values (no fact-based resolution possible)

---

## Relationship to Conference

Debate is often used as a post-conference step to investigate contentious findings:

```
autoconference → analyze → debate (on Tier 3 challenged findings)
```

Example: a conference on prompt engineering found that chain-of-thought prompting improved accuracy, but the Reviewer marked it `challenged` due to potential evaluation contamination. Running a debate on "chain-of-thought improves accuracy on clean holdout sets" forces both sides to produce evidence before accepting or rejecting the finding.

See [chains-and-combinations.md](chains-and-combinations.md) for the full `analyze → debate` chain.
