"""结果组装。额外字段只能描述降级，不能抬高结论。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from ezer_audit_review.stages.registry import stage_reports


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_result(
    *,
    request: Dict[str, Any],
    status: str,
    summary: str,
    cards: List[Dict[str, str]],
    points: List[Dict[str, Any]],
    note: str,
    events: List[Dict[str, Any]],
    state_path: List[str],
    model_name: str,
    prompt_id: str,
    manifest: Dict[str, Any],
    query: str = "",
    industry: Dict[str, Any] | None = None,
    outlook: Dict[str, Any] | None = None,
    gate: Dict[str, Any] | None = None,
    rejected_switches: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "task_id": f"review-{uuid.uuid4().hex[:8]}",
        "profile": manifest["profile"],
        "final_status": status,
        "summary": summary,
        "cards": cards,
        "points": points,
        "review_note": note,
        "query": query,
        "industry": industry or {"status": "degraded", "topics": [], "semantic_rerank": False},
        "outlook": outlook or {"status": "unavailable", "statements": []},
        "gate": gate or {"attempted": False, "high_confidence_allowed": False},
        "events": events,
        "stage_reports": stage_reports(),
        "meta": {
            "state_path": state_path,
            "generated_at": utc_now(),
            "model_mode": model_name,
            "prompt_profile": prompt_id,
            "prompt_effect": "clamped",
            "history_count": len(points),
            "allows_trusted": False,
            "live_data": False,
            "commercial": False,
            "rejected_switches": rejected_switches or [],
            "request": {key: request[key] for key in ("code", "period", "year", "lang") if key in request},
        },
    }
