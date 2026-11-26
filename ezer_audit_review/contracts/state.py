"""事件与状态合同。"""

from __future__ import annotations

from typing import Any, Dict, List, Set


TRANSITIONS = {
    "INIT": {"RESOLVED", "FAILED"},
    "RESOLVED": {"FETCHED", "FAILED"},
    "FETCHED": {"PLANNED"},
    "PLANNED": {"ANALYZED"},
    "ANALYZED": {"GATED"},
    "GATED": {"INDUSTRY"},
    "INDUSTRY": {"OUTLOOK"},
    "OUTLOOK": {"REVIEWED"},
    "REVIEWED": {"SUMMARIZED"},
    "SUMMARIZED": {"DELIVERED"},
    "FAILED": set(),
    "DELIVERED": set(),
}


class StateMachine:
    def __init__(self) -> None:
        self.path = ["INIT"]

    def move(self, nxt: str) -> None:
        current = self.path[-1]
        allowed: Set[str] = TRANSITIONS[current]
        if nxt not in allowed:
            raise RuntimeError(f"illegal transition: {current} -> {nxt}")
        self.path.append(nxt)


def event(name: str, producer: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {"event": name, "producer": producer, "data": data}


class EventLog:
    def __init__(self) -> None:
        self.items: List[Dict[str, Any]] = []

    def add(self, name: str, producer: str, data: Dict[str, Any]) -> None:
        self.items.append(event(name, producer, data))
