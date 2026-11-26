"""复核阶段。只给限制说明，不做质量裁判。"""

from __future__ import annotations

from typing import Any, Dict, List

from ezer_audit_review.clamp import clamp_status
from ezer_audit_review.models import ReviewModel


def audit(
    cards: List[Dict[str, str]],
    points: List[Dict[str, Any]],
    model: ReviewModel,
    prompt: str,
    lang: str,
) -> Dict[str, str]:
    return {
        "final_status": clamp_status("PASS_WITH_WARNINGS", cards, points),
        "note": model.review_note(cards, prompt, lang),
    }
