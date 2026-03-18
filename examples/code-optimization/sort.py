"""Sorting function under optimization. Only this file gets modified by the research loop."""


def sort_integers(arr: list[int]) -> list[int]:
    """Sort a list of integers in ascending order.

    Researcher B, Round 2, Iteration 3: sorted() — confirmed fastest
    from shared knowledge. Adopting C's finding.
    """
    return sorted(arr)
