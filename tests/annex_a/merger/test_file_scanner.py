import os
import unittest

from fddc.annex_a.merger.file_scanner import ScanSource
from tests.configuration import PROJECT_ROOT
from fddc.annex_a.merger import file_scanner


class TestFileScanner(unittest.TestCase):

    def test_find_input_files_empty(self):
        result = file_scanner.find_input_files(ScanSource(root=PROJECT_ROOT, include="*.xlsx"))
        self.assertEqual(result, [])

    def test_find_input_files_deep(self):
        result = file_scanner.find_input_files(ScanSource(root=PROJECT_ROOT, include="**/ex*.xlsx"))
        self.assertEqual(len(result), 1)

        filesource  = result[0]
        self.assertEqual(PROJECT_ROOT, filesource.root)
        self.assertEqual('examples/example-01.xlsx', filesource.sort_key)
        self.assertEqual('examples/example-01.xlsx', filesource.sourcename)

    def test_find_input_files_multiext(self):
        result = file_scanner.find_input_files(ScanSource(include=os.path.join(PROJECT_ROOT, "**/ex*.xls*")))
        self.assertEqual(2, len(result))

    def test_find_input_files_sortkeys(self):
        result = file_scanner.find_input_files(ScanSource(
            root=PROJECT_ROOT,
            include="**/ex*.xls*",
            sort_keys=[r'/.*?(\d+).*/\1/i'])
        )
        filesource  = result[0]
        self.assertEqual('01', filesource.sort_key)