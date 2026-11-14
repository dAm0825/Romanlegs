from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request


class ModelUnavailable(RuntimeError):
    pass


class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str, model: str, timeout: int = 45):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def complete_json(self, system: str, user: str, max_tokens: int = 1800) -> dict:
        if not self.enabled:
            raise ModelUnavailable("DeepSeek API key is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
            raise ModelUnavailable(str(exc)) from exc

        try:
            content = body["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ModelUnavailable("DeepSeek returned an unexpected response") from exc

    def complete_with_tools(
        self,
        system: str,
        user: str,
        tools: list[dict],
        max_tokens: int = 800,
    ) -> dict:
        """Ask DeepSeek to choose domain tools through native function calling."""
        if not self.enabled:
            raise ModelUnavailable("DeepSeek API key is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "tools": tools,
            "tool_choice": "auto",
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
            raise ModelUnavailable(str(exc)) from exc

        try:
            message = body["choices"][0]["message"]
            return {
                "content": message.get("content") or "",
                "tool_calls": message.get("tool_calls") or [],
            }
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelUnavailable("DeepSeek returned an unexpected tool response") from exc

