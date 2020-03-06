import logging
from typing import Iterable, Mapping
import pandas as pd
import numpy as np

from fddc.annex_a.merger.configuration import ColumnConfig

logger = logging.getLogger('fddc.datatables.normalise')


def normalise_dataframe(
        df: pd.DataFrame,
        column_names: Iterable[str],
        column_map: Mapping[str, str] = None,
        only_retain_mapped: bool = True
) -> pd.DataFrame:
    """
    Renames columns and adds any missing (unmatched) columns

    :param df:
    :param column_names:
    :param column_map:
    :param only_retain_mapped: by default only columns that are in the map are retained, but if may columns already
    match and you only want to map a few, then set this to False to keep any that already have the right name. If you
    don't provide a map, then this setting has no effect.
    :return: the resulting DataFrame
    """
    if df is None:
        df = pd.DataFrame(columns=column_names)

    if column_map is not None:
        if only_retain_mapped:
            df = df[column_map.keys()].copy()
        df.rename(columns=column_map, inplace=True)

    # Add missing columns
    missing_columns = set(column_names) - set(df.columns)
    for c in missing_columns:
        logger.debug("Adding missing column {}".format(c))
        df[c] = np.nan

    # Return columns in right order
    return df[column_names].copy()


def _clean_date_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    size_before = df[col_name].count()
    after_col = col_name + "_after_convert"

    df[after_col] = pd.to_datetime(df[col_name], dayfirst=True, errors="coerce")

    # error_values = df[~df[col_name].isnull() & df[after_col].isnull()][col_name].values.tolist()
    # error_values = [{"sourcename": sheet.source_config.name,
    #                  "sheetname": sheet.sheet_detail.sheetname,
    #                  "column": col_name,
    #                  "column_type": 'date',
    #                  "original": v
    #                  } for v in error_values]

    df[col_name] = df[after_col]
    df[col_name] = df[col_name].dt.date

    size_after = df[col_name].count()

    if size_before != size_after:
        logger.warning(f"Removed {size_before - size_after} dates due to invalid format.")

    del df[after_col]

    return df


def clean_datatypes(df: pd.DataFrame, spec: Iterable[ColumnConfig]) -> pd.DataFrame:
    # See if we need special type handling on any columns
    for col in spec:
        col_type = col.type
        col_name = col.name
        if col_type == "date":
            df = _clean_date_column(df, col_name)

    return df
