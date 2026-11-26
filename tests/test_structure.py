import json
import os
import threading
import unittest
import urllib.request
from pathlib import Path

from ezer_audit_review.contracts.state import StateMachine
from ezer_audit_review.pipeline import run_chain
from ezer_audit_review.profile_lock import COMMERCIAL_SWITCHES
from ezer_audit_review.server import serve

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = {"code": "000000.SZ", "year": 2024, "period": "FY", "lang": "zh-CN"}


class StructureTests(unittest.TestCase):
    def test_success_path_visits_every_review_stage(self) -> None:
        result = run_chain(SAMPLE)
        self.assertEqual(
            result["meta"]["state_path"],
            [
                "INIT",
                "RESOLVED",
                "FETCHED",
                "PLANNED",
                "ANALYZED",
                "GATED",
                "INDUSTRY",
                "OUTLOOK",
                "REVIEWED",
                "SUMMARIZED",
                "DELIVERED",
            ],
        )
        self.assertEqual(result["industry"]["topics"], [])
        self.assertEqual(result["outlook"]["statements"], [])
        self.assertFalse(result["meta"]["commercial"])

    def test_commercial_switch_fails_closed(self) -> None:
        name = COMMERCIAL_SWITCHES[0]
        os.environ[name] = "1"
        try:
            result = run_chain(SAMPLE)
        finally:
            os.environ.pop(name, None)
        self.assertEqual(result["final_status"], "NO_VALID_CONCLUSION")
        self.assertEqual(result["meta"]["state_path"], ["INIT", "FAILED"])
        self.assertEqual(result["meta"]["rejected_switches"], [name])
        self.assertEqual(result["cards"], [])

    def test_illegal_transition_is_rejected(self) -> None:
        machine = StateMachine()
        with self.assertRaises(RuntimeError):
            machine.move("DELIVERED")

    def test_degraded_stages_do_not_open_network_clients(self) -> None:
        for name in ("industry.py", "outlook.py", "fetcher.py", "planner.py"):
            text = (ROOT / "ezer_audit_review" / "stages" / name).read_text(encoding="utf-8")
            self.assertNotIn("urllib", text)
            self.assertNotIn("socket", text)

    def test_manifest_lists_stages_without_commercial_flag(self) -> None:
        httpd = serve(port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            port = httpd.server_address[1]
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/manifest", timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertFalse(payload["commercial"])
            self.assertGreaterEqual(len(payload["stages"]), 10)
            self.assertTrue(all(item["commercial"] is False for item in payload["stages"]))
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
