import copy
import logging

logger = logging.getLogger('fddc.annex_a.merger.merge_util')

def load_dataframes(valid_datasources, datasources, **args):
    import pandas as pd
    ds_lookup = {ds["filename"]: {} for ds in valid_datasources}
    for ds in valid_datasources:
        ds_lookup[ds["filename"]][ds["sheetname"]] = copy.deepcopy(ds)

    valid_datasources = []
    for filename in ds_lookup:
        logger.info("Opening {}".format(filename))
        file = pd.ExcelFile(filename)
        for sheetname in ds_lookup[filename]:
            ds = ds_lookup[filename][sheetname]
            valid_datasources.append(ds)
            skiprows = ds.get("header_row_index")
            if skiprows is None:
                skiprows = 1
            logger.debug("Reading '{}' from '{}'".format(sheetname, filename))
            df = pd.read_excel(filename, skiprows=skiprows - 1, sheet_name=sheetname)
            ds["dataframe"] = df
            logger.debug("Reading {} rows and {} cols from '{}' from '{}'".format(*df.shape, sheetname, filename))

    return valid_datasources


def merge_datasources(valid_datasources, datasources, error_report_filename=False, **args):
    import pandas as pd
    import numpy as np

    cfg_datasources = datasources

    output_dataframes = {}

    error_report = []

    for ds_key in cfg_datasources.keys():
        # Find datasources for this key
        datasources = [ds for ds in valid_datasources if ds["source_key"] == ds_key]

        # Find configuration for this datasource
        cfg_datasource = cfg_datasources[ds_key]
        cfg_columns = cfg_datasource["columns"]
        columns = [c["name"] for c in cfg_columns]
        unique_columns = [c["name"] for c in cfg_columns if c.get("unique", False)]

        # Read datasources
        dataframes = []
        for ds in datasources:
            df = ds["dataframe"]

            # Build column map for this datasource
            column_map = {}
            columns_found = []
            for col in ds["column_spec"]:
                if "header" in col:
                    column_map[col["header"]["name"]] = col["name"]
                    columns_found.append(col["name"])
            df.rename(columns=column_map, inplace=True)

            # Add missing columns
            for c in columns:
                if c not in columns_found:
                    logger.debug("Adding missing column {}".format(c))
                    df[c] = np.nan

            # Sort columns
            df = df[columns].copy()

            # Add sort key
            df["sort_key"] = ds["sort_key"]

            # See if we need special type handling on any columns
            for col in ds["column_spec"]:
                col_type = col.get("type")
                col_name = col["name"]
                if col_type == "date":
                    size_before = df[col_name].count()

                    after_col = col_name + "_after_convert"
                    df[after_col] = pd.to_datetime(df[col_name], dayfirst=True, errors="coerce")

                    error_values = df[~df[col_name].isnull() & df[after_col].isnull()] \
                        [col_name].values.tolist()
                    error_values = [{"sourcename": ds["sourcename"],
                                     "sheetname": ds["sheetname"],
                                     "column": col_name,
                                     "column_type": col_type,
                                     "original": v
                                     } for v in error_values]

                    error_report += error_values

                    df[col_name] = df[after_col]
                    df[col_name] = df[col_name].dt.date
                    size_after = df[col_name].count()
                    if size_before != size_after:
                        logger.warn("Removed {} dates from {} in {} due to invalid format."
                                    .format(size_before - size_after, ds["sheetname"], ds["sourcename"]))

            dataframes.append(df)

        if len(dataframes) > 0:
            logger.debug("Merging {} dataframes for {} with the following unique columns: {}" \
                         .format(len(dataframes), ds_key, unique_columns))

            df_lengths = []
            for df in dataframes:
                df_lengths.append(df.shape[0])

            dataframes = pd.concat(dataframes)
            len_before = dataframes.shape[0]

            dataframes.sort_values("sort_key", inplace=True)

            for c in unique_columns:
                logger.debug("Column {} has {} unique values".format(c, len(dataframes[c].unique())))

            dataframes = dataframes.groupby(unique_columns).last().reset_index()
            dataframes = dataframes[columns]

            output_dataframes[ds_key] = dataframes

            len_after = dataframes.shape[0]

            if len_after <= np.min(df_lengths):
                logger.warning("Low number of rows after deduplication - could indicate a problem. " +
                               "Before: {} After: {}".format(len_before, len_after))

            logger.debug("Deduplicated {} rows giving {} unique rows  for {}".format(len_before, len_after, ds_key))

    if error_report_filename is not None and len(error_report) > 0:
        error_report = pd.DataFrame(error_report)
        error_report = error_report[["sourcename", "sheetname", "column", "column_type", "original"]]
        error_report.to_excel(error_report_filename, index=False)
        logger.info("Wrote column error report to {}".format(error_report_filename))

    return output_dataframes


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
