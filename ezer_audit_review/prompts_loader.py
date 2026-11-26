"""读取审阅版短提示词。提示词不参与生产质量路径。"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    text = path.read_text(encoding="utf-8").strip()
    if len(text) > 400:
        raise ValueError(f"review prompt too long: {name}")
    return text


def prompt_profile(lang: str) -> Dict[str, str]:
    b_name = "b_en.txt" if lang == "en" else "b_zh.txt"
    c_name = "c_en.txt" if lang == "en" else "c_zh.txt"
    loaded = {
        "q": load_prompt("q.txt"),
        "b": load_prompt(b_name),
        "c": load_prompt(c_name),
    }
    digest = hashlib.sha256("\n".join(loaded.values()).encode("utf-8")).hexdigest()[:12]
    return {
        "q": loaded["q"],
        "b": loaded["b"],
        "c": loaded["c"],
        "id": f"review-short-{digest}",
        "effect": "clamped",
    }
