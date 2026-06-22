# Conference: Sorting Algorithm Optimization

## Goal
Sort 1M integers in under 0.5 seconds.

## Mode
metric

## Success Metric
- **Metric:** wall_time_seconds
- **Target:** < 0.5
- **Direction:** minimize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 2

## Search Space
- **Allowed changes:** Sorting implementation strategy and pure-Python algorithm choices.
- **Forbidden changes:** Benchmark inputs, correctness tests, and metric collection.

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Algorithmic alternatives such as merge sort, radix sort, and hybrids.

### Researcher B Focus
Data-structure choices such as counting maps and sparse-distribution handling.

### Researcher C Focus
Low-level and built-in implementations such as `sorted()` and `list.sort()`.

## Guard
Do not modify benchmark data or correctness checks.

## Noise Handling
- **Noise runs:** 1
- **Min consensus delta:** 0

## Current Approach
Recursive quicksort with list comprehensions, measured at 2.0421s.

## Shared Knowledge
All researchers converged on Python `sorted()` as the fastest implementation for this task.

## Conference Log
See `conference_results.tsv`, `synthesis.md`, and `final_report.md`.
