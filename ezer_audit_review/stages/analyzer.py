"""分析阶段。只产出三张短卡片。"""

from __future__ import annotations

from typing import Any, Dict, List

from ezer_audit_review.models import ReviewModel


def analyze(sample: Dict[str, Any], model: ReviewModel, prompt: str, lang: str) -> List[Dict[str, str]]:
    return model.cards(sample, prompt, lang)
