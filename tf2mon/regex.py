"""A regular-expression/handler pair.

And functions to operate on a list of them.
"""

import re

from loguru import logger


class Regex:
    """A regular-expression/handler pair."""

    def __init__(self, pattern, handler=None):
        """Create object to run `handler` when `pattern` is a hit."""

        self.regex = re.compile(pattern)
        self.handler = handler

        self.match = self.regex.match
        self.search = self.regex.search

        # set by `match_list` or `search_list` to matching `re.Match(object)`.
        self.re_match_obj = None

    @staticmethod
    def match_list(string, regex_list):
        """Return the first matching `Regex` in `regex_list` using `match`.

        The object's `re_match_obj` attribute is set to the resultant `re.Match(object)`.
        """

        for regex in regex_list:
            if m := regex.regex.match(string):
                logger.log("regex", m)
                regex.re_match_obj = m
                return regex

        return None

    @staticmethod
    def search_list(string, regex_list):
        """Return the first matching `Regex` in `regex_list` using `search`.

        The object's `re_match_obj` attribute is set to the resultant `re.Match(object)`.
        """

        for regex in regex_list:
            if m := regex.regex.search(string):
                logger.log("regex", m)
                regex.re_match_obj = m
                return regex

        return None
