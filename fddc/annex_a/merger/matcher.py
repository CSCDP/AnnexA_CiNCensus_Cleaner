from abc import ABC

from dataclasses import dataclass

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


@dataclass
class RegexMatcherConfig(MatcherConfig):
    pattern: str
    type: str = 'regex'

    def __post_init__(self):
        assert self.type == 'regex'
        self.__matcher = parse_regex(self.pattern)

    def match(self, string):
        if self.__matcher.match(string) is not None:
            return True
        else:
            return False

