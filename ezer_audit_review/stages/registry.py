"""审阅版阶段登记。模块在，商业效果不在。"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

STAGES: Tuple[Dict[str, str], ...] = (
    {"id": "resolver", "module": "stages.resolver", "effect": "field_check"},
    {"id": "Q", "module": "stages.planner", "effect": "unexecuted_query"},
    {"id": "fetch", "module": "stages.fetcher", "effect": "fixture_only"},
    {"id": "A", "module": "stages.normalizer", "effect": "two_metrics"},
    {"id": "router", "module": "stages.router", "effect": "single_slot"},
    {"id": "B", "module": "stages.analyzer", "effect": "three_short_cards"},
    {"id": "gate", "module": "stages.gate", "effect": "no_supplement_no_high_confidence"},
    {"id": "I", "module": "stages.industry", "effect": "empty_topics"},
    {"id": "O", "module": "stages.outlook", "effect": "unavailable"},
    {"id": "C", "module": "stages.auditor", "effect": "limitation_note"},
    {"id": "summary", "module": "stages.summarizer", "effect": "short_summary"},
)


def stage_reports() -> List[Dict[str, Any]]:
    return [
        {
            "stage": item["id"],
            "module": item["module"],
            "effect": item["effect"],
            "commercial": False,
        }
        for item in STAGES
    ]
