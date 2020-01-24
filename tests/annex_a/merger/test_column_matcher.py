import unittest
from dacite import from_dict
import yaml
from fddc.annex_a.merger import column_matcher
from fddc.annex_a.merger.datasource_matcher import MatchedSheet
from fddc.annex_a.merger.matcher import RegexMatcherConfig
from fddc.annex_a.merger.workbook_util import WorkSheetHeaderItem


class TestConfiguration(unittest.TestCase):

    def test_match_header(self):
        header_list = [
            WorkSheetHeaderItem(value="Test", column_index=0),
            WorkSheetHeaderItem(value="Dummy", column_index=1),
            WorkSheetHeaderItem(value="Header 1", column_index=2),
            WorkSheetHeaderItem(value="Header 2", column_index=3),
        ]

        matcher_list = [
            RegexMatcherConfig('/Header 1/i'),
            RegexMatcherConfig('/Header X/i')
        ]

        result = column_matcher._match_header(header_list, matcher_list)
        self.assertEqual(result, header_list[2])

    def test_match_single_column(self):
        sheet = """
source_config:
    name: Test Source
    columns:
        - name: Header 1
        - name: Header X
        - name: Header Y
sheet_detail:
    filename: Test Name
    header_values:
        - value: Header T
          column_index: 0
        - value: Header   X
          column_index: 1
        - value: Header 1
          column_index: 2
"""
        sheet = from_dict(data_class=MatchedSheet, data=yaml.safe_load(sheet))

        result_sheet_list = column_matcher.match_columns(sheet)

        self.assertEqual(len(result_sheet_list), 1)

        result_sheet = result_sheet_list[0]

        self.assertEqual(result_sheet.sheet, sheet)
        self.assertEqual(len(result_sheet.columns), 2)
        self.assertEqual(result_sheet.columns[0].header.column_index, 2)
        self.assertEqual(result_sheet.columns[1].header.column_index, 1)

