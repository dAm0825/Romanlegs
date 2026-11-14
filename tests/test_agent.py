from __future__ import annotations

import os
import json
import subprocess
import unittest
from pathlib import Path

from server.agent import ContractAgent
from server.safety import redact_pii


ROOT = Path(__file__).resolve().parent.parent


class RedactionTests(unittest.TestCase):
    def test_common_identifiers_are_removed(self):
        clean, redactions = redact_pii(
            "电话 13800138000，邮箱 student@example.com，身份证 110101200001010012"
        )
        self.assertNotIn("13800138000", clean)
        self.assertNotIn("student@example.com", clean)
        self.assertNotIn("110101200001010012", clean)
        self.assertEqual(sum(item.count for item in redactions), 3)


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["OFFERGUARD_OFFLINE"] = "true"
        cls.agent = ContractAgent(ROOT)
        cls.contract = (ROOT / "data" / "demo_contract.txt").read_text(encoding="utf-8")

    def test_demo_contract_has_high_risk_findings(self):
        result = self.agent.analyze(self.contract)
        finding_ids = {finding["id"] for finding in result["findings"]}
        self.assertIn("probation-duration", finding_ids)
        self.assertIn("late-social-insurance", finding_ids)
        self.assertIn("unpaid-overtime", finding_ids)
        self.assertGreaterEqual(result["score"], 65)
        self.assertEqual(result["level"], "高风险")

    def test_every_finding_quote_is_in_original(self):
        result = self.agent.analyze(self.contract)
        for finding in result["findings"]:
            self.assertIn(finding["quote"], self.contract)

    def test_citations_are_retrieved_evidence(self):
        result = self.agent.analyze(self.contract)
        evidence_ids = {evidence["id"] for evidence in result["evidence"]}
        for finding in result["findings"]:
            self.assertTrue(finding["citations"])
            self.assertTrue(set(finding["citations"]).issubset(evidence_ids))

    def test_agent_trace_is_complete(self):
        result = self.agent.analyze(self.contract)
        step_names = [step["name"] for step in result["agent"]["steps"]]
        self.assertEqual(
            step_names,
            [
                "pii_shield",
                "clause_scout",
                "policy_rag",
                "risk_engine",
                "action_planner",
                "safety_reviewer",
            ],
        )

    def test_short_input_is_rejected(self):
        with self.assertRaises(ValueError):
            self.agent.analyze("太短")


class MCPTests(unittest.TestCase):
    def test_mcp_server_lists_policy_tools(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]
        process = subprocess.run(
            [os.sys.executable, str(ROOT / "server" / "mcp_server.py")],
            input="\n".join(json.dumps(item) for item in messages) + "\n",
            text=True,
            capture_output=True,
            check=True,
            env={**os.environ, "OFFERGUARD_OFFLINE": "true"},
        )
        replies = [json.loads(line) for line in process.stdout.splitlines()]
        tool_names = {tool["name"] for tool in replies[1]["result"]["tools"]}
        self.assertIn("search_policy", tool_names)
        self.assertIn("calculate_risk", tool_names)


if __name__ == "__main__":
    unittest.main()

