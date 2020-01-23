import logging
from dataclasses import dataclass, asdict
from typing import List, Dict

from fddc.annex_a.merger.workbook_util import WorkSheetDetail
from fddc.annex_a.merger.configuration import SheetConfig

logger = logging.getLogger('fddc.annex_a.merger.configuration')


@dataclass
class MatchedSource:
    key: str
    sheet: WorkSheetDetail
    source: SheetConfig


def _does_sheet_match(config: SheetConfig, sheetname: str):
    """ Returns True if sheetname is matched by any of the matchers in config """
    for matcher in config.matchers:
        if matcher.match(sheetname):
            return True
    return False


def match_data_sources(file_sources: List[WorkSheetDetail], data_sources: Dict[str, SheetConfig]):
    """
        Checks each entry in file_sources to see if it is matched by any of the data_sources.

        Returns the matched entries combined with the matching source.
    """
    matched_sources = []  # type: List[MatchedSource]
    unmatched_sources = [*file_sources]  # type: List[WorkSheetDetail]

    for source in file_sources:
        for key, config in data_sources.items():
            if _does_sheet_match(config, source.sheetname):
                matched_sources.append(MatchedSource(key=key, source=source, sheet=source))
                unmatched_sources.remove(source)
                break

    for source in unmatched_sources:
        logger.warning(
            "No datasource identified for '{sheetname}' in '{filename}'".format(**asdict(source)))

    return file_sources, unmatched_sources
