import unittest
import os

from fddc.annex_a.merger.workbook_util import WorkSheetDetail
from fddc.datatables import load
from tests.configuration import PROJECT_ROOT


class TestLoad(unittest.TestCase):

    def test_file_source(self):
        src = load.ExcelFileSource()
        file_a = src.get_file(os.path.join(PROJECT_ROOT, "examples/example-B-2004.xlsx"))
        file_b = src.get_file(os.path.join(PROJECT_ROOT, "examples/example-A-2005.xls"))
        file_c = src.get_file(os.path.join(PROJECT_ROOT, "examples/example-B-2004.xlsx"))

        self.assertIs(file_a, file_c)
        self.assertIsNot(file_a, file_b)

    def test_load_single(self):
        file = WorkSheetDetail(os.path.join(PROJECT_ROOT, "examples/example-B-2004.xlsx"), sheetname="List_1")

        df = load.load_dataframe(file)
        self.assertIsNotNone(df)
