#!/usr/bin/env python3
"""Minimal FE lab: array / stack (LIFO) / queue (FIFO) contracts.

Run:  python3 verify.py
Opt:  python3 verify.py --learner   # enables TODO checks (fill stubs first)
"""

from __future__ import annotations

import argparse
import sys


# --- Reference ADTs (lab contracts; keep tiny) ---------------------------------


class Stack:
    """LIFO: touch the top only."""

    def __init__(self) -> None:
        self._items: list[object] = []

    def push(self, value: object) -> None:
        self._items.append(value)

    def pop(self) -> object:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> object:
        if not self._items:
            raise IndexError("peek on empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)


class Queue:
    """FIFO: enqueue at rear, dequeue at front."""

    def __init__(self) -> None:
        self._items: list[object] = []

    def enqueue(self, value: object) -> None:
        self._items.append(value)

    def dequeue(self) -> object:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)

    def __len__(self) -> int:
        return len(self._items)


# --- Contract checks ----------------------------------------------------------


def check_array_random_access() -> None:
    # Fixed layout: index → value in O(1) mental model for FE.
    scores = [70, 85, 90, 60]
    assert scores[2] == 90, "array: known index must read the expected element"
    assert len(scores) == 4, "array: length is the count of slots"


def check_stack_lifo() -> None:
    s = Stack()
    s.push("A")
    s.push("B")
    s.push("C")
    assert s.pop() == "C", "stack: last pushed must come out first (LIFO)"
    assert s.pop() == "B", "stack: LIFO continues"
    assert s.peek() == "A", "stack: peek must not remove"
    assert s.pop() == "A", "stack: final pop"
    assert len(s) == 0, "stack: empty after balanced push/pop"


def check_queue_fifo() -> None:
    q = Queue()
    q.enqueue("job-1")
    q.enqueue("job-2")
    q.enqueue("job-3")
    assert q.dequeue() == "job-1", "queue: first enqueued must leave first (FIFO)"
    assert q.dequeue() == "job-2", "queue: FIFO continues"
    assert q.dequeue() == "job-3", "queue: final dequeue"
    assert len(q) == 0, "queue: empty after balanced enqueue/dequeue"


def check_empty_edges() -> None:
    s = Stack()
    q = Queue()
    try:
        s.pop()
        raise AssertionError("stack: pop on empty must fail")
    except IndexError:
        pass
    try:
        q.dequeue()
        raise AssertionError("queue: dequeue on empty must fail")
    except IndexError:
        pass


# --- LEARNER_TODO (scaffolding; optional) ------------------------------------
# Fill these only when practicing recall. Default run does not call them.
# Do not ask the tutor for an unlock dump until you have attempted twice.


def choose_structure(scenario: str) -> str:
    """Return one of: 'array' | 'linked_list' | 'stack' | 'queue'.

    TODO: implement from the concept card (delete the raise when ready).
    """
    raise NotImplementedError("learner TODO: map scenario → structure name")


def learner_checks() -> None:
    cases = {
        "browser back-button history": "stack",
        "printer job waiting line": "queue",
        "read the 100th sensor sample by index": "array",
        "insert a node beside a known neighbor often": "linked_list",
    }
    for scenario, expected in cases.items():
        got = choose_structure(scenario)
        assert got == expected, f"scenario {scenario!r}: expected {expected!r}, got {got!r}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--learner",
        action="store_true",
        help="also run LEARNER_TODO checks (fill stubs first)",
    )
    args = parser.parse_args()

    check_array_random_access()
    check_stack_lifo()
    check_queue_fifo()
    check_empty_edges()
    print("OK: array / stack(LIFO) / queue(FIFO) contracts hold")

    if args.learner:
        try:
            learner_checks()
        except NotImplementedError as exc:
            print(f"LEARNER_TODO incomplete: {exc}", file=sys.stderr)
            return 2
        print("OK: learner scenario → structure mapping")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
