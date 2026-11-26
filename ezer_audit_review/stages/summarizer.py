"""交付摘要。只复述样例已完成，不提升结论强度。"""

from __future__ import annotations


def summarize(name: str, lang: str) -> str:
    if lang == "en":
        return f"{name} review sample finished with warnings."
    return f"{name}审阅样例已完成，结论带有限制。"
