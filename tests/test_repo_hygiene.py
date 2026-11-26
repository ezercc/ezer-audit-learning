import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".venv"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".example", ".toml", ""}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*['\"][^'\"]{8,}"),
)


class HygieneTests(unittest.TestCase):
    def test_repo_has_no_secret_shapes_or_large_blobs(self) -> None:
        offenders = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.stat().st_size > 100_000:
                offenders.append(f"large:{path.relative_to(ROOT)}")
                continue
            if path.suffix not in TEXT_SUFFIXES and path.name not in {".env.example", ".gitignore", "LICENSE"}:
                offenders.append(f"unexpected:{path.relative_to(ROOT)}")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    offenders.append(f"secret:{path.relative_to(ROOT)}:{pattern.pattern}")
        self.assertEqual(offenders, [])

    def test_prompts_stay_short_and_generic(self) -> None:
        for path in (ROOT / "prompts").glob("*.txt"):
            text = path.read_text(encoding="utf-8")
            self.assertLessEqual(len(text.splitlines()), 8, path.name)
            self.assertLess(len(text), 400, path.name)


if __name__ == "__main__":
    unittest.main()
