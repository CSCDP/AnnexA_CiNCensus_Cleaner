import unittest
from fddc.annex_a.merger.matcher import Matcher


class TestMatcher(unittest.TestCase):

    def test_regex_matcher(self):
        matcher_definition = dict(type="regex", pattern="/[Do]+/i")
        matcher = Matcher(**matcher_definition)
        self.assertTrue(matcher.match("dodo"))
        self.assertFalse(matcher.match("yehaa"))
