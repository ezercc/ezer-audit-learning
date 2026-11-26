"""本机审阅接口。只暴露降级链路，不暴露已删除能力。"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict
from urllib.parse import urlparse

from ezer_audit_review.api.tasks import TaskStore
from ezer_audit_review.config import demo_token, review_manifest
from ezer_audit_review.pipeline import run_chain
from ezer_audit_review.stages.registry import stage_reports


class ReviewHandler(BaseHTTPRequestHandler):
    task_store = TaskStore()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if not self._authorized() and path != "/health":
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        if path == "/health":
            self._send(HTTPStatus.OK, {"status": "ok", "profile": "degraded"})
            return
        if path == "/v1/manifest":
            payload = review_manifest()
            payload["stages"] = stage_reports()
            payload["commercial"] = False
            self._send(HTTPStatus.OK, payload)
            return
        if path.startswith("/v1/tasks/"):
            task = self.task_store.get(path.rsplit("/", 1)[-1])
            if task is None:
                self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
                return
            self._send(HTTPStatus.OK, task)
            return
        self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/v1/review", "/v1/tasks"}:
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        if not self._authorized():
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        raw = self._read_json()
        if raw is None:
            return
        result = self.task_store.put(run_chain(raw))
        self._send(HTTPStatus.OK, result)

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _authorized(self) -> bool:
        token = demo_token()
        if not token:
            return True
        return self.headers.get("Authorization") == f"Bearer {token}"

    def _read_json(self) -> Dict[str, Any] | None:
        length = int(self.headers.get("Content-Length") or "0")
        try:
            raw = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return None
        if not isinstance(raw, dict):
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_body"})
            return None
        return raw

    def _send(self, status: HTTPStatus, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    if host != "127.0.0.1":
        raise ValueError("review server binds to loopback only")
    store = TaskStore()

    class BoundHandler(ReviewHandler):
        task_store = store

    return ThreadingHTTPServer((host, port), BoundHandler)
