import copy


def match_columns(data_sources):
    data_sources = copy.deepcopy(data_sources)
    for ds in data_sources:

        # Build list of available headers
        ds_headers = [{"name": x, "pos": ix} for ix, x in enumerate(ds["header_values"]) if x is not None]

        # Loop over each configured column and try to identify candidate column
        columns = []
        for col in ds["column_config"]:
            col = copy.deepcopy(col)
            columns.append(col)
            for matcher in col["matchers"]:
                # matcher = Matcher(**matcher)
                for header in ds_headers:
                    if matcher.match(header["name"]):
                        ds_headers.remove(header)
                        col["header"] = header
                        break

        ds["column_spec"] = columns
        ds["headers_unmatched"] = ds_headers

    return data_sources


def column_report(data_sources, all_data_sources, filename=None):
    import pandas as pd
    report = []

    invalid_data_sources = [d for d in all_data_sources if "source_key" not in d]
    for source in invalid_data_sources:
        source_info = dict(root=source["root"], filename=source["sourcename"],
                           sort_key=source["sort_key"], sheetname=source["sheetname"])
        report.append(source_info)

    for source in data_sources:
        source_info = dict(root=source["root"], filename=source["sourcename"],
                           sort_key=source["sort_key"], sheetname=source["sheetname"])
        source_info["name"] = source["source_config"]["name"]

        for col in source.get("column_spec", []):
            loop_info = copy.deepcopy(source_info)
            loop_info["column_name"] = col["name"]

            if "header" in col:
                loop_info["header_name"] = col["header"]["name"]
                loop_info["header_pos"] = col["header"]["pos"]

            report.append(loop_info)

        for header in source.get("headers_unmatched", []):
            loop_info = copy.deepcopy(source_info)
            loop_info["header_name"] = header["name"]
            loop_info["header_pos"] = header["pos"]
            report.append(loop_info)

    df = pd.DataFrame(report)
    df.sort_values(by=["sort_key", "sheetname"], inplace=True)
    df.loc[df["column_name"].isnull() & df["header_name"].notnull(), "potential_mismatch"] = True

    if filename is not None:
        df = df[
            ["root", "filename", "sort_key", "sheetname", "name", "column_name", "header_name", "potential_mismatch"]]
        df.to_excel(filename, index=False)

    return df