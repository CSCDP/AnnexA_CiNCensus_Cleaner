import logging
from typing import List, Union, Iterable
import pandas as pd

from fddc.annex_a.merger import file_scanner, workbook_util, matcher, matcher_report
from fddc.annex_a.merger.configuration import SourceConfig
from fddc.annex_a.merger.file_scanner import FileSource, ScanSource
from fddc.annex_a.merger.matcher import SheetWithHeaders
from fddc.annex_a.merger.workbook_util import WorkSheetDetail
from fddc.datatables import load, normalise, merge
from fddc.datatables.load import ExcelFileSource


logger = logging.getLogger('fddc.annex_a.merger.workflow')


def __to_scan_source(input_value: Union[str, ScanSource, Iterable]) -> Iterable[ScanSource]:
    if isinstance(input_value, str):
        return [ScanSource(input_value)]
    elif isinstance(input_value, Iterable):
        sources: List[ScanSource] = []
        for i in input_value:
            sources += __to_scan_source(i)
        return sources
    else:
        return [input_value]


def find_sources(
        *args: Union[str, ScanSource, List],
        data_sources: List[SourceConfig],
        column_report_filename: str = None,
        file_source: ExcelFileSource = ExcelFileSource()
) -> List[SheetWithHeaders]:
    """
    Search the filesystem for sources and try to automatically discoverer tables and match columns.

    :param args: Files to scan - can include wildcard characters (glob patterns)
    :param data_sources: Configuration for tables and columns
    :param column_report_filename: Optional generation of a report summarising matches. This can be edited and
                                   fed back into :func:`~fddc.annex_a.merger.read_sources` function.
    :param file_source:
    :return: discovered sources
    """
    input_files = __to_scan_source(args)

    # First we scan the input files section for all inputs
    files: List[FileSource] = []
    for scan_source in input_files:
        files += file_scanner.find_input_files(scan_source)

    logger.info("Found {} candidate input files".format(len(files)))

    # We then scan the input files for data sources
    file_sources: List[WorkSheetDetail] = []
    for file in files:
        file_sources += workbook_util.find_worksheets(file, file_source=file_source)

    logger.info("Found {} candidate data sources".format(len(file_sources)))

    # Match datasources based on configuration
    matched_sheets, unmatched_sheets = matcher.match_data_sources(file_sources, data_sources)

    # Match headers to column configuration
    sheet_with_columns: List[SheetWithHeaders] = matcher.match_columns(matched_sheets)

    # Write column report
    if column_report_filename is not None:
        matcher_report.column_report(sheet_with_columns, unmatched_sheets, column_report_filename)

    return sheet_with_columns


def read_sources(
        report: Union[str, pd.DataFrame],
        data_sources: List[SourceConfig],
        column_report_filename: str = None
) -> List[SheetWithHeaders]:
    """
    Reads configuration report produced by the :func:`~fddc.annex_a.merger.find_sources` function, and converts these
    into a merge configuration

    :param report:
    :param data_sources:
    :param column_report_filename:
    :return:
    """

    records = matcher_report.parse_report(report)
    sheet_with_headers, unmatched_list = matcher_report.process_report(records, data_sources)
    if column_report_filename is not None:
        matcher_report.column_report(sheet_with_headers, unmatched_list, column_report_filename)
    return sheet_with_headers


def merge_dataframes(
        sheet_with_headers: List[SheetWithHeaders],
        data_sources: List[SourceConfig],
        output_file: str = None,
        file_source: ExcelFileSource = ExcelFileSource()
):

    writer = None
    if output_file is not None:
        logger.info("Writing to {}".format(output_file))
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    for data_source_config in data_sources:
        # Filter the source list to give us only sources for this table
        source_list = [s for s in sheet_with_headers if s.sheet.source_config.name == data_source_config.name]
        logger.info(f"Loading {len(source_list)} sources for {data_source_config.name}")

        if len(source_list) == 0:
            # We just create an empty sheet
            df = pd.DataFrame(columns=data_source_config.column_names())
        else:
            data_frames: List[pd.DataFrame] = []
            for source in source_list:
                df = load.load_dataframe(source.sheet.sheet_detail, file_source=file_source)
                df = normalise.normalise_dataframe(df, data_source_config.column_names(), source.column_map())
                df = normalise.clean_datatypes(df, data_source_config.columns)
                df["sort_key"] = source.sheet.sheet_detail.sort_key
                data_frames.append(df)
            df = merge.merge_dataframes(data_frames, data_source_config.columns, sort_key="sort_key")

        if writer is not None:
            df.to_excel(writer, sheet_name=data_source_config.name, index=False)

    if writer is not None:
        writer.save()
        writer.close()
