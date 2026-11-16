from __future__ import annotations

import os
import unittest
from pathlib import Path

from server.analyzer import FraudAnalyzer
from server.assistant import SafetyCopilot
from server.safety import redact_sensitive


ROOT = Path(__file__).resolve().parent.parent


class DetectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["OFFERGUARD_OFFLINE"] = "true"
        cls.analyzer = FraudAnalyzer(ROOT)

    def test_brush_order_is_high_risk(self):
        result = self.analyzer.analyze(
            "招聘点赞员，做任务返佣金。第一单已完成，现在需要垫付980元解冻账户，再共享屏幕处理。"
        )
        self.assertEqual(result["category"], "刷单返利")
        self.assertGreaterEqual(result["score"], 75)
        self.assertTrue(result["critical_actions"])

    def test_authority_impersonation_is_detected(self):
        result = self.analyzer.analyze(
            "这里是公安机关，你名下账户涉嫌诈骗，请立即保密并缴纳取保候审保证金。"
        )
        self.assertEqual(result["category"], "冒充公检法")
        self.assertIn(result["level"], {"高风险", "极高风险"})

    def test_public_news_cases_are_returned(self):
        result = self.analyzer.analyze("演唱会门票私下转让，付款后说账户冻结，让我继续转账。")
        self.assertTrue(result["related_cases"])
        self.assertTrue(all(case["url"].startswith("http") for case in result["related_cases"]))

    def test_sensitive_data_is_redacted(self):
        clean, found = redact_sensitive("电话13800138000，邮箱a@example.com，证件110101200001010012")
        self.assertNotIn("13800138000", clean)
        self.assertNotIn("a@example.com", clean)
        self.assertEqual(sum(item.count for item in found), 3)


class CopilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["OFFERGUARD_OFFLINE"] = "true"
        cls.copilot = SafetyCopilot(ROOT)

    def test_assistant_returns_grounded_answer(self):
        result = self.copilot.assistant("对方让我共享屏幕退款，我该怎么办？", [])
        self.assertIn("停止", result["answer"])
        self.assertTrue(result["evidence"])

    def test_practice_feedback_detects_risky_reply(self):
        result = self.copilot.practice(
            "part-time",
            [{"role": "user", "content": "我把验证码发给你，接下来怎么操作？"}],
        )
        self.assertLess(result["risk_delta"], 0)
        self.assertIn("验证码", result["feedback"] + "验证码")

    def test_practice_recognizes_defensive_reply(self):
        result = self.copilot.practice(
            "part-time",
            [{"role": "user", "content": "我不会垫付，也不会共享屏幕，我会自己向官方核实。"}],
        )
        self.assertGreater(result["risk_delta"], 0)


if __name__ == "__main__":
    unittest.main()

