"""内存任务表。进程退出后不保留。"""

from __future__ import annotations

from typing import Any, Dict, Optional


class TaskStore:
    def __init__(self) -> None:
        self._items: Dict[str, Dict[str, Any]] = {}

    def put(self, result: Dict[str, Any]) -> Dict[str, Any]:
        self._items[str(result["task_id"])] = result
        return result

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._items.get(task_id)
