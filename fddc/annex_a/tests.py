import unittest
import os
from fddc.annex_a import merger

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class TestExcel(unittest.TestCase):

    def test_find_input_files_empty(self):
        result = merger.find_input_files(root, "*.xlsx")
        self.assertEqual(result, [])

    def test_find_input_files_deep(self):
        result = merger.find_input_files(root, "**/*.xlsx")
        self.assertEqual(len(result), 1)

        file  = result[0]
        self.assertEqual(root, file["root"])
        self.assertEqual('examples/example-01.xlsx', file["sort_key"])
        self.assertEqual('examples/example-01.xlsx', file["sourcename"])

    def test_find_input_files_multiext(self):
        result = merger.find_input_files(root, "**/*.xls*")
        self.assertEqual(2, len(result))

    def test_find_input_files_sortkeys(self):
        result = merger.find_input_files(root, "**/*.xls*", sort_keys=[r'/.*?(\d+).*/\1/i'])
        file  = result[0]
        self.assertEqual('01', file["sort_key"])

    def test_find_worksheets_xlsx(self):
        result = merger.find_worksheets(filename=os.path.join(root, "examples/example-01.xlsx"))
        self.assert_worksheets(result)

    def test_find_worksheets_xls(self):
        result = merger.find_worksheets(filename=os.path.join(root, "examples/example-01.xls"))
        self.assert_worksheets(result)

    def assert_worksheets(self, worksheets):
        self.assertEqual(15, len(worksheets), "Number of sheets found")
        worksheets_by_name = {ws['sheetname']: ws for ws in worksheets}

        list_1 = worksheets_by_name['List_1']
        self.assertEqual(2, list_1['header_row_index'])
        self.assertEqual(['Child Unique ID',
                          'Gender',
                          'Ethnicity',
                          'Date of Birth',
                          'Age of Child (Years)',
                          'Date of Contact',
                          'Contact Source'],
                         list_1['header_values'])
