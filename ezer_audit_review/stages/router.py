"""模型路由。单槽位，产业和展望阶段不允许调用模型。"""

from __future__ import annotations

from typing import Any, Dict

MODEL_STAGES = {"B", "C"}


def route(stage: str, model_name: str) -> Dict[str, Any]:
    allowed = stage in MODEL_STAGES
    return {
        "stage": stage,
        "model": model_name if allowed else "",
        "allowed": allowed,
        "attempts": 1 if allowed else 0,
        "fallback": False,
    }
