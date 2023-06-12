import re
from dataclasses import dataclass

import errors


@dataclass
class Token:
    token_type: str
    pattern: str
    position: int = 0
    line_number: int = 0


COMMENTS = [
    Token("COMMENT", r"//.*"),
    Token("MULTI_LINE_COMMENT", r"(?s)/\\*.*?\\*/"),
]

VAR_TYPES = [
    Token("TYPE_INT", r"int"),
    Token("TYPE_FLOAT", r"float"),
    Token("TYPE_STR", r"str"),
    Token("TYPE_LIST", r"list"),
    Token("TYPE_DICT", r"dict"),
    Token("TYPE_BOOL", r"bool"),
    Token("TYPE_LIST", r"list"),
]

VAR_VALUES = [
    Token("FLOAT", r"\d+\.\d+"),
    Token("STR", r'"(?:\\.|[^"])*"'),
    Token("INTEGER", r"\d+"),
]

OPEATORS = [
    Token("PLUS", r"\+"),
    Token("MINUS", r"-"),
    Token("MULTIPLY", r"\*"),
    Token("DIVIDE", r"/(?![/])"),  # Matches '/' not followed by '/'
]

GROUPING_SYMBOLS = [
    Token("LPAREN", r"\("),
    Token("RPAREN", r"\)"),
    Token("LBRACE", r"{"),
    Token("RBRACE", r"}"),
    Token("LBRACKET", r"\["),
    Token("RBRACKET", r"\]"),
]

TOKEN_TYPES = [
    *COMMENTS,
    *OPEATORS,
    *GROUPING_SYMBOLS,
    *VAR_TYPES,
    *VAR_VALUES,
    Token("EQUALS", r"="),
    Token("SEMICOLON", r";"),
    Token("COLON", r":"),
    Token("DOT", r"\."),
    Token("COMMA", r","),
    Token("PRINT", r"print"),
    Token("IDENTIFIER", r"[a-zA-Z_]\w*"),
]

# Define a pattern to match whitespace characters
WHITESPACE_PATTERN = r"\s+"
COMMENT_PATTERN = r"//.*"


class Lexer:
    def __init__(self, input_code) -> None:
        self.input_code = input_code
        self.tokens: list[Token] = []
        self._position = 0
        self._pattern = None
        self._line_number = 0

    def parse(self) -> list[Token]:
        while self._position < len(self.input_code):
            matched = False

            if self.input_code[self._position] == "\n":
                self._line_number += 1

            # Skip whitespace characters
            whitespace_match = re.match(
                WHITESPACE_PATTERN, self.input_code[self._position :]
            )
            if whitespace_match:
                self._position += whitespace_match.end()
                continue

            for token in TOKEN_TYPES:
                regex = re.compile(token.pattern)
                match = regex.match(self.input_code, self._position)

                if match:
                    value = match.group(0)
                    token = Token(
                        token.token_type, value, self._position, self._line_number
                    )
                    if token.token_type not in ["COMMENT", "MULTI_LINE_COMMENT"]:
                        self.tokens.append(token)
                    self._position = match.end()
                    matched = True
                    break

            if not matched:
                # TODO
                raise errors.SyntaxError(
                    position=self._position,
                    code=self.input_code,
                    line_number=self._line_number,
                )

        # TODO wrong line number
        return self.tokens
