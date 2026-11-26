"""只监听本机的审阅接口。"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from ezer_audit_review.config import demo_token
from ezer_audit_review.pipeline import run_chain


class ReviewHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        self._send(HTTPStatus.OK, {"status": "ok", "profile": "degraded"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/review":
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        token = demo_token()
        if token and self.headers.get("Authorization") != f"Bearer {token}":
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        length = int(self.headers.get("Content-Length") or "0")
        try:
            raw = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return
        if not isinstance(raw, dict):
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_body"})
            return
        self._send(HTTPStatus.OK, run_chain(raw))

    def log_message(self, fmt: str, *args: Any) -> None:
        return

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
    return ThreadingHTTPServer((host, port), ReviewHandler)
