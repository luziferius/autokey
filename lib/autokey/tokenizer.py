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
This package contains a tokenizer for parsing user phrases. The implementation is based on the example tokenizer
implementation provided by the Python 're' module documentation, here:
https://docs.python.org/3.7/library/re.html#writing-a-tokenizer

The phrase tokenizer is used to identify macro tags present in the phrase text. It splits the full phrase into text
sections. The resulting token generator can be used by a parser to parse macro definitions in user phrases.
"""

import re
import typing
import abc
import inspect


def _extract_phrase_macro_keywords() -> typing.Set[str]:
    """Get all keywords by iterating over the macro module and extracting the ID of all AbstractMacro subclasses."""
    import autokey.macro
    all_classes = (class_info[1] for class_info in inspect.getmembers(autokey.macro, inspect.isclass))
    return {cls.ID for cls in all_classes if cls
            # Because issubclass(A, A) is True, make sure to exclude the abstract base class.
            is not autokey.macro.AbstractMacro and issubclass(cls, autokey.macro.AbstractMacro)}


Token = typing.NamedTuple("Token", [("typ", str), ("value", str), ("line", int), ("column", int)])


class AbstractTokenizer:
    """
    This class implements an abstract, regular expression based tokenizer/scanner.
    It can be used to define concrete tokenizers by defining the token specification.
    """
    TokenSpecification = typing.NamedTuple("TokenSpecification", [("name", str), ("expression", str)])

    def __init__(self):
        token_regex = "|".join(
            "(?P<{name}>{expression})".format(name=pair.name, expression=pair.expression)
            for pair in self.token_specifications
        )
        self._compiled_expression = re.compile(token_regex)

    @property
    @abc.abstractmethod
    def token_specifications(self) -> typing.Iterable[TokenSpecification]:
        """
        Each token has a name, identifying the token kind and a regular expression that specifies what the token is
         matching.
        """
        pass

    @property
    def compiled_expression(self) -> typing.Pattern:
        """Returns a compiled regular expression pattern used for the tokenizer."""
        return self._compiled_expression

    def tokenize(self, code: str) -> typing.Generator[Token, None, None]:
        """Returns a Generator, splitting the input code into Tokens, based on the token specification"""
        line_num = 1
        line_start = 0
        for mo in self.compiled_expression.finditer(code):
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - line_start
            yield Token(kind, value, line_num, column)

            if kind == "NEWLINE":
                line_start = mo.end()
                line_num += 1


class PhraseTokenizer(AbstractTokenizer):
    """
    The Phrase tokenizer is used to split user phrases.
    The result can be used to parse <macro> tags in phrases.
    """

    KEYWORDS = _extract_phrase_macro_keywords()

    def __init__(self):

        # When adding new special characters: Remember to exclude them in the OTHER Token. Otherwise, it will greedily
        # swallow those. E.g. if [] brackets are added but not excluded in OTHER, because OTHER is greedy, in example
        # input "Ab[e", the "[" will be swallowed by OTHER and the expected "[" match won’t occur.
        self._token_specifications = (
            AbstractTokenizer.TokenSpecification("BEGIN", r"<"),  # Macro begin
            AbstractTokenizer.TokenSpecification("END", r">"),  # Macro end
            AbstractTokenizer.TokenSpecification("ASSIGN", r"="),  # Parameter value assignment
            AbstractTokenizer.TokenSpecification("MACRO", "|".join(PhraseTokenizer.KEYWORDS)),  # Identifiers
            AbstractTokenizer.TokenSpecification('NEWLINE', r"\n"),  # Line endings
            AbstractTokenizer.TokenSpecification("SPACE", r" +"),  # Space. Delimits multiple macro parameters
            AbstractTokenizer.TokenSpecification("STRING_DELIMITER", r'"'),  # Marks begin and end of parameter values
            AbstractTokenizer.TokenSpecification("STRING_ESCAPE", r'\\'),  # Escapes string delimiters in strings
            # Any other character sequence.
            AbstractTokenizer.TokenSpecification("OTHER", r'[^<>= \\"' + '\n' + ']+')
        )
        # super class __init__ called last, because it needs the data specified above
        super(PhraseTokenizer, self).__init__()

    @property
    def token_specifications(self)-> typing.Iterable[AbstractTokenizer.TokenSpecification]:
        return self._token_specifications
