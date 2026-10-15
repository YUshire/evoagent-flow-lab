import unittest
from fixtures.request_handler import parse_request_value

class SecurityRegressionTests(unittest.TestCase):
    def test_python_expression_rejected(self):
        with self.assertRaises(ValueError): parse_request_value('1+1')
    def test_json_true(self): self.assertIs(parse_request_value('true'), True)
    def test_json_null(self): self.assertIsNone(parse_request_value('null'))
    def test_malformed_json_rejected(self):
        with self.assertRaises(ValueError): parse_request_value('{')
