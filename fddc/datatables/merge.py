import logging
from typing import Iterable, Union, Sequence
import pandas as pd
import numpy as np

from fddc.annex_a.merger.configuration import ColumnConfig

logger = logging.getLogger('fddc.datatables.merge')


def merge_dataframes(
        dataframes: Sequence[pd.DataFrame],
        columns: Iterable[ColumnConfig],
        sort_key: Union[str, Iterable[str]] = None
) -> pd.DataFrame:
    all_column_names = [c.name for c in columns]
    unique_columns = [c.name for c in columns if c.unique]

    logger.debug(f"Merging {len(dataframes)} dataframes with the following "
                 f"unique columns: {unique_columns}")

    df_lengths = [df.shape[0] for df in dataframes]

    df = pd.concat(dataframes)
    len_before = df.shape[0]

    if sort_key is not None:
        df.sort_values(sort_key, ascending=True, inplace=True)

    if len(unique_columns) > 0:
        df = df.groupby(unique_columns).last().reset_index()
        df = df[all_column_names]
        len_after = df.shape[0]

        logger.info(f"Deduplicated {len_before} rows resulting in {len_after} unique rows.")

        # If we have ended up with less rows than our smallest sheet, then something odd is going on
        if len_after < np.min(df_lengths):
            logger.warning(f"Low number of rows after deduplication - could indicate a problem. "
                           f"Before: {len_before} After: {len_after}")

    return df
