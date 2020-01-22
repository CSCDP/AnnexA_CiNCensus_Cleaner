import copy
import logging
from typing import List

from fddc.annex_a.merger.workbook_util import WorkSheetDetail
from fddc.annex_a.merger.configuration import DataSourceConfig

logger = logging.getLogger('fddc.annex_a.merger.configuration')


def match_data_sources(file_sources: List[WorkSheetDetail], data_sources: List[DataSourceConfig]):
    for source in file_sources:
        for key, cfg_source in data_sources.items():
            for matcher in cfg_source["matchers"]:
                if matcher.match(source["sheetname"]):
                    source["source_key"] = key
                    source["source_config"] = cfg_source
                    break

        if "source_key" not in source:
            logger.warning("No datasource identified for '{}' in '{}'".format(source["sheetname"], source["sourcename"]))

    return file_sources