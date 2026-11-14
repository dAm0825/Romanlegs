"""Minimal stdio MCP server exposing OfferGuard's evidence tools.

Example client configuration:

  {
    "mcpServers": {
      "offerguard-policy": {
        "command": "python3",
        "args": ["server/mcp_server.py"]
      }
    }
  }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from server.agent import ContractAgent, _extract_findings
    from server.safety import normalise_text
else:
    from .agent import ContractAgent, _extract_findings
    from .safety import normalise_text


AGENT = ContractAgent()

TOOLS = [
    {
        "name": "search_policy",
        "description": "检索 OfferGuard 可信劳动法规知识库。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "categories": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["query"],
        },
    },
    {
        "name": "calculate_risk",
        "description": "识别合同风险并计算可解释风险指数。",
        "inputSchema": {
            "type": "object",
            "properties": {"contract_text": {"type": "string"}},
            "required": ["contract_text"],
        },
    },
    {
        "name": "build_evidence_checklist",
        "description": "根据合同生成书面澄清和证据留存清单。",
        "inputSchema": {
            "type": "object",
            "properties": {"contract_text": {"type": "string"}},
            "required": ["contract_text"],
        },
    },
]


def text_result(payload: object, is_error: bool = False) -> dict:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ],
        "isError": is_error,
    }


def call_tool(name: str, arguments: dict) -> dict:
    if name == "search_policy":
        query = normalise_text(str(arguments.get("query", "")))
        categories = [item for item in arguments.get("categories", []) if isinstance(item, str)]
        if not query:
            return text_result({"error": "query is required"}, True)
        evidence = AGENT.rag.search(query, categories, limit=6)
        return text_result({"query": query, "evidence": evidence})

    if name in {"calculate_risk", "build_evidence_checklist"}:
        contract_text = str(arguments.get("contract_text", ""))
        findings = _extract_findings(normalise_text(contract_text))
        if not findings:
            return text_result({"findings": [], "message": "未检测到规则库中的风险主题"})
        if name == "calculate_risk":
            return text_result(
                {
                    "findings": findings,
                    "risk": ContractAgent._execute_risk(findings),
                }
            )
        return text_result(
            {
                "checklist": ContractAgent._execute_checklist(findings),
                "safety": ContractAgent._execute_safety(findings),
            }
        )

    return text_result({"error": f"Unknown tool: {name}"}, True)


def respond(request_id: object, result: object = None, error: dict | None = None) -> None:
    payload = {"jsonrpc": "2.0", "id": request_id}
    if error:
        payload["error"] = error
    else:
        payload["result"] = result
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            respond(None, error={"code": -32700, "message": "Parse error"})
            continue

        method = message.get("method")
        request_id = message.get("id")
        if method == "initialize":
            respond(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "offerguard-policy", "version": "1.0.0"},
                },
            )
        elif method == "tools/list":
            respond(request_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = message.get("params", {})
            respond(request_id, call_tool(params.get("name", ""), params.get("arguments", {})))
        elif method.startswith("notifications/"):
            continue
        else:
            respond(
                request_id,
                error={"code": -32601, "message": f"Method not found: {method}"},
            )


if __name__ == "__main__":
    main()

