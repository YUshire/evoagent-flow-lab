import unittest
from fixtures.app import parse_value

class ParsingTests(unittest.TestCase):
    def test_integer(self): self.assertEqual(parse_value("42"), 42)
    def test_list(self): self.assertEqual(parse_value("[1, 2]"), [1, 2])
    def test_string(self): self.assertEqual(parse_value('"hello"'), "hello")
