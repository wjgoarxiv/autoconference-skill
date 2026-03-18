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

### Round 1 Validated Findings

1. **Weight/Fat Loss (VALIDATED):** Morning pre-breakfast exercise maximizes 24h fat oxidation (717 vs 432 kcal/d, Iwayama 2015). Sex-specific effects: women lose more abdominal fat with AM (-10% vs -3%, Arciero 2022); men oxidize more fat with PM (+6% vs +1%). Willis 2020 RCT (n=88) shows comparable total weight loss AM vs PM.

2. **Cardiovascular Health (VALIDATED):** Acute BP effects are similar AM/PM (Brito 2023 meta-analysis). Chronic evening training reduces BP more effectively in treated hypertension via reduced sympathetic modulation and improved baroreflex sensitivity (Melo de Souza 2024, Fairbrother 2014).

3. **Metabolic Health (VALIDATED):** Population-dependent direction. Evening/afternoon exercise improves glycemic control in T2D — morning HIIT actually increases glucose acutely (Savikj 2019, Diabetologia). This is explained by inverted circadian insulin sensitivity in T2D. In metabolic syndrome (non-T2D), morning training reduces insulin resistance more (Morales-Palomo 2024).

4. **Muscle Performance (VALIDATED, deepened):** PM advantage for hypertrophy over 24 weeks (Kuusmaa 2016). PM performance advantage 3-21% for power/anaerobic capacity (Chtourou 2012). Strength gains (1RM) comparable between AM and PM.

5. **Hormonal Response (VALIDATED):** PM hormonal environment favors hypertrophy — lower cortisol:testosterone ratio. AM has higher testosterone but also higher cortisol, which counteracts anabolic benefit (Hayes 2010, Sedliak 2007, Ahtiainen 2015, Kraemer 2004).

6. **Circadian Rhythm (CHALLENGED — caveat noted):** Morning exercise phase-advances human circadian clock by ~0.6h (Youngstedt 2019). Effect is chronotype-dependent: late chronotypes benefit from both AM and PM exercise; early chronotypes may be harmed by PM exercise (Thomas 2020, JCI Insight). Animal data (Wolff 2012) shows larger peripheral clock shifts (up to 8h) but translatability is limited.

7. **Sleep Quality (VALIDATED):** AM exercise shortens sleep onset latency and improves subjective quality (Stutz 2023 systematic review). PM exercise does NOT disrupt sleep if ended >1h before bed (Frimpong 2021 meta-analysis) and may increase slow-wave sleep (Myllymaki 2011). Clinically actionable: the >1h buffer is the key threshold.

8. **Adherence & Consistency (CHALLENGED — evidence level caveat):** Consistent timing appears more important than specific time (Schumacher 2023, feasibility study). AM adherence slightly higher (94% vs 87%, Brooker 2023). However, most evidence is from small feasibility studies or observational data (Willis 2020 NHANES). Large-scale RCTs specifically comparing AM vs PM long-term adherence are lacking.

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
| 1 | A | 5/8 | Added Weight/Fat Loss, Cardiovascular, Metabolic Health (12 papers) | completed |
| 1 | B | 4/8 | Added Hormonal Response, Circadian Rhythm; deepened Muscle Performance (11 papers) | completed |
| 1 | C | 4/8 | Added Sleep Quality, Adherence & Consistency (11 papers) | completed |
| 1 | ALL | 8/8 | TARGET REACHED — all 8 categories covered with >=2 papers each | CONVERGED |
