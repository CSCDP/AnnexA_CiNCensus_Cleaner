import unittest
from fddc.annex_a.merger.configuration import ColumnConfig, RegexMatcherConfig, MatcherConfig
from fddc.annex_a.merger import configuration


class TestConfiguration(unittest.TestCase):

    def test_regex_matcher(self):
        matcher = MatcherConfig(type="regex", pattern="/[Do]+/i")
        self.assertTrue(matcher.match("dodo"))
        self.assertFalse(matcher.match("yehaa"))

    def test_column_config_name_only(self):
        cfg = ColumnConfig(name='List 1')
        self.assertEqual(cfg.matchers, [RegexMatcherConfig(pattern=r'/.*List\s+1.*/i')])
        self.assertTrue(cfg.matchers[0].match('   List    1   '))

    def test_column_config_regex_str(self):
        cfg = ColumnConfig(name='List 1', regex=r'/.*/')
        self.assertEqual(cfg.matchers, [RegexMatcherConfig(pattern=r'/.*/')])
        self.assertTrue(cfg.matchers[0].match(' Anything! '))

    def test_column_config_regex_list(self):
        cfg = ColumnConfig(name='List 1', regex=[r'/1/', r'/2/'])
        self.assertEqual(cfg.matchers, [
            RegexMatcherConfig(pattern=r'/1/'),
            RegexMatcherConfig(pattern=r'/2/'),
        ])
        self.assertTrue(cfg.matchers[0].match('1'))
        self.assertFalse(cfg.matchers[0].match('2'))
        self.assertTrue(cfg.matchers[1].match('2'))

    def test_column_config_spaces(self):
        cfg = ColumnConfig(name='List 1')
        self.assertTrue(cfg.matchers[0].match('   List    1   '))

        cfg = ColumnConfig(name='List      2')
        self.assertTrue(cfg.matchers[0].match('List 2'))

        cfg = ColumnConfig(name='List 3')
        self.assertFalse(cfg.matchers[0].match('List3'))

        cfg = ColumnConfig(name='List4')
        self.assertFalse(cfg.matchers[0].match('List 4'))

    def test_column_config_brackets(self):
        cfg = ColumnConfig(name='This (and) that')
        self.assertTrue(cfg.matchers[0].match('this (and) that'))

        cfg = ColumnConfig(name=r'This \(and\) that')
        self.assertTrue(cfg.matchers[0].match(r'this \(and\) that'))

    def test_column_config_not_very_smart_quotes(self):
        matcher = configuration._parse_regex(None, 'This "and" that')[0]
        self.assertEqual(r"/.*This\s+.?and.?\s+that.*/i", matcher.pattern)
        self.assertTrue(matcher.match('This "and" that'))
        self.assertTrue(matcher.match('This “and” that'))

        matcher = configuration._parse_regex(None, "I 'like' that!")[0]
        self.assertTrue(matcher.match("I 'like' that!"))
        self.assertTrue(matcher.match("I ‘like’ that!"))

