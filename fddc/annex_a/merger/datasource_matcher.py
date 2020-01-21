import copy
import logging
from fddc.annex_a.merger.matcher import Matcher

logger = logging.getLogger('fddc.annex_a.merger.configuration')


def match_datasources(data_sources, datasource_config):
    data_sources = copy.deepcopy(data_sources)
    for source in data_sources:
        for key, cfg_source in datasource_config.items():
            for matcher in cfg_source["matchers"]:
                matcher = Matcher(**matcher)
                if matcher.match(source["sheetname"]):
                    source["source_key"] = key
                    source["source_config"] = cfg_source
                    break

        if "source_key" not in source:
            logger.warning("No datasource identified for '{}' in '{}'".format(source["sheetname"], source["sourcename"]))

    return data_sources