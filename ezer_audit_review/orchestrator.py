"""把阶段串成审阅链路。结构完整，效果保持降级。"""

from __future__ import annotations

from typing import Any, Dict

from ezer_audit_review.config import review_manifest
from ezer_audit_review.contracts.result import build_result
from ezer_audit_review.contracts.state import EventLog, StateMachine
from ezer_audit_review.models import ReviewModel, build_model
from ezer_audit_review.profile_lock import rejected_switches
from ezer_audit_review.prompts_loader import prompt_profile
from ezer_audit_review.source import FixtureSource
from ezer_audit_review.stages.analyzer import analyze
from ezer_audit_review.stages.auditor import audit
from ezer_audit_review.stages.fetcher import fetch_sample
from ezer_audit_review.stages.gate import apply_gate
from ezer_audit_review.stages.industry import run_industry
from ezer_audit_review.stages.normalizer import normalize_sample
from ezer_audit_review.stages.outlook import run_outlook
from ezer_audit_review.stages.planner import plan_query
from ezer_audit_review.stages.resolver import resolve_request
from ezer_audit_review.stages.router import route
from ezer_audit_review.stages.summarizer import summarize


def run_chain(
    raw_request: Dict[str, Any],
    *,
    model: ReviewModel | None = None,
    source: FixtureSource | None = None,
) -> Dict[str, Any]:
    selected_model = model or build_model()
    selected_source = source or FixtureSource()
    manifest = review_manifest()
    blocked = rejected_switches()
    if blocked:
        return _finish(
            request={"lang": "zh-CN"},
            status="NO_VALID_CONCLUSION",
            summary="审阅版拒绝打开已删除的能力。",
            state_path=["INIT", "FAILED"],
            model_name=selected_model.name,
            prompt_id="review-short-locked",
            manifest=manifest,
            rejected_switches=blocked,
        )

    request = resolve_request(raw_request if isinstance(raw_request, dict) else {})
    prompts = prompt_profile(request["lang"])
    machine = StateMachine()
    events = EventLog()
    if request["errors"]:
        machine.move("FAILED")
        summary = "请求字段不足，审阅版没有补全。" if request["lang"] != "en" else "Request fields are incomplete."
        return _finish(
            request=request,
            status="NO_VALID_CONCLUSION",
            summary=summary,
            events=events.items,
            state_path=machine.path,
            model_name=selected_model.name,
            prompt_id=prompts["id"],
            manifest=manifest,
        )

    machine.move("RESOLVED")
    events.add("resolved", "SYSTEM", {"code": request["code"], "year": request["year"], "period": request["period"]})
    sample = fetch_sample(request, selected_source)
    if sample is None:
        machine.move("FAILED")
        events.add("fetch_miss", "A", {"reason": "fixture_only"})
        summary = "审阅版只有本地样例，没有外部取数。" if request["lang"] != "en" else "Review build has only a local sample."
        return _finish(
            request=request,
            status="NO_VALID_CONCLUSION",
            summary=summary,
            events=events.items,
            state_path=machine.path,
            model_name=selected_model.name,
            prompt_id=prompts["id"],
            manifest=manifest,
        )

    machine.move("FETCHED")
    normalized = normalize_sample(sample)
    planned = plan_query(normalized, request, prompts["q"])
    machine.move("PLANNED")
    events.add("q_query", "Q", planned)
    events.add("a_normalized", "A", {"points": len(normalized["points"]), "metrics": normalized["metrics"]})

    routed = {
        "B": route("B", selected_model.name),
        "C": route("C", selected_model.name),
        "I": route("I", selected_model.name),
        "O": route("O", selected_model.name),
    }
    events.add("provider", "SYSTEM", {"attempts": 1, "fallback": False, "routes": routed})
    cards = analyze(normalized, selected_model, prompts["b"], request["lang"])
    machine.move("ANALYZED")
    events.add("b_cards", "B", {"count": len(cards)})

    gate = apply_gate()
    machine.move("GATED")
    events.add("gate", "GATE", {"supplement_retries": 0, "trusted_allowed": False})
    events.add("supplement", "GATE", {"attempted": False, "reason": gate["reason"]})

    industry = run_industry(prompts["i"])
    machine.move("INDUSTRY")
    events.add("i_industry", "I", industry)
    outlook = run_outlook(prompts["o"])
    machine.move("OUTLOOK")
    events.add("o_outlook", "O", outlook)

    audited = audit(cards, normalized["points"], selected_model, prompts["c"], request["lang"])
    machine.move("REVIEWED")
    events.add("c_done", "C", {"final_status": audited["final_status"]})
    machine.move("SUMMARIZED")
    machine.move("DELIVERED")
    return _finish(
        request=request,
        status=audited["final_status"],
        summary=summarize(str(normalized["name"]), request["lang"]),
        cards=cards,
        points=normalized["points"],
        note=audited["note"],
        events=events.items,
        state_path=machine.path,
        model_name=selected_model.name,
        prompt_id=prompts["id"],
        manifest=manifest,
        query=planned["query"],
        industry=industry,
        outlook=outlook,
        gate=gate,
    )


def _finish(**kwargs: Any) -> Dict[str, Any]:
    defaults: Dict[str, Any] = {
        "cards": [],
        "points": [],
        "note": "",
        "events": [],
        "query": "",
    }
    defaults.update(kwargs)
    return build_result(**defaults)
