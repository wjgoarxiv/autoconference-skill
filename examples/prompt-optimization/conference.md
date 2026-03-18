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
