"""效果路径降级：截断历史、卡片和结论，并禁止高置信状态。"""

from __future__ import annotations

from typing import Any, Dict, List

from ezer_audit_review.config import (
    ALLOWED_STATUSES,
    CARD_IDS,
    CARD_TEXT_LIMIT,
    HISTORY_LIMIT,
)


def clamp_points(points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    kept = []
    for item in points[:HISTORY_LIMIT]:
        kept.append(
            {
                "label": str(item.get("label") or ""),
                "revenue": item.get("revenue"),
                "net_profit": item.get("net_profit"),
            }
        )
    return kept


def clamp_text(value: Any) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= CARD_TEXT_LIMIT:
        return text
    return text[: CARD_TEXT_LIMIT - 1] + "…"


def clamp_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    by_id = {str(item.get("card_id") or ""): item for item in cards}
    clamped = []
    for card_id in CARD_IDS:
        source = by_id.get(card_id) or {}
        clamped.append({"card_id": card_id, "text": clamp_text(source.get("text"))})
    return clamped


def clamp_status(status: str, cards: List[Dict[str, str]], points: List[Dict[str, Any]]) -> str:
    normalized = str(status or "").strip().upper()
    if normalized not in ALLOWED_STATUSES:
        normalized = "PASS_WITH_WARNINGS"
    if len(points) < 1 or any(not card["text"] for card in cards):
        return "NO_VALID_CONCLUSION"
    if normalized == "PASS_WITH_WARNINGS":
        return normalized
    return "NO_VALID_CONCLUSION"
