"""Sorting function under optimization. Only this file gets modified by the research loop."""


def sort_integers(arr: list[int]) -> list[int]:
    """Sort a list of integers in ascending order.

    Baseline: recursive quicksort with list comprehensions.
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return sort_integers(left) + middle + sort_integers(right)
