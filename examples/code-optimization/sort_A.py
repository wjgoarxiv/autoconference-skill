"""Sorting function under optimization. Researcher A's workspace."""


def sort_integers(arr: list[int]) -> list[int]:
    """Sort a list of integers in ascending order.

    Researcher A, Iteration 5: Optimized LSD Radix sort, base 65536.
    Uses two explicit passes (low 16 bits, high 16 bits) to avoid
    the while-loop condition check. Pre-computes digit arrays.
    Stable sort.
    """
    a = list(arr)
    n = len(a)
    if n <= 1:
        return a

    min_val = min(a)
    if min_val < 0:
        a = [x - min_val for x in a]

    max_val = max(a)
    if max_val == 0:
        if min_val < 0:
            return [x + min_val for x in a]
        return a

    MASK = 0xFFFF
    SIZE = 65538  # MASK + 2
    b = [0] * n

    # Pass 1: low 16 bits
    count = [0] * SIZE
    for x in a:
        count[(x & MASK) + 1] += 1
    for i in range(1, SIZE):
        count[i] += count[i - 1]
    for x in a:
        d = x & MASK
        b[count[d]] = x
        count[d] += 1
    a, b = b, a

    # Pass 2: high 16 bits (only if max_val > MASK)
    if max_val > MASK:
        count = [0] * SIZE
        for x in a:
            count[((x >> 16) & MASK) + 1] += 1
        for i in range(1, SIZE):
            count[i] += count[i - 1]
        for x in a:
            d = (x >> 16) & MASK
            b[count[d]] = x
            count[d] += 1
        a, b = b, a

    if min_val < 0:
        a = [x + min_val for x in a]
    return a
