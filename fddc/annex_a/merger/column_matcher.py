import copy
from dataclasses import dataclass
from typing import List, Union

from fddc.annex_a.merger.configuration import ColumnConfig
from fddc.annex_a.merger.datasource_matcher import MatchedSheet
from fddc.annex_a.merger.matcher import MatcherConfig
from fddc.annex_a.merger.workbook_util import WorkSheetHeaderItem


@dataclass
class MatchedColumn:
    column: ColumnConfig
    header: WorkSheetHeaderItem


@dataclass
class SheetWithHeaders:
    sheet: MatchedSheet
    columns: List[MatchedColumn]
    unmatched_columns: List[ColumnConfig]


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
    matched_columns = []  # type: List[MatchedColumn]
    unmatched_columns = []  # type: List[ColumnConfig]

    # Loop over each configured column and try to identify candidate column
    for column_config in matched_sheet.source_config.columns:
        matched_header = _match_header(matched_sheet.sheet_detail.header_values,
                                       column_config.matchers)
        if matched_header is None:
            unmatched_columns.append(column_config)
        else:
            matched_columns.append(MatchedColumn(header=matched_header, column=column_config))

    return [SheetWithHeaders(sheet=matched_sheet, columns=matched_columns, unmatched_columns=unmatched_columns)]


def column_report(data_sources, all_data_sources, filename=None):
    import pandas as pd
    report = []

    invalid_data_sources = [d for d in all_data_sources if "source_key" not in d]
    for source in invalid_data_sources:
        source_info = dict(root=source["root"], filename=source["sourcename"],
                           sort_key=source["sort_key"], sheetname=source["sheetname"])
        report.append(source_info)

    for source in data_sources:
        source_info = dict(root=source["root"], filename=source["sourcename"],
                           sort_key=source["sort_key"], sheetname=source["sheetname"])
        source_info["name"] = source["source_config"]["name"]

        for col in source.get("column_spec", []):
            loop_info = copy.deepcopy(source_info)
            loop_info["column_name"] = col["name"]

            if "header" in col:
                loop_info["header_name"] = col["header"]["name"]
                loop_info["header_pos"] = col["header"]["pos"]

            report.append(loop_info)

        for header in source.get("headers_unmatched", []):
            loop_info = copy.deepcopy(source_info)
            loop_info["header_name"] = header["name"]
            loop_info["header_pos"] = header["pos"]
            report.append(loop_info)

    df = pd.DataFrame(report)
    df.sort_values(by=["sort_key", "sheetname"], inplace=True)
    df.loc[df["column_name"].isnull() & df["header_name"].notnull(), "potential_mismatch"] = True

    if filename is not None:
        df = df[
            ["root", "filename", "sort_key", "sheetname", "name", "column_name", "header_name", "potential_mismatch"]]
        df.to_excel(filename, index=False)

    return df
