import unittest
from tests.configuration import PROJECT_ROOT
from fddc.annex_a.merger import file_scanner


class TestFileScanner(unittest.TestCase):

    def test_find_input_files_empty(self):
        result = file_scanner.find_input_files(PROJECT_ROOT, "*.xlsx")
        self.assertEqual(result, [])

    def test_find_input_files_deep(self):
        result = file_scanner.find_input_files(PROJECT_ROOT, "**/*.xlsx")
        self.assertEqual(len(result), 1)

        file  = result[0]
        self.assertEqual(PROJECT_ROOT, file["root"])
        self.assertEqual('examples/example-01.xlsx', file["sort_key"])
        self.assertEqual('examples/example-01.xlsx', file["sourcename"])

    def test_find_input_files_multiext(self):
        result = file_scanner.find_input_files(PROJECT_ROOT, "**/*.xls*")
        self.assertEqual(2, len(result))

    def test_find_input_files_sortkeys(self):
        result = file_scanner.find_input_files(PROJECT_ROOT, "**/*.xls*", sort_keys=[r'/.*?(\d+).*/\1/i'])
        file  = result[0]
        self.assertEqual('01', file["sort_key"])