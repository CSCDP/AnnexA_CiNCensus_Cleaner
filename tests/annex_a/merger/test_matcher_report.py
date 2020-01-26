import os
import unittest
import fddc.annex_a.merger.matcher_report
from fddc.annex_a.merger import matcher_report, configuration
from tests.configuration import PROJECT_ROOT


class TestMatcherReport(unittest.TestCase):

    def test_parse_and_process(self):
        """
        This is not a unit test - it tests the integration of multiple components
        """
        records = matcher_report.parse_report(os.path.join(PROJECT_ROOT, "examples/matcher-report/report.xlsx"))
        data_sources = configuration.parse_datasources(os.path.join(PROJECT_ROOT, "config/annex-a-merge.yml"))

        sheet_with_headers, unmatched_list = matcher_report.process_report(records, data_sources)

        fddc.annex_a.merger.matcher_report.column_report(sheet_with_headers, unmatched_list, "test-report.xlsx")
