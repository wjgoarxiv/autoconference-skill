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
1. **Non-comparison sorts dominate for integers.** LSD radix sort (0.474s) and counting sort (0.458s) both beat comparison-based sorts by 3-4x for 1M integers in range 0-10M.
2. **Dict-based counting is faster than list-based for sparse distributions.** With 1M values in 0-10M range, dict avoids allocating a 10M-entry list and skips 9M empty slots during output.
3. **LSD radix sort base 65536 achieves 2 passes** for values up to ~4B, down from 3 passes with base 256 (32% faster).
4. **C-level builtins should be maximized.** sorted(), Counter, list multiplication [val]*count all run in C and are 10-100x faster than equivalent Python loops.
5. **sorted() is the optimal single-function solution** at 0.152s, but is a trivial wrapper — the non-trivial approaches teach more about algorithm design.
6. **Python loop overhead is the fundamental bottleneck.** Any competitive pure-Python approach must minimize Python-level iterations.

### Round 2 Validated Findings
7. **All researchers converged on sorted().** No Python-level preprocessing (radix partitioning, bucketing, heapq.merge, chunk sorting) can beat a single C-level sorted() call.
8. **Counter is equivalent to manual dict for counting** — not faster as initially hypothesized. Counter has internal bookkeeping overhead that offsets its C-level counting.
9. **itertools wrapped in generators is an anti-pattern.** Python generator frames negate C-level itertools speed.
10. **Best non-trivial approaches:** LSD radix sort base 65536 (0.474s) and dict-based counting sort (0.458s) are the fastest pure-Python implementations without using sorted().

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
| 1 | A | 0.4742s | LSD radix sort base 65536 beats comparison sorts | validated |
| 1 | B | 0.4585s | Dict-based counting sort optimal for sparse integer data | validated |
| 1 | C | 0.1521s | Built-in sorted() is unbeatable in pure Python | validated |
| 2 | A | 0.1516s | Adopted sorted() from shared knowledge; no preprocessing beats it | validated |
| 2 | B | 0.152s | Adopted sorted(); Counter ~ manual dict, itertools generators slow | validated |
| 2 | C | 0.1521s | Confirmed sorted() optimal; no further improvement | validated |
| - | ALL | 0.1516s | **CONVERGED** — best metric stable across 2 rounds | converged |
