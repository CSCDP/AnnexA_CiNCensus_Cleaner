import os
import unittest
from fddc.annex_a.merger.file_scanner import ScanSource
from tests.configuration import PROJECT_ROOT
from fddc.annex_a.merger import file_scanner


class TestFileScanner(unittest.TestCase):

    def test_find_input_files_empty(self):
        result = file_scanner.find_input_files(ScanSource(include=os.path.join(PROJECT_ROOT,
                                                                               "oh-no-I-do-not-exist.xlsx")))
        self.assertEqual(result, [])

    def test_find_input_files_deep(self):
        result = file_scanner.find_input_files(ScanSource(include=os.path.join(PROJECT_ROOT, "**/ex*.xlsx")))
        self.assertEqual(len(result), 1)

        filesource = result[0]
        self.assertEqual('mples/example-B-2004.xlsx', filesource.filename[-25:])

    def test_find_input_files_multiext(self):
        result = file_scanner.find_input_files(ScanSource(include=os.path.join(PROJECT_ROOT, "**/ex*.xls*")))
        self.assertEqual(2, len(result))

    def test_find_input_files_sortkeys(self):
        result = file_scanner.find_input_files(ScanSource(
            include=os.path.join(PROJECT_ROOT, "**/ex*.xls*"),
            sort_keys=[r'/.*?(\d+).*/\1/i'])
        )
        sort_keys = {r.sort_key for r in result}
        self.assertSetEqual({'2004', '2005'}, sort_keys)
