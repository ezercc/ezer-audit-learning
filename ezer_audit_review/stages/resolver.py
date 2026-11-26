"""请求字段检查。不补全缺失字段。"""

from __future__ import annotations

from typing import Any, Dict

PERIODS = {"FY", "Q1", "Q2", "Q3", "H1"}


def resolve_request(raw: Dict[str, Any]) -> Dict[str, Any]:
    code = str(raw.get("code") or "").strip().upper()
    period = str(raw.get("period") or "").strip().upper()
    lang = "en" if str(raw.get("lang") or "").lower().startswith("en") else "zh-CN"
    try:
        year = int(raw.get("year"))
    except (TypeError, ValueError):
        year = 0
    errors = []
    if len(code) < 6 or "." not in code:
        errors.append("code")
    if period not in PERIODS:
        errors.append("period")
    if year < 1990 or year > 2100:
        errors.append("year")
    return {"code": code, "period": period, "year": year, "lang": lang, "errors": errors}
