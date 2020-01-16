import unittest
import os
from fddc.annex_a.merger import find_worksheets

root = os.path.join(os.path.dirname(__file__), "../..")


class TestExcel(unittest.TestCase):

    def test_find_worksheets_xlsx(self):
        result = find_worksheets(filename=os.path.join(root, "examples/example-01.xlsx"))
        self.assertEqual(len(result), 15, "Number of sheets found")

    def test_find_worksheets_xls(self):
        result = find_worksheets(filename=os.path.join(root, "examples/example-01.xls"))
        self.assertEqual(len(result), 15, "Number of sheets found")
