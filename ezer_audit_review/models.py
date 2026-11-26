"""审阅版模型适配。默认本地模板，远程调用只接受短输出。"""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List, Protocol
from urllib.error import URLError

from ezer_audit_review.clamp import clamp_cards, clamp_text
from ezer_audit_review.config import model_settings


class ReviewModel(Protocol):
    name: str

    def cards(self, sample: Dict[str, Any], prompt: str, lang: str) -> List[Dict[str, str]]:
        ...

    def review_note(self, cards: List[Dict[str, str]], prompt: str, lang: str) -> str:
        ...


class LocalTemplateModel:
    name = "local-template"

    def cards(self, sample: Dict[str, Any], prompt: str, lang: str) -> List[Dict[str, str]]:
        del prompt
        latest = (sample.get("points") or [{}])[-1]
        name = sample.get("name") or sample.get("code")
        revenue = latest.get("revenue")
        profit = latest.get("net_profit")
        if lang == "en":
            overview = f"{name} sample revenue {revenue}, net profit {profit}."
            profit_note = "Review build lists the sample figures only."
            limits = "No cash flow, notes, or external sources in this build."
        else:
            overview = f"{name}样例营收{revenue}，净利润{profit}。"
            profit_note = "审阅版只列出样例数字。"
            limits = "本版本没有现金流、附注或外部来源。"
        return clamp_cards(
            [
                {"card_id": "overview", "text": overview},
                {"card_id": "profit_note", "text": profit_note},
                {"card_id": "limits", "text": limits},
            ]
        )

    def review_note(self, cards: List[Dict[str, str]], prompt: str, lang: str) -> str:
        del cards, prompt
        if lang == "en":
            return "Review build cannot confirm quality or an audit opinion."
        return "审阅版不能确认质量，也不能给出审计意见。"


class RemoteReviewModel:
    """可选远程小模型。失败时退回本地模板，不重试，不换供应商。"""

    name = "remote-clamped"

    def __init__(self, settings: Dict[str, str] | None = None) -> None:
        self.settings = settings or model_settings()
        self.fallback = LocalTemplateModel()
        self.last_error = ""

    def ready(self) -> bool:
        return bool(self.settings.get("base_url") and self.settings.get("api_key"))

    def _complete(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        body = {
            "model": self.settings["model_name"],
            "max_tokens": 180,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
        }
        request = urllib.request.Request(
            self.settings["base_url"],
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings['api_key']}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        return json.loads(content)

    def cards(self, sample: Dict[str, Any], prompt: str, lang: str) -> List[Dict[str, str]]:
        if not self.ready():
            self.last_error = "remote_not_configured"
            return self.fallback.cards(sample, prompt, lang)
        try:
            parsed = self._complete(
                prompt,
                {
                    "name": sample.get("name"),
                    "points": sample.get("points"),
                },
            )
            cards = [
                {"card_id": "overview", "text": parsed.get("overview")},
                {"card_id": "profit_note", "text": parsed.get("profit_note")},
                {"card_id": "limits", "text": parsed.get("limits")},
            ]
            return clamp_cards(cards)
        except (KeyError, TypeError, ValueError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            self.last_error = type(exc).__name__
            return self.fallback.cards(sample, prompt, lang)

    def review_note(self, cards: List[Dict[str, str]], prompt: str, lang: str) -> str:
        if not self.ready():
            return self.fallback.review_note(cards, prompt, lang)
        try:
            parsed = self._complete(prompt, {"cards": cards})
            return clamp_text(parsed.get("note")) or self.fallback.review_note(cards, prompt, lang)
        except (KeyError, TypeError, ValueError, URLError, TimeoutError, json.JSONDecodeError):
            return self.fallback.review_note(cards, prompt, lang)


def build_model() -> ReviewModel:
    settings = model_settings()
    if settings["mode"] == "remote":
        return RemoteReviewModel(settings)
    return LocalTemplateModel()
