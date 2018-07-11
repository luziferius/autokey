# Copyright (C) 2018 Thomas Hess
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains a parser for user phrases. It uses the results of the PhraseTokenizer to parse macro tags in
user phrases.
"""

import abc
import collections
import typing

import autokey.tokenizer
import autokey.macro

Tokens = typing.Iterator[autokey.tokenizer.Token]
TokenQueue = typing.Deque[autokey.tokenizer.Token]
MacroParameters = typing.Dict[str, str]


class AbstractPhraseSection:
    @abc.abstractmethod
    def collect(self) -> str:
        pass


class StringSection(AbstractPhraseSection):
    def __init__(self, parts: typing.List[str]):
        self.parts = parts

    def collect(self):
        return "".join(self.parts)


class MacroSection(AbstractPhraseSection):
    # Lookup table for macro classes by macro keyword.
    MACRO_CLASSES = autokey.tokenizer.extract_phrase_macro_classes()

    def __init__(self, keyword: str, parameters: MacroParameters):
        self.keyword = keyword
        self.parameters = parameters

    def collect(self):
        import warnings
        warnings.warn("collect(): stub called!")
        return "[Macro stub! Macro: {}]".format(self.keyword)


class PhraseParser:
    """
    Parses a tokenized autokey phrase. The class parses embedded macro tags and prepares the macro execution.
    All non-macro text is retained as-is.
    """

    def __init__(self, tokens: Tokens):
        self.tokens = tokens
        self.collected = []  # type: typing.List[typing.Union[StringSection, MacroSection]]
        self.token_queue = collections.deque()  # type: TokenQueue

    def parse(self):
        try:
            self.token_queue.append(next(self.tokens))
        except GeneratorExit:
            pass

        while self.token_queue:
            token = self.token_queue[0]
            if token.typ == "BEGIN":
                yield from self._collect_macro()
            else:
                yield from self._collect_string_parts()

    def _collect_string_parts(self) -> StringSection:
        """
        Used to join non-macro tokens.
        Takes Token elements, until a BEGIN is encountered, and joins all string segments.
        """
        items = []  # type: typing.List[str]
        for token in self.token_queue:
            if token.typ == "BEGIN":
                break
            else:
                items.append(self.token_queue.popleft().value)
                self._request_next()

        yield StringSection(items)

    def _collect_macro(self):
        """
        Found a possible Macro, so try to collect all macro tokens.
        There are some possibilities:
         - This is really a begin of a macro token, then all tokens can be collected linearly into a MacroSection
         - This is a broken macro token without further BEGIN tokens, then treat all tokens as string tokens to keep
         them as-is. Thus "<script>" (missing arguments) will be kept as a "<script>" StringSection.
         - This is a broken macro token, that contains multiple valid or further stacked broken tokens.
          E.g. '''<file <date format="%Y"> some text <script (broken) <script name="myscript" args="valid_token">>'''
          Those cases are most probable, when the user wants to dynamically generate HTML or XML code.
        """
        collected_items = collections.deque()  # type: TokenQueue
        collected_items.append(self.token_queue.popleft())
        self._request_next()
        if self._try_collect_macro(collected_items):
            pass
        else:
            # Collection failed
            self.token_queue.extendleft(collected_items)
            yield self._collect_string_parts()

        pass

    def _try_collect_macro(self, collected_items: TokenQueue) -> bool:
        """
        Try to linearly collect ma
        :return:
        """

    def _request_next(self):
        try:
            self.token_queue.append(next(self.tokens))
        except GeneratorExit:
            pass

    def _collect_quoted_string(self):

        collected_items = collections.deque()  # type: TokenQueue