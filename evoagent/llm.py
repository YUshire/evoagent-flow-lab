"""Small OpenAI-compatible JSON client with auditable usage accounting."""
import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from .telemetry import ExecutionLedger


class JsonChatClient:
    def __init__(
        self, base_url: str, api_key: str, model: str,
        provider: str = "openai-compatible", timeout: int = 60,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.timeout = timeout
        self.extra_headers = dict(extra_headers or {})

    def complete_json(
        self, role: str, system: str, user: str,
        ledger: Optional[ExecutionLedger] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system + (
                    "\nOutput exactly one JSON object matching the requested protocol. "
                    "Put protocol fields directly at the root. Do not wrap the result "
                    "in a type/content envelope or Markdown, and do not append commentary."
                )},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        if self.provider == "deepseek":
            payload["thinking"] = {"type": "disabled"}
        if max_tokens:
            payload["max_tokens"] = int(max_tokens)
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        headers.update(self.extra_headers)
        request = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers, method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            choice = body["choices"][0]
            if choice.get("finish_reason") == "length":
                raise ValueError("model JSON was truncated by its output token limit")
            content = choice["message"]["content"]
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("model JSON root is not an object")
            if ledger:
                ledger.record_model(
                    role, self.provider, self.model, body.get("usage") or {},
                    int((time.monotonic() - started) * 1000), True,
                )
            return result
        except urllib.error.HTTPError as exc:
            detail = exc.read(1000).decode("utf-8", errors="replace")
            message = "%s API returned HTTP %d: %s" % (
                self.provider, exc.code, detail,
            )
        except (urllib.error.URLError, socket.timeout, ValueError, KeyError,
                IndexError, TypeError, json.JSONDecodeError) as exc:
            message = "%s JSON request failed: %s" % (self.provider, exc)
        if ledger:
            ledger.record_model(
                role, self.provider, self.model, {},
                int((time.monotonic() - started) * 1000), False, message,
            )
        raise RuntimeError(message)
