import logging

from . import column_matcher
from . import configuration
from . import datasource_matcher
from . import file_scanner
from . import merge_util
from . import workbook_util

logger = logging.getLogger('fddc.annex_a.merger')


def merge(config):
    # First we scan the input files section for all inputs
    files = []
    for cfg_input in config["input_files"]:
        files += file_scanner.find_input_files(**cfg_input)

    logger.info("Found {} candidate input files".format(len(files)))

    # We then scan the input files for data sources
    data_sources = []
    for file in files:
        data_sources += workbook_util.find_worksheets(**file)

    logger.info("Found {} candidate data sources".format(len(data_sources)))

    # Read Global Datasource Configuration
    datasources_config = configuration.init_datasource_config(config["datasources"])

    # Match datasources based on configuration
    datasources_config_matched = datasource_matcher.match_datasources(data_sources, datasources_config)

    # Limit to only matched datasources
    valid_datasources = [d for d in datasources_config_matched if "source_key" in d]

    # Initialise column configuration for all valid datasources
    valid_datasources = config.init_all_column_config(valid_datasources)

    # Match headers to column configuration
    valid_datasources =column_matcher.match_columns(valid_datasources)

    # Write column report
    if config.get("column_report_filename") is not None:
        column_matcher.column_report(valid_datasources, datasources_config_matched, config["column_report_filename"])

    # Load dataframes
    valid_datasources = merge_util.load_dataframes(valid_datasources, **config)

    # Merge sources into single view
    valid_datasources = merge_util.merge_datasources(valid_datasources, **config)

    # Write final output
    merge_util.write_dataframes(valid_datasources, **config)

    return valid_datasources
