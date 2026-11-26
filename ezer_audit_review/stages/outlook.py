"""展望阶段。结构保留，但不读取正文，也不生成展望。"""

from __future__ import annotations

from typing import Any, Dict


def run_outlook(prompt: str) -> Dict[str, Any]:
    del prompt
    return {
        "status": "unavailable",
        "statements": [],
        "sections": [],
        "reason": "review_build",
    }
