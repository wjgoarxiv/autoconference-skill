"""Sorting function under optimization. Researcher B's workspace."""


def sort_integers(arr: list[int]) -> list[int]:
    """Sort a list of integers in ascending order.

    Researcher B, Iteration 4 (best): Optimized counting sort.
    Uses list extend with [val]*count for C-level bulk operations.
    Stable sort.
    """
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a

    min_val = min(a)
    max_val = max(a)
    range_size = max_val - min_val + 1

    count = [0] * range_size
    for x in a:
        count[x - min_val] += 1

    result = []
    extend = result.extend
    for i in range(range_size):
        c = count[i]
        if c:
            extend([i + min_val] * c)

    return result
