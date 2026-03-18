"""Benchmark helper for per-researcher sort files. Usage: python bench_researcher.py sort_A"""
import importlib
import json
import random
import statistics
import sys
import time


def generate_test_data(n: int = 1_000_000, seed: int = 42) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(0, 10_000_000) for _ in range(n)]


def verify_correctness(sort_fn) -> bool:
    cases = [
        [],
        [1],
        [3, 1, 2],
        [5, 5, 5],
        list(range(100)),
        list(range(100, 0, -1)),
    ]
    for case in cases:
        result = sort_fn(case[:])
        if result != sorted(case):
            print(f"FAIL: input={case[:20]}... expected={sorted(case)[:20]}... got={result[:20]}...")
            return False
    # Stability check
    data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    result = sort_fn(data[:])
    if result != sorted(data):
        print(f"FAIL: stability/correctness check failed")
        return False
    return True


def benchmark(sort_fn, data: list[int], runs: int = 5) -> dict:
    times = []
    for i in range(runs):
        arr = data[:]
        t0 = time.perf_counter()
        result = sort_fn(arr)
        t1 = time.perf_counter()
        times.append(t1 - t0)
        if i == 0 and result != sorted(data):
            return {"error": "incorrect output", "times": times}
    return {
        "median": round(statistics.median(times), 4),
        "mean": round(statistics.mean(times), 4),
        "min": round(min(times), 4),
        "max": round(max(times), 4),
        "stdev": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
        "times": [round(t, 4) for t in times],
    }


def main():
    sys.setrecursionlimit(10_000)
    module_name = sys.argv[1] if len(sys.argv) > 1 else "sort"
    mod = importlib.import_module(module_name)
    importlib.reload(mod)

    if not verify_correctness(mod.sort_integers):
        print("CORRECTNESS_FAIL")
        print(json.dumps({"error": "correctness failure"}))
        sys.exit(1)

    data = generate_test_data()
    results = benchmark(mod.sort_integers, data, runs=5)

    if "error" in results:
        print(f"BENCHMARK_FAIL: {results['error']}")
        print(json.dumps(results))
        sys.exit(1)

    print(f"median={results['median']}")
    print(json.dumps(results))


if __name__ == "__main__":
    main()
