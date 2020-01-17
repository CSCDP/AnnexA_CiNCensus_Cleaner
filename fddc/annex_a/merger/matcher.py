from fddc.regex import parse_regex


class Matcher:
    def __init__(self, type: str, **args):
        if type == "regex":
            self.__matcher = RegexMatcher(**args)
        else:
            raise Exception("Unknown matcher type: {}".format(type))

    def match(self, string: str) -> bool:
        return self.__matcher.match(string)


class RegexMatcher(Matcher):
    def __init__(self, pattern):
        self.__matcher = parse_regex(pattern)

    def match(self, string):
        if self.__matcher.match(string) is not None:
            return True
        else:
            return False
