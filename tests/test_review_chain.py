import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from ezer_audit_review.clamp import clamp_cards, clamp_points, clamp_status
from ezer_audit_review.config import CARD_IDS, HISTORY_LIMIT
from ezer_audit_review.models import RemoteReviewModel
from ezer_audit_review.pipeline import run_chain
from ezer_audit_review.server import serve

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = {"code": "000000.SZ", "year": 2024, "period": "FY", "lang": "zh-CN"}


class ChainTests(unittest.TestCase):
    def test_sample_finishes_with_warnings_only(self) -> None:
        result = run_chain(SAMPLE)
        self.assertEqual(result["final_status"], "PASS_WITH_WARNINGS")
        self.assertNotIn("TRUSTED", json.dumps(result))
        self.assertEqual([card["card_id"] for card in result["cards"]], list(CARD_IDS))
        self.assertLessEqual(result["meta"]["history_count"], HISTORY_LIMIT)
        self.assertFalse(result["meta"]["allows_trusted"])
        self.assertFalse(result["meta"]["live_data"])
        skipped = [event["data"]["stage"] for event in result["events"] if event["event"] == "skipped"]
        self.assertEqual(skipped, ["I", "O", "supplement", "provider_fallback"])
        self.assertEqual(result["meta"]["state_path"][-1], "DELIVERED")
        self.assertFalse(any(event["data"].get("executed") for event in result["events"] if event["event"] == "q_query"))

    def test_unknown_code_does_not_fetch_live_data(self) -> None:
        result = run_chain({**SAMPLE, "code": "999999.SZ"})
        self.assertEqual(result["final_status"], "NO_VALID_CONCLUSION")
        self.assertIn("FAILED", result["meta"]["state_path"])
        self.assertEqual(result["cards"], [])

    def test_period_mismatch_is_not_backfilled(self) -> None:
        result = run_chain({**SAMPLE, "period": "Q1"})
        self.assertEqual(result["final_status"], "NO_VALID_CONCLUSION")

    def test_english_sample_stays_short(self) -> None:
        result = run_chain({**SAMPLE, "lang": "en"})
        self.assertTrue(all(len(card["text"]) <= 60 for card in result["cards"]))
        self.assertIn("warnings", result["summary"])

    def test_unconfigured_remote_falls_back_without_retry(self) -> None:
        model = RemoteReviewModel({"mode": "remote", "base_url": "", "api_key": "", "model_name": "review-small"})
        result = run_chain(SAMPLE, model=model)
        self.assertEqual(result["final_status"], "PASS_WITH_WARNINGS")
        self.assertEqual(model.last_error, "remote_not_configured")
        self.assertEqual(result["meta"]["model_mode"], "remote-clamped")

    def test_clamp_rejects_rich_model_output(self) -> None:
        points = clamp_points([{"label": str(i), "revenue": i, "net_profit": i, "cash": 99} for i in range(8)])
        self.assertEqual(len(points), HISTORY_LIMIT)
        self.assertNotIn("cash", points[0])
        cards = clamp_cards(
            [{"card_id": card_id, "text": "超长" * 80} for card_id in ("overview", "profit_note", "limits", "extra")]
        )
        self.assertEqual(len(cards), 3)
        self.assertTrue(all(len(card["text"]) <= 60 for card in cards))
        self.assertEqual(clamp_status("TRUSTED", cards, points), "PASS_WITH_WARNINGS")
        self.assertEqual(clamp_status("PASS_WITH_WARNINGS", [{"card_id": "overview", "text": ""}], points), "NO_VALID_CONCLUSION")


class ServerTests(unittest.TestCase):
    def test_loopback_review_endpoint(self) -> None:
        old = os.environ.pop("REVIEW_DEMO_TOKEN", None)
        httpd = serve(port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            port = httpd.server_address[1]
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/v1/review",
                data=json.dumps(SAMPLE).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(payload["final_status"], "PASS_WITH_WARNINGS")
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)
            if old is not None:
                os.environ["REVIEW_DEMO_TOKEN"] = old

    def test_demo_token_is_required_when_set(self) -> None:
        os.environ["REVIEW_DEMO_TOKEN"] = "review-demo"
        httpd = serve(port=0)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            port = httpd.server_address[1]
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/v1/review",
                data=json.dumps(SAMPLE).encode("utf-8"),
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(request, timeout=5)
            self.assertEqual(caught.exception.code, 401)
            caught.exception.close()
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)
            os.environ.pop("REVIEW_DEMO_TOKEN", None)


if __name__ == "__main__":
    unittest.main()
