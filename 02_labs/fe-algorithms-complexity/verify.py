#!/usr/bin/env python3
"""Minimal FE lab: linear vs binary search + complexity-order intuition.

Run:  python3 verify.py
Opt:  python3 verify.py --learner   # enables TODO checks (fill stubs first)
"""

from __future__ import annotations

import argparse
import sys


# --- Tiny search helpers (lab contracts; keep tiny) ---------------------------


def linear_search(data: list[int], key: int) -> tuple[int | None, int]:
    """Scan left→right. Returns (index or None, comparison_count)."""
    comparisons = 0
    for i, value in enumerate(data):
        comparisons += 1
        if value == key:
            return i, comparisons
    return None, comparisons


def binary_search(sorted_data: list[int], key: int) -> tuple[int | None, int]:
    """Requires ascending sorted_data. Returns (index or None, comparison_count)."""
    lo = 0
    hi = len(sorted_data) - 1
    comparisons = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1
        found = sorted_data[mid]
        if found == key:
            return mid, comparisons
        if found < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return None, comparisons


# Growth "ladder" used only for order checks (smaller index = asymptotically better).
ORDER_LADDER = ("O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)")


def order_rank(label: str) -> int:
    try:
        return ORDER_LADDER.index(label)
    except ValueError as exc:
        raise AssertionError(f"unknown complexity label: {label!r}") from exc


# --- Contract checks ----------------------------------------------------------


def check_linear_finds_unsorted() -> None:
    bag = [9, 1, 4, 7, 2]
    idx, comps = linear_search(bag, 7)
    assert idx == 3, "linear: must find key by scanning from the left"
    assert comps == 4, "linear: comparisons equal position+1 when found mid-list"
    missing, miss_comps = linear_search(bag, 5)
    assert missing is None, "linear: missing key → None"
    assert miss_comps == len(bag), "linear: miss scans all elements (≈ O(n))"


def check_binary_needs_sorted_and_is_cheaper() -> None:
    sorted_nums = list(range(0, 64))  # 0..63 inclusive → 64 elements
    key = 50
    b_idx, b_comps = binary_search(sorted_nums, key)
    l_idx, l_comps = linear_search(sorted_nums, key)
    assert b_idx == key == l_idx, "binary/linear: same correct index on sorted data"
    assert b_comps < l_comps, "binary: should use fewer comparisons than linear here"
    assert b_comps <= 7, "binary: log2(64)=6 ballpark; allow a small constant slack"
    miss_idx, _ = binary_search(sorted_nums, 99)
    assert miss_idx is None, "binary: missing key → None"


def check_empty_and_singleton() -> None:
    assert linear_search([], 1) == (None, 0), "linear: empty → None, 0 comps"
    assert binary_search([], 1) == (None, 0), "binary: empty → None, 0 comps"
    assert linear_search([42], 42) == (0, 1), "linear: singleton hit"
    assert binary_search([42], 42) == (0, 1), "binary: singleton hit"
    assert linear_search([42], 0)[0] is None, "linear: singleton miss"
    assert binary_search([42], 0)[0] is None, "binary: singleton miss"


def check_order_ladder_intuition() -> None:
    # FE-style map: name → rough class (not a proof; contract for the card).
    expected = {
        "array index read": "O(1)",
        "binary search on sorted array": "O(log n)",
        "linear search": "O(n)",
        "mergesort-class sort": "O(n log n)",
        "naive nested-loop sort": "O(n^2)",
    }
    for name, label in expected.items():
        assert label in ORDER_LADDER, f"{name}: label must be on the FE ladder"
    assert order_rank("O(log n)") < order_rank("O(n)"), "log n beats linear"
    assert order_rank("O(n)") < order_rank("O(n log n)"), "linear beats n log n"
    assert order_rank("O(n log n)") < order_rank("O(n^2)"), "n log n beats quadratic"


# --- LEARNER_TODO (scaffolding; optional) ------------------------------------
# Fill these only when practicing recall. Default run does not call them.
# Do not ask the tutor for an unlock dump until you have attempted twice.


def classify_growth(scenario: str) -> str:
    """Return one of ORDER_LADDER labels for the scenario string.

    TODO: implement from the concept card (delete the raise when ready).
    """
    raise NotImplementedError("learner TODO: map scenario → complexity label")


def pick_search(scenario: str) -> str:
    """Return 'linear' or 'binary'.

    TODO: implement from the concept card (delete the raise when ready).
    """
    raise NotImplementedError("learner TODO: map scenario → search strategy")


def learner_checks() -> None:
    growth_cases = {
        "read scores[i] when i is known": "O(1)",
        "binary search in a phone book already sorted by name": "O(log n)",
        "scan a unsorted sensor log for one id": "O(n)",
        "mergesort-style divide-and-conquer sort": "O(n log n)",
        "compare every pair in a double loop to sort": "O(n^2)",
    }
    for scenario, expected in growth_cases.items():
        got = classify_growth(scenario)
        assert got == expected, f"growth {scenario!r}: expected {expected!r}, got {got!r}"

    search_cases = {
        "one-shot scan of an unsorted bag": "linear",
        "many lookups on data kept sorted": "binary",
    }
    for scenario, expected in search_cases.items():
        got = pick_search(scenario)
        assert got == expected, f"search {scenario!r}: expected {expected!r}, got {got!r}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--learner",
        action="store_true",
        help="also run LEARNER_TODO checks (fill stubs first)",
    )
    args = parser.parse_args()

    check_linear_finds_unsorted()
    check_binary_needs_sorted_and_is_cheaper()
    check_empty_and_singleton()
    check_order_ladder_intuition()
    print("OK: linear/binary search contracts + complexity-order ladder hold")

    if args.learner:
        try:
            learner_checks()
        except NotImplementedError as exc:
            print(f"LEARNER_TODO incomplete: {exc}", file=sys.stderr)
            return 2
        print("OK: learner growth/search mapping")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
