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
        collected_items.append(self.token_queue.popleft())  # collect BEGIN
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
        Try to linearly collect macro tokens. BEGIN is already collected.
        :return: True, if successful, False otherwise. If False, the collected_items are parsed as a regular string
        """
        # Collect any space between BEGIN and MACRO. Thus '<    cursor>' will be a valid macro.
        if not self._try_collect_space(collected_items):
            return False
        # Now, the next token must be a MACRO token
        if not self._try_collect_macro_token(collected_items):
            return False

    def _try_collect_space(self, collected_items: TokenQueue) -> bool:
        """
        Collect the next token, if it is a SPACE token. Otherwise, do nothing.
        :param collected_items: Queue containing all tokens collected during macro parsing
        :return: True, if the queue still contains items, False otherwise
        """
        item = self.token_queue.popleft()
        if item.typ == "SPACE":
            collected_items.append(item)
            self._request_next()
        else:
            # Not a space, so do nothing, just push the item back
            self.token_queue.appendleft(item)
        return bool(self.token_queue)

    def _try_collect_macro_token(self, collected_items: TokenQueue) -> bool:
        """
        Collect the next token, if it is a MACRO token. Otherwise, do nothing.
        :param collected_items: Queue containing all tokens collected during macro parsing
        :return: True, if a MACRO was collected and the queue still contains items, False otherwise
        """
        item = self.token_queue.popleft()
        collected_items.append(item)
        self._request_next()

        return (item.typ == "MACRO") and bool(self.token_queue)

    def _build_macro_parameters(self, collected_items: TokenQueue):
        """
        Parse the to be used macro class and the parameter list.
        :raises KeyError: If the requested macro class is not found.
        """
        # The last queued item is a MACRO token, thus the token value is by construction a valid key for MACRO_CLASSES.
        macro_class = MacroSection.MACRO_CLASSES[collected_items[-1].value]
        required_parameters = [arg[0] for arg in macro_class.ARGS]  # split (name, gui_description) tuples
        self._try_collect_space(collected_items)
        while self.token_queue[0].typ != "END":
            pass

    def _request_next(self):
        try:
            self.token_queue.append(next(self.tokens))
        except GeneratorExit:
            pass

    def _collect_quoted_string(self):

        collected_items = collections.deque()  # type: TokenQueue
