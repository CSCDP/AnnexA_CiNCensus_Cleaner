#!/usr/bin/env python
import argparse
import logging


from fddc.annex_a.merger.configuration import parse_datasources
from fddc.annex_a.merger import workflow
from fddc.datatables.cache import ExcelFileSource


def main():
    parser = argparse.ArgumentParser(description='Merge and convert Annex A files')

    parser.add_argument('-f', '--input-files', metavar='file', type=str, nargs='+', required=False,
                        help='The filename or pattern to scan')

    parser.add_argument('-o', '--output-file', type=str, default="merged.xlsx", required=False,
                        help='The output of the merge process')

    parser.add_argument('--report-output', type=str, required=False,
                        help='Report on sheet and column matching')

    parser.add_argument('--report-input', type=str, required=False,
                        help='Read mappings from input report')

    parser.add_argument('-m', '--merge', action='count', default=0,
                        help='Perform merge - if not, tool just does the sheet and column matching')

    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Verbose logging')

    parser.add_argument('--config', '-c', type=str, nargs='+', required=False, default=["config/annex-a-merge.yml"],
                        help='Additional config files')

    args = parser.parse_args()

    if args.input_files is None and args.report_input is None:
        raise Exception("One of input_files or report_input must be provided")

    level = logging.DEBUG if args.verbose > 0 else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)-15s [%(module)s] %(message)s')

    data_sources = parse_datasources(*args.config)

    file_source = ExcelFileSource()

    if args.input_files:
        sheet_with_headers = workflow.find_sources(
            args.input_files,
            data_sources=data_sources,
            column_report_filename=args.report_output,
            file_source = file_source
        )
    else:
        sheet_with_headers = workflow.read_sources(
            report = args.report_input,
            data_sources=data_sources,
            column_report_filename=args.report_output,
        )

    if args.merge > 0:
        workflow.merge_dataframes(
            data_sources=data_sources,
            sheet_with_headers=sheet_with_headers,
            output_file=args.output_file,
            file_source=file_source
        )


main()
