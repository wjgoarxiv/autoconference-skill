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
1. **Decision rules for confusing pairs (Researcher A, validated):** Explicit decision rules distinguishing Billing/Account ("money-related = Billing, profile/settings = Account"), Bug Report/Technical ("software malfunction = Bug Report, hardware/connectivity = Technical"), and Returns/General Inquiry ("wants to send item back = Returns, seeking information = General Inquiry") yield the single largest improvement: 68% to 90% (+22%).
2. **Structured JSON output (Researcher C, validated):** JSON format with confidence field `{"category": "...", "confidence": "high|medium|low"}` yields 68% to 86% (+18%). Forces disciplined classification without overthinking.
3. **5 targeted few-shot examples (Researcher B, validated):** One example per confusing category pair is the sweet spot. Yields 68% to 84% (+16%). More than 5 examples shows diminishing returns (challenged — needs more testing).
4. **ANTI-PATTERN: No explicit reasoning (Researcher C, validated):** Chain-of-thought and multi-pass verify both regress to 74%. ALL forms of explicit step-by-step reasoning are HARMFUL for gpt-4o-mini classification. Do NOT use CoT, multi-pass, or self-verification steps.
5. **Negative findings (all validated):** Example ordering has no effect. System/user message split has no effect. Output format specification alone has no effect. Narrow edge case documentation does not generalize.

### Round 2 Validated Findings
6. **Triple combination is optimal (all researchers, validated):** Decision rules + structured JSON output + 5 targeted few-shot examples = 94% (47/50). Order-independent — all 3 researchers arrived at the same result independently regardless of combination order.
7. **Diminishing returns from >5 examples confirmed (Researcher B, validated):** Tested with 6 examples (Round 1) and 7 examples (Round 2). 5 is the sweet spot. Round 1 reviewer challenge addressed.
8. **No explicit reasoning anti-pattern extends broadly (Researcher C, validated):** Confidence routing and elimination-based classification are also ineffective. The anti-pattern covers: CoT, multi-pass, confidence routing, elimination-based, and negative instruction lists.
9. **94% is locally optimal (challenged -> validated in Round 3):** 9 independent micro-optimization attempts across all 3 researchers failed to improve beyond 94%. The remaining 3 errors (IDs 39, 44, 49) are genuinely ambiguous. However, fundamentally different framings were not explored — radical departures could potentially break through.

### Round 3 Validated Findings (ENDGAME)
10. **94% is the confirmed ceiling (all researchers, validated):** 24 total failed attempts across Rounds 2-3 (15 in Round 3 alone). The remaining 3 errors (IDs 39, 44, 49) are genuinely ambiguous category boundary cases that prompt engineering cannot resolve.
11. **Ablation confirms triple combination necessity (Researcher B, validated):** Removing examples from the triple combination regresses from 94% to 90%. Each component serves a distinct purpose.
12. **Section ordering irrelevant (Researcher A, validated):** Prompt section order has no effect on accuracy.
13. **Confidence field optional (Researcher C, validated):** Include for downstream utility, not for accuracy.

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
| 1 | A | 90.0% | Decision rules for confusing category pairs (+22% from baseline) | completed |
| 1 | B | 84.0% | 5 targeted few-shot examples, one per confusing pair (+16%) | completed |
| 1 | C | 86.0% | Structured JSON output with confidence field (+18%); CoT is harmful (-6%) | completed |
| 2 | A | 94.0% | Triple combination (rules+JSON+examples) = 94%, target exceeded | completed |
| 2 | B | 94.0% | Confirmed >5 examples has no effect; triple combination order-independent | completed |
| 2 | C | 94.0% | Confidence routing and elimination classification both ineffective | completed |
| 3 | A | 94.0% | 5 EXPLOIT attempts all at 94%; section reordering no effect | converged |
| 3 | B | 94.0% | Ablation: removing examples regresses to 90%; all components necessary | converged |
| 3 | C | 94.0% | Two-field JSON, table format, XML tags, decisiveness all no effect | converged |
