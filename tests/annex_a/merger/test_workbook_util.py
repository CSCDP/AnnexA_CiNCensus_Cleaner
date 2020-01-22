import unittest
import os
from typing import List

from fddc.annex_a.merger.workbook_util import WorkSheetDetail
from tests.configuration import PROJECT_ROOT
from fddc.annex_a.merger import workbook_util, FileSource


class TestWorkbookUtil(unittest.TestCase):

    def test_find_worksheets_xlsx(self):
        source = FileSource(filename=os.path.join(PROJECT_ROOT, "examples/example-01.xlsx"))
        result = workbook_util.find_worksheets(source)
        self.assert_worksheets(result)

    def test_find_worksheets_xls(self):
        source = FileSource(filename=os.path.join(PROJECT_ROOT, "examples/example-01.xls"))
        result = workbook_util.find_worksheets(source)
        self.assert_worksheets(result)

    def assert_worksheets(self, worksheets: List[WorkSheetDetail]):
        self.assertEqual(15, len(worksheets), "Number of sheets found")
        worksheets_by_name = {ws.sheetname: ws for ws in worksheets}

        list_1 = worksheets_by_name['List_1']
        self.assertEqual(2, list_1.header_row_index)
        self.assertEqual(['Child Unique ID',
                          'Gender',
                          'Ethnicity',
                          'Date of Birth',
                          'Age of Child (Years)',
                          'Date of Contact',
                          'Contact Source'],
                         list_1.header_values)
