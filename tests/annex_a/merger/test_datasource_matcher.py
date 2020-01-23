import unittest

from fddc.annex_a.merger import WorkSheetDetail
from fddc.annex_a.merger.datasource_matcher import match_data_sources
from fddc.annex_a.merger.configuration import SheetConfig


class TestMatcher(unittest.TestCase):

    def test_datasource_matcher(self):
        worksheets = [
            WorkSheetDetail(filename="File 1", sheetname="List 1"),
            WorkSheetDetail(filename="File 2", sheetname="List 2"),
        ]
        config = {
            "list1": SheetConfig(name="list 1"),
            "list3": SheetConfig(name="list 3")
        }
        matched, unmatched = match_data_sources(worksheets, config)
        self.assertEqual(matched, worksheets[0:1])