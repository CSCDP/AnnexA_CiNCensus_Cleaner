import copy
import re

from dataclasses import dataclass, InitVar
from typing import List, Union

from fddc.annex_a.merger.matcher import MatcherConfig, RegexMatcherConfig


def _parse_regex(regex: Union[str, List[str]], name: str):
    # Create default regex based on name
    if regex is None:
        name = re.sub(r'\s+', r'\\s+', name)
        regex = ["/.*{}.*/i".format(name)]

    # We want a list
    if isinstance(regex, str):
        regex = [regex]

    return [RegexMatcherConfig(type='regex', pattern=p) for p in regex]


@dataclass
class ColumnConfig:
    name: str
    unique: bool = False
    type: str = None
    matchers: List[MatcherConfig] = None
    regex: InitVar[Union[str, List[str]]] = None

    def __post_init__(self, regex):
        # Set matchers object
        self.matchers = _parse_regex(regex, self.name)


@dataclass
class SourceConfig:
    name: str
    columns: List[ColumnConfig] = None
    matchers: List[MatcherConfig] = None
    regex: InitVar[Union[str, List[str]]] = None

    def __post_init__(self, regex):
        # Set matchers object
        self.matchers = _parse_regex(regex, self.name)


