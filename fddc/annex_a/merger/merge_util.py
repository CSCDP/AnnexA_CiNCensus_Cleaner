import copy
import logging
from typing import List, Dict

import pandas as pd
import numpy as np

from fddc.annex_a.merger import SheetWithHeaders, SourceConfig
from fddc.annex_a.merger.datasource_matcher import MatchedSheet

logger = logging.getLogger('fddc.annex_a.merger.merge_util')


def _index_sheets_by_filename(sheet_list: List[SheetWithHeaders]) -> Dict[str, Dict[str, SheetWithHeaders]]:
    sheet_lookup = dict()
    for sheet in sheet_list:
        sheet_lookup.setdefault(sheet.sheet.sheet_detail.filename, {})[sheet.sheet.sheet_detail.sheetname] = sheet
    return sheet_lookup


def _index_sheets_by_source(sheet_list: List[SheetWithHeaders]) -> Dict[SourceConfig, List[SheetWithHeaders]]:
    sheet_lookup = dict()
    for sheet in sheet_list:
        sheet_lookup.setdefault(sheet.sheet.source_config, []).append(sheet)
    return sheet_lookup


def load_dataframes(sheet_list: List[SheetWithHeaders]) -> Dict[SheetWithHeaders, pd.DataFrame]:
    dataframes: Dict[SheetWithHeaders, pd.DataFrame] = []

    # We group the sheets by filename so we can optimize loading
    sheet_lookup = _index_sheets_by_filename(sheet_list)

    for filename in sheet_lookup.keys():
        logger.info("Opening {}".format(filename))
        file = pd.ExcelFile(filename)

        for sheetname, sheet in sheet_lookup[filename].items():
            logger.info("Reading '{}' from '{}'".format(sheetname, filename))
            skiprows = sheet.sheet.sheet_detail.header_row_index
            df = pd.read_excel(file, skiprows=skiprows - 1, sheet_name=sheetname)
            logger.debug("Read {} rows and {} cols from '{}' from '{}'".format(*df.shape, sheetname, filename))

            dataframes[sheet] = df

    return dataframes


def normalise_datasources(dataframes: Dict[SheetWithHeaders, pd.DataFrame]) -> Dict[SheetWithHeaders, pd.DataFrame]:
    """
    Renames columns and adds any missing (unmatched) columns

    :param dataframes:
    :return:
    """
    normalised_dataframes: Dict[SheetWithHeaders, pd.DataFrame] = dict()
    for sheet, df in dataframes.items():
        df = df.copy()

        all_column_names = [c.name for c in sheet.sheet.source_config.columns]

        column_map = dict()

        # Rename all matched columns
        for col in sheet.columns:
            column_map[col.header.value] = col.column.name

        df.rename(columns=column_map, inplace=True)

        # Add missing columns
        missing_columns = set(all_column_names) - set(column_map.values())
        for c in missing_columns:
            logger.debug("Adding missing column {}".format(c))
            df[c] = np.nan

        # Return columns in right order
        df = df[all_column_names].copy()

        # Store
        normalised_dataframes[sheet] = df

    return normalised_dataframes


def _clean_date_column(df: pd.DataFrame, col_name: str, sheet: MatchedSheet) -> Dict:
    size_before = df[col_name].count()
    after_col = col_name + "_after_convert"

    df[after_col] = pd.to_datetime(df[col_name], dayfirst=True, errors="coerce")

    error_values = df[~df[col_name].isnull() & df[after_col].isnull()][col_name].values.tolist()
    error_values = [{"sourcename": sheet.source_config.name,
                     "sheetname": sheet.sheet_detail.sheetname,
                     "column": col_name,
                     "column_type": 'date',
                     "original": v
                     } for v in error_values]

    df[col_name] = df[after_col]
    df[col_name] = df[col_name].dt.date

    size_after = df[col_name].count()

    if size_before != size_after:
        logger.warning("Removed {} dates from {}/{} in {} due to invalid format.".format(
            size_before - size_after,
            sheet.sheet.source_config.name,
            sheet.sheet.sheet_detail.sheetname,
            sheet.sheet.sheet_detail.filename,
        ))

    return error_values


def clean_datatypes(dataframes: Dict[SheetWithHeaders, pd.DataFrame]) -> Dict[SheetWithHeaders, pd.DataFrame]:
    cleaned_dataframes: Dict[SheetWithHeaders, pd.DataFrame] = dict()
    for sheet, df in dataframes.items():
        df = df.copy()

        # See if we need special type handling on any columns
        for col in sheet.columns:
            col_type = col.column.type
            col_name = col.column.name
            if col_type == "date":
                _clean_date_column(df, col_name, sheet.sheet)

        cleaned_dataframes[sheet] = df

    return cleaned_dataframes


def merge_datasources(dataframes: Dict[SheetWithHeaders, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    sheet_lookup = _index_sheets_by_source(dataframes.keys())
    output_dataframes: Dict[str, pd.DataFrame] = dict()

    for source, sheet_list in sheet_lookup.items():

        dataframe_list = [dataframes[sheet] for sheet in sheet_list]
        unique_columns = [c for c in source.columns if c.unique]
        all_column_names = [c.name for c in sheet.sheet.source_config.columns]

        if len(dataframe_list) > 0:
            logger.debug("Merging {} dataframes for {} with the following unique columns: {}"
                         .format(len(dataframe_list), source.name, unique_columns))

            df_lengths = [df.shape[0] for df in dataframe_list]

            merged = pd.concat(dataframe_list)
            len_before = merged.shape[0]

            merged.sort_values("sort_key", inplace=True)

            for c in unique_columns:
                logger.debug("Column {} has {} unique values".format(c, len(merged[c].unique())))

            merged = dataframes.groupby(unique_columns).last().reset_index()
            merged = merged[all_column_names]

            output_dataframes[source.name] = merged

            len_after = merged.shape[0]

            # If we have ended up with less rows than our smallest sheet, then something odd is going on
            if len_after < np.min(df_lengths):
                logger.warning("Low number of rows after deduplication - could indicate a problem. " +
                               "Before: {} After: {}".format(len_before, len_after))

            logger.debug("Deduplicated {} rows giving {} unique rows  for {}".format(len_before, len_after, ds_key))

    return output_dataframes

    # if error_report_filename is not None and len(error_report) > 0:
    #     error_report = pd.DataFrame(error_report)
    #     error_report = error_report[["sourcename", "sheetname", "column", "column_type", "original"]]
    #     error_report.to_excel(error_report_filename, index=False)
    #     logger.info("Wrote column error report to {}".format(error_report_filename))


def write_dataframes(dataframes, datasources, output_file, **args):
    import pandas as pd
    cfg_datasources = datasources

    logger.info("Writing to {}".format(output_file))
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    for ds_key, ds in cfg_datasources.items():
        logger.info("Writing {}".format(ds_key))
        df = dataframes.get(ds_key)
        if df is None:
            df = pd.DataFrame(columns=[x["name"] for x in ds["columns"]])
        df.to_excel(writer, sheet_name=ds["name"], index=False)

    writer.save()
