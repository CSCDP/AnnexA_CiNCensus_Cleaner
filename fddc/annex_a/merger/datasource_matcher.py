import logging
from dataclasses import dataclass, asdict
from typing import List, Tuple

from fddc.annex_a.merger.workbook_util import WorkSheetDetail
from fddc.annex_a.merger.configuration import SourceConfig

logger = logging.getLogger('fddc.annex_a.merger.datasource_matcher')


@dataclass
class MatchedSheet:
    sheet_detail: WorkSheetDetail
    source_config: SourceConfig


def _does_sheet_match(source_config: SourceConfig, sheetname: str):
    """ Returns True if sheetname is matched by any of the matchers in source_config """
    for matcher in source_config.matchers:
        if matcher.match(sheetname):
            return True
    return False


def match_data_sources(sheet_detail_list: List[WorkSheetDetail],
                       source_configuration_list: List[SourceConfig]) -> Tuple[List[MatchedSheet], List[WorkSheetDetail]]:
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
            "No datasource identified for '{sheetname}' in '{filename}'".format(**asdict(sheet)))

    return matched_sheets, unmatched_sheets
