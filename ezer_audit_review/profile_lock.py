"""拒绝把审阅版开关拨回已删除的能力。"""

from __future__ import annotations

import os
from typing import List

COMMERCIAL_SWITCHES = (
    "REVIEW_ENABLE_LIVE_DATA",
    "REVIEW_ENABLE_SEMANTIC_RERANK",
    "REVIEW_ENABLE_OUTLOOK",
    "REVIEW_ENABLE_HIGH_CONFIDENCE",
    "REVIEW_ENABLE_KEY_POOL",
    "REVIEW_ENABLE_SUPPLEMENT",
    "REVIEW_ENABLE_PROVIDER_FALLBACK",
)
TRUTHY = {"1", "true", "yes", "on"}


def rejected_switches() -> List[str]:
    found = []
    for name in COMMERCIAL_SWITCHES:
        value = os.environ.get(name, "").strip().lower()
        if value in TRUTHY:
            found.append(name)
    return found
