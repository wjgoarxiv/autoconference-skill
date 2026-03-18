"""Sorting function under optimization. Researcher C's workspace."""


def sort_integers(arr: list[int]) -> list[int]:
    """Sort a list of integers in ascending order.

    Researcher C, Best (Iteration 2): list copy + in-place sort.
    Uses C-level Timsort via list.sort(). Stable sort.
    """
    result = list(arr)
    result.sort()
    return result
