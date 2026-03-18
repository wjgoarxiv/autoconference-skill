# Conference: Morning vs Evening Exercise Effectiveness

## Goal
Conduct a systematic literature review to determine whether morning or evening exercise is more effective across multiple health and fitness outcomes. Build a comprehensive taxonomy covering 8 outcome categories with sufficient evidence depth (>=2 papers each).

## Mode
metric

## Success Metric
- **Metric:** Taxonomy coverage (8 categories, each needs >=2 papers)
- **Target:** 8/8 categories covered (100%)
- **Direction:** maximize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 3

## Search Space
- **Allowed changes:** Search queries, source databases, taxonomy category refinement, inclusion/exclusion criteria
- **Forbidden changes:** Minimum 2-paper threshold per category, 8-category taxonomy structure, language requirement (English)

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Clinical outcomes focus: weight/fat loss studies, cardiovascular health (blood pressure, heart rate), metabolic health (insulin sensitivity, glucose tolerance). Prioritize RCTs and meta-analyses on these medical outcomes.

### Researcher B Focus
Performance and physiology: muscle performance (strength, hypertrophy, power), hormonal response (cortisol, testosterone, growth hormone), circadian rhythm interactions (chronotype, phase shifts, peripheral clocks).

### Researcher C Focus
Behavioral and practical: sleep quality (onset, duration, disruption risk), adherence and consistency (habit formation, long-term compliance, dropout rates). Also look for cross-cutting themes that span multiple categories.

## Constraints
- **Max total iterations:** 45
- **Time budget:** 2h
- **Researcher timeout:** 40m
- Publication types: RCTs, meta-analyses, systematic reviews, prospective cohort studies
- Language: English only
- Sources: PubMed, arxiv, Google Scholar, Semantic Scholar
- Minimum 2 papers per taxonomy category to count as "covered"

## Taxonomy Categories
1. **Weight/Fat Loss** -- Body composition, fat oxidation, weight reduction outcomes
2. **Muscle Performance** -- Strength, hypertrophy, power, maximal exercise capacity
3. **Cardiovascular Health** -- Blood pressure, heart rate, vascular function
4. **Hormonal Response** -- Cortisol, testosterone, growth hormone, insulin
5. **Sleep Quality** -- Sleep onset, duration, architecture, disturbance
6. **Metabolic Health** -- Insulin sensitivity, glucose tolerance, metabolic syndrome markers
7. **Circadian Rhythm** -- Chronotype interactions, peripheral clock entrainment, phase shifts
8. **Adherence & Consistency** -- Habit formation, long-term compliance, dropout rates

## Current Approach
Starting from 3 known meta-analyses as seed references:
1. Bruggisser et al. (2023) "Best Time of Day for Strength and Endurance Training" -- Sports Medicine Open
2. Sevilla-Lorente et al. (2023) "Effects of Time-of-Day on Blood Pressure" -- JSAMS
3. Chtourou & Souissi (2012) "Effect of Training at a Specific Time of Day" -- JSCR

Initial taxonomy coverage:
- **Muscle Performance:** Bruggisser 2023, Chtourou 2012 (2 papers -- covered)
- **Cardiovascular Health:** Sevilla-Lorente 2023 (1 paper -- needs more)
- **Weight/Fat Loss:** 0 papers -- gap
- **Hormonal Response:** 0 papers -- gap
- **Sleep Quality:** 0 papers -- gap
- **Metabolic Health:** 0 papers -- gap
- **Circadian Rhythm:** 0 papers -- gap
- **Adherence & Consistency:** 0 papers -- gap

## Shared Knowledge
<!-- Auto-populated after each round with validated findings -->

### Round 1 Validated Findings

1. **Evening exercise superior for blood pressure reduction** in hypertensive patients, mediated by sympathetic nervous system modulation and improved baroreflex sensitivity (Brito 2019, Brito 2024, Sevilla-Lorente 2023). *Caveat: both Brito studies from same lab.*
2. **Evening/afternoon exercise superior for glycemic control in T2DM.** Afternoon HIIT lowered overnight and next-day glycemia; morning HIIT can paradoxically raise blood glucose acutely via cortisol-driven hepatic glucose output (Savikj 2019, Mancilla 2021).
3. **Evening T:C ratio is more favorable for anabolism.** Cortisol exercise response is attenuated in evening; baseline GH twofold higher in evening (Kanaley 2001, Hayes 2010). *Caveat: acute T:C ratio may not predict chronic hypertrophy outcomes.*
4. **Morning exercise reliably phase-advances the circadian clock.** Effect modulated by chronotype — late chronotypes advance from both AM and PM exercise (Thomas 2020, Youngstedt 2019). Strong RCT evidence (N=52).
5. **Short-term hypertrophy shows no timing difference; long-term may favor evening.** <3 months: equivalent (Sedliak 2009). >3 months: evening groups gained more muscle mass (Kuusmaa 2016). *Caveat: Kuusmaa used combined strength + endurance protocol.*
6. **Evening exercise does NOT disrupt sleep** in healthy young/middle-aged adults. Two independent meta-analyses confirm (Stutz 2019, Frimpong 2021). Only consistent effect: slight REM reduction (~2.3%).
7. **Consistent exercise timing is more important than specific time** for habit formation and long-term adherence. Consistent exercisers perform ~23% more weekly exercise minutes (Schumacher 2020, 2022, 2023; Thomas 2022). *Caveat: all observational — causation not established.*

## Context & References
- Exercise timing research has accelerated since 2019 with wearable-derived data
- Key confound: most studies do not control for chronotype
- "Temporal congruence effect" -- training at a consistent time matters more than which time
- Sex-specific differences emerging as major finding (Arciero 2022, Scientific Reports 2025)

---

## Conference Log
<!-- Auto-maintained by Conference Chair. Do not edit manually. -->
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
| 1 | A | 8/8 | Evening superior for CV + metabolic; morning for fat oxidation (fasted); sex-specific effects | completed |
| 1 | B | 8/8 | Evening T:C ratio favorable; morning phase-advances clock; hypertrophy timing-neutral short-term | completed |
| 1 | C | 8/8 | Evening exercise safe for sleep; consistent timing > specific time for adherence | completed |
