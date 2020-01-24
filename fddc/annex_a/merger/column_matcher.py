import copy
from dataclasses import dataclass
from typing import List, Union, Any, Dict

import pandas as pd

from fddc.annex_a.merger.configuration import ColumnConfig
from fddc.annex_a.merger.datasource_matcher import MatchedSheet
from fddc.annex_a.merger.matcher import MatcherConfig
from fddc.annex_a.merger.workbook_util import WorkSheetHeaderItem, WorkSheetDetail


@dataclass
class MatchedColumn:
    column: ColumnConfig
    header: WorkSheetHeaderItem


@dataclass
class SheetWithHeaders:
    sheet: MatchedSheet
    columns: List[MatchedColumn]
    unmatched_columns: List[ColumnConfig]

    def unmatched_headers(self):
        unmatched_headers: List[WorkSheetHeaderItem] = []
        matched_columns_by_index = {col.header.column_index: col for col in self.columns}

        for header in self.sheet.sheet_detail.headers:
            if header.column_index not in matched_columns_by_index:
                unmatched_headers.append(header)

        return unmatched_headers


def _match_header(header_list: List[WorkSheetHeaderItem], matcher_list: List[MatcherConfig]) -> WorkSheetHeaderItem:
    for matcher in matcher_list:
        for header in header_list:
            if matcher.match(header.value):
                return header


def match_columns(matched_sheet: Union[MatchedSheet, List[MatchedSheet]]) -> List[SheetWithHeaders]:
    # First we check if we were passed a list, in which case we iterate
    if not isinstance(matched_sheet, MatchedSheet):
        sheet_list = []  # type: List[SheetWithHeaders]
        for m in matched_sheet:
            sheet_list += match_columns(m)
        return sheet_list

    # Otherwise we're working on a single sheet
    matched_columns: List[MatchedColumn] = []
    unmatched_columns: List[ColumnConfig] = []

    # Loop over each configured column and try to identify candidate column
    for column_config in matched_sheet.source_config.columns:
        matched_header = _match_header(matched_sheet.sheet_detail.headers,
                                       column_config.matchers)
        if matched_header is None:
            unmatched_columns.append(column_config)
        else:
            matched_columns.append(MatchedColumn(header=matched_header, column=column_config))

    return [SheetWithHeaders(sheet=matched_sheet,
                             columns=matched_columns,
                             unmatched_columns=unmatched_columns
                             )]


def column_report(sheet_list: List[SheetWithHeaders],
                  unmatched_list: List[WorkSheetDetail] = None,
                  filename: str = None) -> pd.DataFrame:
    report: Dict[str, Any] = []

    if unmatched_list:
        for sheet_detail in unmatched_list:
            source_info = dict(root=sheet_detail.root, filename=sheet_detail.filename,
                               sort_key=sheet_detail.sort_key, sheetname=sheet_detail.sheetname)
            report.append(source_info)

    for source in sheet_list:
        sheet_detail = source.sheet.sheet_detail
        source_info = dict(root=sheet_detail.root, filename=sheet_detail.filename,
                           sort_key=sheet_detail.sort_key, sheetname=sheet_detail.sheetname)
        source_info["name"] = source.sheet.source_config.name

        for col in source.columns:
            loop_info = dict(source_info)
            loop_info["column_name"] = col.column.name
            loop_info["header_name"] = col.header.value
            loop_info["header_pos"] = col.header.column_index
            report.append(loop_info)

        for col in source.unmatched_columns:
            loop_info = dict(source_info)
            loop_info["column_name"] = col.name
            report.append(loop_info)

        for header in source.unmatched_headers():
            loop_info = dict(source_info)
            loop_info["header_name"] = header.value
            loop_info["header_pos"] = header.column_index
            report.append(loop_info)

    df = pd.DataFrame(report)
    df.sort_values(by=["sort_key", "sheetname"], inplace=True)
    df.loc[df["column_name"].isnull() & df["header_name"].notnull(), "potential_mismatch"] = True

    if filename is not None:
        df = df[
            ["root", "filename", "sort_key", "sheetname", "name", "column_name", "header_name", "potential_mismatch"]]
        df.to_excel(filename, index=False)

    return df
