import logging
from dataclasses import dataclass
from typing import List, Union, Dict, Tuple
from fddc.annex_a.merger.configuration import ColumnConfig, SourceConfig, MatcherConfig
from fddc.annex_a.merger.workbook_util import WorkSheetHeaderItem, WorkSheetDetail


logger = logging.getLogger('fddc.annex_a.merger.matcher')


@dataclass(frozen=True, eq=True)
class MatchedColumn:
    column: ColumnConfig
    header: WorkSheetHeaderItem


@dataclass(frozen=True, eq=True)
class MatchedSheet:
    sheet_detail: WorkSheetDetail
    source_config: SourceConfig


@dataclass(frozen=True, eq=True)
class SheetWithHeaders:
    sheet: MatchedSheet
    columns: List[MatchedColumn]
    unmatched_columns: List[ColumnConfig]

    def column_configs(self) -> List[ColumnConfig]:
        return [c.column for c in self.columns]

    def column_names(self) -> List[str]:
        return [c.column.name for c in self.columns]

    def column_map(self) -> Dict[str, str]:
        """
        Returns a mapping of all header values to the required column names
        :return:
        """
        return {col.header.value: col.column.name for col in self.columns}

    def unmatched_headers(self) -> List[WorkSheetHeaderItem]:
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


def _does_sheet_match(source_config: SourceConfig, sheetname: str):
    """ Returns True if sheetname is matched by any of the matchers in source_config """
    for matcher in source_config.matchers:
        if matcher.match(sheetname):
            return True
    return False


def match_data_sources(
        sheet_detail_list: List[WorkSheetDetail],
        source_configuration_list: List[SourceConfig]
) -> Tuple[List[MatchedSheet], List[WorkSheetDetail]]:
    """
        Checks each entry in file_sources to see if it is matched by any of the data_sources.

        Returns the matched entries combined with the matching source.
    """
    matched_sheets = []  # type: List[MatchedSheet]
    unmatched_sheets = list(sheet_detail_list)  # type: List[WorkSheetDetail]

    for sheet_detail in sheet_detail_list:
        for source_configuration in source_configuration_list:
            if _does_sheet_match(source_configuration, sheet_detail.sheetname):
                matched_sheets.append(MatchedSheet(source_config=source_configuration, sheet_detail=sheet_detail))
                unmatched_sheets.remove(sheet_detail)
                break

    for sheet in unmatched_sheets:
        logger.warning(
            f"No datasource identified for '{sheet.sheetname}' in '{sheet.filename}'")

    return matched_sheets, unmatched_sheets
