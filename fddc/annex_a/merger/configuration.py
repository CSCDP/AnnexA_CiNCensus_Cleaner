import re
import dacite
from abc import ABC
from dataclasses import dataclass
from typing import List, Union
from fddc.config import Config
from fddc.regex import parse_regex


class MatcherConfig(ABC):
    def __init__(self, type: str, **kwargs):
        self.type = type
        if type == "regex":
            self.__matcher = RegexMatcherConfig(**kwargs)
        else:
            raise "Unknown matcher type: {}".format(type)

    def match(self, string: str) -> bool:
        return self.__matcher.match(string)


@dataclass(frozen=True, eq=True)
class RegexMatcherConfig(MatcherConfig):
    pattern: str
    type: str = 'regex'

    def __post_init__(self):
        assert self.type == 'regex'
        object.__setattr__(self, '__matcher', parse_regex(self.pattern))

    def match(self, string):
        matcher = object.__getattribute__(self, '__matcher')
        if matcher.match(string) is not None:
            return True
        else:
            return False


def _parse_regex(regex: Union[str, List[str]], name: str):
    # Create default regex based on name
    if regex is None:
        # Escape any characters that may cause issues for the expression
        name = re.escape(name)

        # We ignore spaces in the final matching
        name = re.sub(r'(\\ )+', r'\s+', name)

        # Smart quotes also often cause problems
        name = re.sub(r'\\[\'\"]', r'.', name)

        # Create regex
        regex = [f"/.*{name}.*/i"]

    # We want a list
    if isinstance(regex, str):
        regex = [regex]

    return [RegexMatcherConfig(type='regex', pattern=p) for p in regex]


@dataclass(frozen=True, eq=True)
class ColumnConfig:
    name: str
    unique: bool = False
    type: str = None
    matchers: List[MatcherConfig] = None
    regex: Union[str, List[str]] = None

    def __post_init__(self):
        # Set matchers object
        if self.matchers is None:
            object.__setattr__(self, 'matchers', _parse_regex(self.regex, self.name))


@dataclass(frozen=True, eq=True)
class SourceConfig:
    name: str
    columns: List[ColumnConfig] = None
    matchers: List[MatcherConfig] = None
    regex: Union[str, List[str]] = None

    def __post_init__(self):
        # Set matchers object
        if self.matchers is None:
            object.__setattr__(self, 'matchers', _parse_regex(self.regex, self.name))

    def column_names(self) -> List[str]:
        return [c.name for c in self.columns]


@dataclass(frozen=True, eq=True)
class __DataSourceConfig:
    datasources: List[SourceConfig]


def parse_datasources(*args) -> List[SourceConfig]:
    config = Config(*args)

    data_sources = dacite.from_dict(
        data_class=__DataSourceConfig,
        data=dict(datasources=config["datasources"]),
        config=dacite.Config(strict=True)
    )

    return data_sources.datasources
