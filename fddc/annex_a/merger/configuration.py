import copy
import re

from dataclasses import dataclass, InitVar
from typing import List, Dict, Union

from fddc.annex_a.merger.matcher import MatcherConfig, RegexMatcherConfig


@dataclass
class ColumnConfig:
    name: str
    unique: bool = False
    type: str = None
    matchers: List[MatcherConfig] = None
    regex: InitVar[Union[str, List[str]]] = None

    def __post_init__(self, regex):

        # Create default regex based on name
        if regex is None:
            name = re.sub(r'\s+', r'\\s+', self.name)
            regex = ["/.*{}.*/i".format(name)]

        # We want a list
        if isinstance(regex, str):
            regex = [regex]

        # Set matchers object
        self.matchers = [RegexMatcherConfig(type='regex', pattern=p) for p in regex]


@dataclass
class SheetConfig:
    name: str
    columns: List[ColumnConfig] = None
    regex: str = None


@dataclass
class DataSourceConfig:
    data_source: Dict[str, SheetConfig]


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
