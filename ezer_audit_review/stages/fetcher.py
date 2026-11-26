"""取数阶段。只读本地样例，不连接外部数据源。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ezer_audit_review.source import FixtureSource


def fetch_sample(request: Dict[str, Any], source: FixtureSource) -> Optional[Dict[str, Any]]:
    return source.load(request["code"], request["year"], request["period"])
