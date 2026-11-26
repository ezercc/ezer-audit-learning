"""标准化阶段。只保留营收和净利润，并截断期间。"""

from __future__ import annotations

from typing import Any, Dict, List

from ezer_audit_review.clamp import clamp_points


def normalize_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    points: List[Dict[str, Any]] = clamp_points(sample.get("points") or [])
    return {
        "code": sample.get("code"),
        "name": sample.get("name"),
        "year": sample.get("year"),
        "period": sample.get("period"),
        "points": points,
        "metrics": ["revenue", "net_profit"],
    }
