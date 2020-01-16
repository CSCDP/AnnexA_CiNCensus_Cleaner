import copy
import re

def init_datasource_config(datasource_config):
    """
    Reads all configured datasources from the configuration
    and initialises them with patterns.

    Returns a new object.
    """
    datasource_config = copy.deepcopy(datasource_config)
    for key, cfg_source in datasource_config.items():
        # We generate a default regex to use if no specific pattern is set
        name = cfg_source["name"]
        name = re.sub(r'\s+', "\\\s+", name)

        # If regex is not set, use our default one instead
        pattern = cfg_source.get("regex", "/.*{}.*/i".format(name))

        # Set matchers object
        cfg_source["matchers"] = [{"type": "regex", "pattern": pattern}]

    return datasource_config


def init_all_column_config(datasources):
    datasources = copy.deepcopy(datasources)
    for ds in datasources:
        ds_key = ds["source_key"]
        custom_config = ds["input_cfg"].get("datasources", {}).get(ds_key, dict(columns=[]))["columns"]
        global_config = ds["source_config"]["columns"]

        ds["column_config"] = init_column_config(global_config, custom_config)

    return datasources


def init_column_config(global_config, custom_config):
    """
    Iterates over the columns and adds matcher configuration

    Returns merged list
    """
    custom_config_dict = {d["name"]: d for d in custom_config}

    global_config = copy.deepcopy(global_config)

    for col in global_config:
        # We generate a default regex to use if no specific pattern is set
        name = col["name"]
        escaped_name = re.sub(r'\s+', "\\\s+", name)

        # Create default matchers for column
        pattern = col.get("regex", "/.*{}.*/i".format(escaped_name))
        matchers = [{"type": "regex", "pattern": pattern}]

        # See if we have any custom matchers
        custom_col_config = custom_config_dict.get(name)
        if custom_col_config is not None and "regex" in custom_col_config:
            matchers = [{"type": "regex", "pattern": custom_col_config["regex"]}] + matchers

        col["matchers"] = matchers

    return global_config