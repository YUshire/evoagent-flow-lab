import json
import unittest

from evoagent.agentic_core import _normalize_final_action


class FinalProtocolTests(unittest.TestCase):
    def test_missing_action_is_only_inferred_from_the_current_final_schema(self):
        payload = {"accepted_finding_indices": [0]}
        result = _normalize_final_action(payload, "lead", json.dumps({"phase": "finalize"}))
        self.assertEqual("final", result["action"])
        self.assertNotIn("action", _normalize_final_action(payload, "lead", '{"phase":"delegate"}'))

    def test_json_object_envelope_preserves_the_explicit_action(self):
        payload = {"type": "json_object", "content": {"action": "final", "findings": []}}
        self.assertEqual({"action": "final", "findings": []}, _normalize_final_action(payload, "security", '{}'))

    def test_tools_and_invalid_explicit_actions_are_never_inferred_or_rewritten(self):
        tool = {"tool": "read_file", "arguments": {"path": "a.py"}}
        self.assertNotIn("action", _normalize_final_action(tool, "security", '{}'))
        invalid = {"action": "execute", "findings": []}
        self.assertEqual("execute", _normalize_final_action(invalid, "security", '{}')["action"])

    def test_final_field_must_be_an_array(self):
        self.assertNotIn("action", _normalize_final_action({"findings": "all safe"}, "security", '{}'))
