import unittest
from fddc.annex_a.merger.matcher import MatcherConfig


class TestMatcher(unittest.TestCase):

    def test_regex_matcher(self):
        matcher = MatcherConfig(type="regex", pattern="/[Do]+/i")
        self.assertTrue(matcher.match("dodo"))
        self.assertFalse(matcher.match("yehaa"))
