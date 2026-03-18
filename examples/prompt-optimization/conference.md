# Conference: Customer Support Ticket Classifier Prompt

## Goal
Improve the classification accuracy of a customer support ticket classifier. The classifier assigns incoming tickets to one of 8 categories: Billing, Technical, Account, Shipping, Returns, Feature Request, Bug Report, General Inquiry.

## Mode
metric

## Success Metric
- **Metric:** Accuracy on 50-case test set (test_cases.json)
- **Target:** > 90%
- **Direction:** maximize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 3

## Search Space
- **Allowed changes:** System prompt text, few-shot examples, output format instructions, chain-of-thought instructions, category descriptions, classification rules, edge case handling
- **Forbidden changes:** Test set (test_cases.json), model (gpt-4o-mini), temperature (0), category names

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Instruction engineering: category definitions, explicit decision rules for confusing category pairs (Billing vs Account, Bug Report vs Technical), output format specification, boundary case documentation.

### Researcher B Focus
Few-shot example selection: targeted examples for each confusing category pair, edge case coverage, example ordering and diversity, example count trade-offs against prompt length.

### Researcher C Focus
Structural techniques: chain-of-thought reasoning, confidence scoring, multi-pass classification (classify then verify), prompt structure and section ordering, system vs user message split.

## Constraints
- **Max total iterations:** 45
- **Time budget:** 1h
- **Researcher timeout:** 20m
- System prompt token count must stay under 2000 tokens
- Response time must remain under 3 seconds per classification
- Must use gpt-4o-mini (no model upgrades allowed)

## Current Approach
Basic zero-shot prompt with category list. No examples, no structured output format.

```
You are a customer support ticket classifier. Classify the following ticket
into one of these categories: Billing, Technical, Account, Shipping, Returns,
Feature Request, Bug Report, General Inquiry.

Ticket: {ticket_text}

Category:
```

Baseline accuracy: 68% (34/50).

Common failure modes:
- Confuses "Billing" with "Account" (10 misclassifications combined)
- Misses "Bug Report" when the user describes symptoms without technical terms (4)
- Over-classifies ambiguous tickets as "General Inquiry" (2)

## Shared Knowledge
<!-- Auto-populated after each round with validated findings -->

### Round 1 Validated Findings
1. **Decision rules for confusing pairs** (Researcher A, validated): Explicit rules for Billing/Account, Bug Report/Technical, and Returns/General Inquiry boundaries are the highest-impact single technique. Accuracy: 68% -> 90%.
2. **5 targeted few-shot examples** (Researcher B, validated): One example per confusing category pair is optimal; more examples add noise, fewer leave gaps. Accuracy: 68% -> 84%.
3. **Structured JSON output** (Researcher C, validated): Requiring JSON format with confidence field improves classification discipline. Accuracy: 68% -> 86%.
4. **WARNING — Chain-of-thought is harmful** (Researcher C, validated): CoT causes overthinking and regression on this classification task (68% -> 74%). AVOID.
5. **Diminishing returns boundary** (Researcher A, validated): Remaining errors after decision rules (IDs 35, 39, 43, 44, 49) are genuinely ambiguous. Micro-rules risk overfitting.
6. **Few-shot plateau at 84%** (Researcher B, validated): Examples alone cannot exceed 84%; must be combined with other techniques.
7. **Combination hypothesis** (cross-researcher): Decision rules + targeted examples + structured output have NOT yet been combined. Primary opportunity for Round 2.

### Round 2 Validated Findings
8. **The combination formula** (all researchers, validated): Decision rules + structured JSON output = 94% accuracy. Cross-validated independently by all 3 researchers.
9. **Irreducible error floor** (all researchers, validated): IDs 39, 44, 49 are at genuine category boundaries and cannot be resolved by prompt engineering alone.
10. **Examples + rules synergy** (Researcher B, validated): Examples reinforce decision rules but are redundant with structured output alone.
11. **No CoT confirmed** (Researcher C, validated): Even constrained CoT provides no benefit when decision rules exist.
12. **Prompt minimization** (Researcher C, validated): Decision rules subsume category definitions; prompt can be minimized to ~1200 tokens while maintaining 94%.
13. **Hierarchical classification is a dead end** (Researcher C, validated): Super-category routing doesn't help when errors cross super-category boundaries.

## Context & References
- test_cases.json contains 50 labeled tickets with ground truth categories
- Error analysis shows Billing/Account confusion is the biggest source of errors
- Prior work suggests few-shot examples and explicit category definitions help most
- Chain-of-thought may help or hurt depending on task complexity
- Evaluation script: `evaluate.py`

---

## Conference Log
<!-- Auto-maintained by Conference Chair. Do not edit manually. -->
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
| 1 | A | 90.0% | Decision rules for confusing category pairs (+22%) | completed |
| 1 | B | 84.0% | 5 targeted few-shot examples (+16%) | completed |
| 1 | C | 86.0% | Structured JSON output (+18%); CoT harmful | completed |
| 2 | A | 94.0% | Decision rules + structured output = 94% | completed |
| 2 | B | 94.0% | Examples + rules synergy; 3 examples suffice | completed |
| 2 | C | 94.0% | Structured output + rules confirmed; prompt minimized | completed |
