import json
import unittest
from unittest.mock import patch

from evoagent.llm import JsonChatClient


class Response:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.value).encode()


class JsonClientTests(unittest.TestCase):
    def test_deepseek_json_transport_disables_thinking_and_keeps_protocol_at_root(self):
        response = {"choices": [{"finish_reason": "stop", "message": {
            "content": '{"action":"final","findings":[]}',
        }}]}
        with patch("evoagent.llm.urllib.request.urlopen", return_value=Response(response)) as request:
            result = JsonChatClient("https://api.deepseek.com", "test-only", "test-model", "deepseek").complete_json(
                "security", "Return JSON with action and findings.", "synthetic diff", max_tokens=1000,
            )
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual({"type": "disabled"}, payload["thinking"])
        self.assertEqual({"type": "json_object"}, payload["response_format"])
        self.assertEqual("final", result["action"])
        self.assertIn("directly at the root", payload["messages"][0]["content"])

    def test_truncated_output_is_rejected_even_when_partial_content_parses(self):
        response = {"choices": [{"finish_reason": "length", "message": {"content": '{}'}}]}
        with patch("evoagent.llm.urllib.request.urlopen", return_value=Response(response)):
            with self.assertRaisesRegex(RuntimeError, "truncated"):
                JsonChatClient("https://example.invalid", "test-only", "test-model").complete_json(
                    "lead", "Return JSON", "synthetic diff",
                )

    def test_custom_provider_does_not_receive_deepseek_specific_parameters(self):
        response = {"choices": [{"message": {"content": '{"action":"final"}'}}]}
        with patch("evoagent.llm.urllib.request.urlopen", return_value=Response(response)) as request:
            JsonChatClient("https://example.invalid", "test-only", "test-model", "custom").complete_json(
                "lead", "Return JSON", "synthetic diff",
            )
        self.assertNotIn("thinking", json.loads(request.call_args.args[0].data))
