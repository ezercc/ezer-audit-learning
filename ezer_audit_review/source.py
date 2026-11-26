"""审阅版只读取本地样例，不连接外部数据源。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "fixtures" / "sample_company.json"


class FixtureSource:
    def __init__(self, path: Path = FIXTURE_PATH) -> None:
        self.path = path

    def load(self, code: str, year: int, period: str) -> Optional[Dict[str, Any]]:
        sample = json.loads(self.path.read_text(encoding="utf-8"))
        if str(sample.get("code")) != code:
            return None
        if int(sample.get("year")) != int(year) or str(sample.get("period")) != period:
            return None
        points = sample.get("points") or []
        return {
            "code": sample["code"],
            "name": sample["name"],
            "year": int(sample["year"]),
            "period": sample["period"],
            "points": [
                {
                    "label": str(item["label"]),
                    "revenue": item.get("revenue"),
                    "net_profit": item.get("net_profit"),
                }
                for item in points
                if isinstance(item, dict)
            ],
        }
