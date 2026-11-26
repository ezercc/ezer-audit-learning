"""审阅版完整链路。阶段都在，高质量分支被固定跳过。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from ezer_audit_review.clamp import clamp_points, clamp_status
from ezer_audit_review.config import review_manifest
from ezer_audit_review.models import ReviewModel, build_model
from ezer_audit_review.prompts_loader import prompt_profile
from ezer_audit_review.source import FixtureSource

PERIODS = {"FY", "Q1", "Q2", "Q3", "H1"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_request(raw: Dict[str, Any]) -> Dict[str, Any]:
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


def _event(name: str, producer: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {"event": name, "producer": producer, "data": data}


def run_chain(
    raw_request: Dict[str, Any],
    *,
    model: ReviewModel | None = None,
    source: FixtureSource | None = None,
) -> Dict[str, Any]:
    request = parse_request(raw_request)
    selected_model = model or build_model()
    selected_source = source or FixtureSource()
    prompts = prompt_profile(request["lang"])
    manifest = review_manifest()
    events: List[Dict[str, Any]] = []
    state_path = ["INIT"]

    if request["errors"]:
        state_path.append("FAILED")
        return _result(
            request=request,
            status="NO_VALID_CONCLUSION",
            summary="请求字段不足，审阅版没有补全。" if request["lang"] != "en" else "Request fields are incomplete.",
            cards=[],
            points=[],
            note="",
            events=events,
            state_path=state_path,
            model_name=selected_model.name,
            prompt_id=prompts["id"],
            manifest=manifest,
        )

    state_path.append("RESOLVED")
    events.append(_event("resolved", "SYSTEM", {"code": request["code"], "year": request["year"], "period": request["period"]}))

    sample = selected_source.load(request["code"], request["year"], request["period"])
    if sample is None:
        state_path.extend(["FAILED"])
        events.append(_event("fetch_miss", "A", {"reason": "fixture_only"}))
        summary = "审阅版只有本地样例，没有外部取数。" if request["lang"] != "en" else "Review build has only a local sample."
        return _result(
            request=request,
            status="NO_VALID_CONCLUSION",
            summary=summary,
            cards=[],
            points=[],
            note="",
            events=events,
            state_path=state_path,
            model_name=selected_model.name,
            prompt_id=prompts["id"],
            manifest=manifest,
        )

    points = clamp_points(sample["points"])
    state_path.append("FETCHED")
    query = f"{sample['name']} {request['year']} {request['period']}"
    events.append(_event("q_query", "Q", {"query": query, "executed": False}))
    events.append(_event("a_normalized", "A", {"points": len(points)}))

    cards = selected_model.cards(sample, prompts["b"], request["lang"])
    state_path.extend(["ANALYZED", "GATED"])
    events.append(_event("b_cards", "B", {"count": len(cards)}))
    events.append(_event("gate", "GATE", {"supplement_retries": 0, "trusted_allowed": False}))
    for stage in manifest["skipped_stages"]:
        events.append(_event("skipped", "SYSTEM", {"stage": stage, "reason": "disabled_in_review_build"}))

    note = selected_model.review_note(cards, prompts["c"], request["lang"])
    status = clamp_status("PASS_WITH_WARNINGS", cards, points)
    state_path.extend(["REVIEWED", "SUMMARIZED", "DELIVERED"])
    events.append(_event("c_done", "C", {"final_status": status}))
    if request["lang"] == "en":
        summary = f"{sample['name']} review sample finished with warnings."
    else:
        summary = f"{sample['name']}审阅样例已完成，结论带有限制。"
    return _result(
        request=request,
        status=status,
        summary=summary,
        cards=cards,
        points=points,
        note=note,
        events=events,
        state_path=state_path,
        model_name=selected_model.name,
        prompt_id=prompts["id"],
        manifest=manifest,
        query=query,
    )


def _result(
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
        "events": events,
        "meta": {
            "state_path": state_path,
            "generated_at": utc_now(),
            "model_mode": model_name,
            "prompt_profile": prompt_id,
            "prompt_effect": "clamped",
            "history_count": len(points),
            "allows_trusted": False,
            "live_data": False,
            "request": {key: request[key] for key in ("code", "period", "year", "lang")},
        },
    }
