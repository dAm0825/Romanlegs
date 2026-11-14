from __future__ import annotations

import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from server.agent import ContractAgent
    from server.config import ROOT, get_config
else:
    from .agent import ContractAgent
    from .config import ROOT, get_config


APP_DIR = ROOT / "app"
AGENT = ContractAgent(ROOT)


class OfferGuardHandler(SimpleHTTPRequestHandler):
    server_version = "OfferGuard/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def log_message(self, format: str, *args) -> None:
        print(f"[offer-guard] {self.address_string()} - {format % args}")

    def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = unquote(urlparse(self.path).path)
        if path == "/api/health":
            self._send_json(
                {
                    "status": "ok",
                    "model_configured": AGENT.model_enabled,
                    "knowledge_documents": len(AGENT.rag.documents),
                }
            )
            return
        if path == "/api/demo-contract":
            demo = (ROOT / "data" / "demo_contract.txt").read_text(encoding="utf-8")
            self._send_json({"text": demo})
            return

        requested = (APP_DIR / path.lstrip("/")).resolve()
        if path == "/":
            requested = APP_DIR / "index.html"
        if APP_DIR not in requested.parents and requested != APP_DIR:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not requested.exists() or requested.is_dir():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content = requested.read_bytes()
        content_type, _ = mimetypes.guess_type(str(requested))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/analyze":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "请求长度无效"}, HTTPStatus.BAD_REQUEST)
            return
        if content_length <= 0 or content_length > 120_000:
            self._send_json({"error": "请求内容为空或超过大小限制"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            result = AGENT.analyze(payload.get("contract_text", ""))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "请求不是有效的 JSON"}, HTTPStatus.BAD_REQUEST)
            return
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            self.log_error("analysis failed: %s", exc)
            self._send_json({"error": "分析暂时失败，请稍后重试"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_json(result)


def main() -> None:
    config = get_config()
    server = ThreadingHTTPServer(("127.0.0.1", int(config["port"])), OfferGuardHandler)
    provider = f"DeepSeek ({config['model']})" if AGENT.model_enabled else "local fallback"
    print(f"OfferGuard running at http://127.0.0.1:{config['port']}")
    print(f"AI provider: {provider}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping OfferGuard")
        server.server_close()


if __name__ == "__main__":
    main()

