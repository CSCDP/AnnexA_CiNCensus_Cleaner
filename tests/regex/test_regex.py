import unittest
from fddc.regex import parse_regex, substitute
import re


class TestRegex(unittest.TestCase):

    def test_simple(self):
        p = parse_regex('/test/')
        self.assertEqual(p, re.compile("test"), "Should have no modifiers")
        self.assertIsNotNone(p.match("test"), "Should match test string 'test'")
        self.assertIsNone(p.match("Test"), "Should not match test string 'Test'")

    def test_case_insensitive(self):
        p = parse_regex('/test/i')
        self.assertEqual(p, re.compile("test", re.I), "Should have I modifier")
        self.assertIsNotNone(p.match("test"), "Should match test string 'test'")
        self.assertIsNotNone(p.match("Test"), "Should match test string 'Test'")

    def test_case_insensitive_multiline(self):
        p = parse_regex(r'/test\s+me/im')
        self.assertEqual(p, re.compile(r"test\s+me", re.I | re.M), "Should have I and M modifier")

        test_string = "test\nme"
        self.assertIsNotNone(p.match(test_string), "Should match test string {}".format(test_string))

        test_string = "test\nME"
        self.assertIsNotNone(p.match(test_string), "Should match test string {}".format(test_string))

    def test_alternative_separator(self):
        p = parse_regex('|test|i')
        self.assertEqual(p, re.compile("test", re.I), "Should have I modifier")
        self.assertIsNotNone(p.match("test"), "Should match test string 'test'")
        self.assertIsNotNone(p.match("Test"), "Should match test string 'Test'")


class TestSubstitute(unittest.TestCase):

    def test_simple(self):
        value = substitute(r'/t(es)t/-\1-/', "test", "default")
        self.assertEqual(value, "-es-", "Shold only retain 'es'")


if __name__ == '__main__':
    unittest.main()
