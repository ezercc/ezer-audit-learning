"""查询阶段。只生成一条不执行的短查询。"""

from __future__ import annotations

from typing import Any, Dict


def plan_query(sample: Dict[str, Any], request: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    del prompt
    name = sample.get("name") or request["code"]
    return {
        "query": f"{name} {request['year']} {request['period']}",
        "executed": False,
        "slot_count": 1,
        "repair": False,
    }
