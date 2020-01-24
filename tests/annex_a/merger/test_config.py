import unittest
from dacite import from_dict
from fddc.annex_a.merger.configuration import ColumnConfig, RegexMatcherConfig, SourceConfig


class TestConfiguration(unittest.TestCase):

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

