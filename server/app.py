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
    from server.analyzer import FraudAnalyzer
    from server.assistant import SafetyCopilot
    from server.config import ROOT, get_config
    from server.safety import sanitize_chat_history
else:
    from .analyzer import FraudAnalyzer
    from .assistant import SafetyCopilot
    from .config import ROOT, get_config
    from .safety import sanitize_chat_history


APP_DIR = ROOT / "app"
ANALYZER = FraudAnalyzer(ROOT)
COPILOT = SafetyCopilot(ROOT)


class MingBianHandler(SimpleHTTPRequestHandler):
    server_version = "MingBian/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[mingbian] {self.address_string()} - {fmt % args}")

    def _json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("请求长度无效") from exc
        if size <= 0 or size > 100_000:
            raise ValueError("请求内容为空或过大")
        try:
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("请求不是有效 JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("请求格式不正确")
        return payload

    def do_GET(self) -> None:
        path = unquote(urlparse(self.path).path)
        if path == "/api/health":
            self._json(
                {
                    "status": "ok",
                    "model_configured": ANALYZER.model_enabled,
                    "knowledge_count": len(ANALYZER.rag.documents),
                    "case_count": len(ANALYZER.rag.cases),
                }
            )
            return
        if path == "/api/news":
            self._json({"cases": ANALYZER.rag.cases})
            return
        if path == "/api/scenarios":
            from server.assistant import SCENARIOS

            self._json({"scenarios": [{"id": key, **value} for key, value in SCENARIOS.items()]})
            return

        requested = (APP_DIR / path.lstrip("/")).resolve()
        if path == "/" or path.startswith("/") and not Path(path).suffix:
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
        try:
            payload = self._body()
            if path == "/api/detect":
                self._json(ANALYZER.analyze(str(payload.get("message", ""))))
            elif path == "/api/assistant":
                self._json(
                    COPILOT.assistant(
                        str(payload.get("question", "")),
                        sanitize_chat_history(payload.get("history", [])),
                    )
                )
            elif path == "/api/practice":
                self._json(
                    COPILOT.practice(
                        str(payload.get("scenario_id", "")),
                        sanitize_chat_history(payload.get("history", [])),
                    )
                )
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self.log_error("request failed: %s", exc)
            self._json({"error": "服务暂时不可用，请稍后重试"}, HTTPStatus.INTERNAL_SERVER_ERROR)


def main() -> None:
    config = get_config()
    server = ThreadingHTTPServer(("127.0.0.1", int(config["port"])), MingBianHandler)
    print(f"MingBian running at http://127.0.0.1:{config['port']}")
    print(f"AI provider: {'DeepSeek' if ANALYZER.model_enabled else 'local fallback'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping MingBian")
        server.server_close()


if __name__ == "__main__":
    main()

