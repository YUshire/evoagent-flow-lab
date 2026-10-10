import unittest
from fixtures.request_handler import parse_request_value

class RequestParsingTests(unittest.TestCase):
    def test_integer(self): self.assertEqual(parse_request_value("42"), 42)
    def test_list(self): self.assertEqual(parse_request_value("[1, 2]"), [1, 2])
    def test_string(self): self.assertEqual(parse_request_value('"hello"'), "hello")
