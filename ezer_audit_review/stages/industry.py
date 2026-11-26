"""产业阶段。结构保留，但不检索、不聚类。"""

from __future__ import annotations

from typing import Any, Dict


def run_industry(prompt: str) -> Dict[str, Any]:
    del prompt
    return {
        "status": "degraded",
        "topics": [],
        "links": [],
        "semantic_rerank": False,
        "reason": "review_build",
    }
