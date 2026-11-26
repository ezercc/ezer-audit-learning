"""硬门。不补数，也不放行高置信结论。"""

from __future__ import annotations

from typing import Any, Dict


def apply_gate() -> Dict[str, Any]:
    return {
        "supplement_retries": 0,
        "attempted": False,
        "high_confidence_allowed": False,
        "reason": "disabled_in_review_build",
    }
