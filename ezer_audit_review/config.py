"""审阅降级版配置。这里没有生产质量档位。"""

from __future__ import annotations

import os
from typing import Any, Dict

PROFILE = "degraded"
HISTORY_LIMIT = 4
CARD_IDS = ("overview", "profit_note", "limits")
CARD_TEXT_LIMIT = 60
ALLOWED_STATUSES = ("PASS_WITH_WARNINGS", "NO_VALID_CONCLUSION")
SUPPLEMENT_RETRIES = 0
SKIPPED_STAGES = ("I", "O", "supplement", "provider_fallback")


def review_manifest() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "history_limit": HISTORY_LIMIT,
        "card_ids": list(CARD_IDS),
        "card_text_limit": CARD_TEXT_LIMIT,
        "allowed_statuses": list(ALLOWED_STATUSES),
        "allows_trusted": False,
        "supplement_retries": SUPPLEMENT_RETRIES,
        "live_data": False,
        "semantic_rerank": False,
        "business_outlook": False,
        "provider_fallback": False,
        "key_pool": False,
        "skipped_stages": list(SKIPPED_STAGES),
    }


def model_settings() -> Dict[str, str]:
    return {
        "mode": os.environ.get("REVIEW_MODEL_MODE", "local-template").strip() or "local-template",
        "base_url": os.environ.get("REVIEW_MODEL_BASE_URL", "").strip(),
        "api_key": os.environ.get("REVIEW_MODEL_API_KEY", "").strip(),
        "model_name": os.environ.get("REVIEW_MODEL_NAME", "review-small").strip() or "review-small",
    }


def demo_token() -> str:
    return os.environ.get("REVIEW_DEMO_TOKEN", "").strip()
