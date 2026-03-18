# Conference: Sorting Algorithm Optimization

## Goal
Reduce execution time of the integer sorting function in `sort.py` when sorting an array of 1,000,000 random integers. The function must produce a correctly sorted output and maintain sort stability.

## Mode
metric

## Success Metric
- **Metric:** Execution time in seconds (median of 5 runs on 1M random integers, range 0--10,000,000)
- **Target:** < 0.5s
- **Direction:** minimize

## Researchers
- **Count:** 3
- **Iterations per round:** 5
- **Max rounds:** 3

## Search Space
- **Allowed changes:** Algorithm choice, data structures, partitioning strategy, hybrid approaches, insertion sort cutoff for small subarrays, iterative vs recursive, built-in function usage (sorted() is allowed since it's stdlib)
- **Forbidden changes:** Function signature, input/output format, constraints below (pure Python, stability, edge cases)

## Search Space Partitioning
- **Strategy:** assigned

### Researcher A Focus
Algorithmic changes: complexity reduction, better algorithm selection (merge sort, radix sort, Timsort-style hybrid), elimination of redundant computation, recursion removal.

### Researcher B Focus
Data structure optimization: memory layout improvements, container choice (list vs array), reducing temporary list allocations, in-place operations where possible.

### Researcher C Focus
Low-level optimization: cache locality improvements, vectorization-friendly patterns, Python-specific tricks (list comprehensions over loops, builtin usage), profiling-guided micro-optimizations.

## Constraints
- **Max total iterations:** 45
- **Time budget:** 2h
- **Researcher timeout:** 40m
- Pure Python only -- no C extensions, no Cython, no ctypes, no subprocess calls to compiled code
- Must maintain sort stability (equal elements preserve original order)
- Must handle edge cases: empty list, single element, already sorted, reverse sorted
- Function signature must remain: `def sort_integers(arr: list[int]) -> list[int]`
- No external libraries (only Python stdlib)

## Current Approach
Basic recursive quicksort implementation in `sort.py`:

```python
def sort_integers(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return sort_integers(left) + middle + sort_integers(right)
```

Baseline: 2.3991s median on 1M integers.

Known issues:
- Three list comprehensions create excessive temporary lists
- Recursive calls add stack overhead
- No special handling for nearly-sorted data
- Not stable (quicksort is inherently unstable, though this partition-based variant happens to be)

## Shared Knowledge
<!-- Auto-populated after each round with validated findings -->

### Round 1 Validated Findings
1. **Radix sort base 65536 (Researcher A):** LSD radix sort with 2 explicit 16-bit passes achieves 0.4261s — best pure-Python algorithmic approach. Stable sort.
2. **Comparison-sort ceiling (Researcher A):** Optimizing comparison sorts (merge sort variants) yields only ~15% improvement over baseline — the path to big gains is non-comparison sorts.
3. **Counting sort for bounded ranges (Researcher B):** Counting sort achieves 0.5462s but is sensitive to value range (10M count array allocation). Uses extend([val]*count) for C-level bulk output.
4. **array.array anti-pattern (Researcher B):** array.array element access in Python is slower due to boxing/unboxing — do not use for sorting.
5. **C-level Timsort floor (Researcher C):** sorted()/list.sort() at 0.14s is ~3x faster than any pure-Python sort — this is the practical performance ceiling.
6. **Bucket sort anti-pattern (Researcher C):** Pre-bucketing does not help Timsort — the distribution overhead exceeds the sorting benefit.

## Context & References
- Python's built-in `sorted()` uses Timsort -- highly optimized C implementation, typically ~0.18s for 1M integers
- Using `sorted()` is allowed but the goal is to learn what algorithmic choices matter
- Timsort: hybrid merge sort + insertion sort, exploits existing order ("runs")
- Radix sort is O(n*k) but not comparison-based -- may be worth exploring for integers
- Insertion sort is fastest for small arrays (n < 20-50)
- Benchmark script: `benchmark.py`
- All iterations reference implementation: `run_iterations.py`

---

## Conference Log
<!-- Auto-maintained by Conference Chair. Do not edit manually. -->
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
| 1 | A | 0.4261s | LSD radix sort base 65536, 2-pass explicit | target_reached |
| 1 | B | 0.5462s | Counting sort with extend([val]*count) | completed |
| 1 | C | 0.1431s | Python built-in list.sort() (C Timsort) | target_reached |
