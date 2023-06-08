import re
import errors
from dataclasses import dataclass

@dataclass
class Token:
    token_type: str
    pattern: str
    position: int = 0
    line_number: int = 0


VAR_TYPES = [
    Token("TYPE_INT", r"int"),
    Token("TYPE_FLOAT", r"float"),
    Token("TYPE_STRING", r"str"),
    Token("TYPE_LIST", r"list"),
    Token("TYPE_DICT", r"dict"),
]

TOKEN_TYPES = [
    Token("INTEGER", r"\d+"),
    Token("PLUS", r"\+"),
    Token("MINUS", r"-"),
    Token("MULTIPLY", r"\*"),
    Token("DIVIDE", r"/"),
    Token("LPAREN", r"\("),
    Token("RPAREN", r"\)"),
    Token("EQUALS", r"="),
    Token("SEMICOLON", r";"),
    Token("LBRACE", r"{"),
    Token("RBRACE", r"}"),
    Token("COLON", r":"),
    
    *VAR_TYPES,
    # Token("TYPE", r":\s*(int|float|str|list|dict)"),

    Token("STRING", r'"(?:\\.|[^"])*"'),

    # Token('FLOAT', r'\d+\.\d+'),
    Token("DOT", r"\."),

    Token('PRINT', r'print'),

    Token("IDENTIFIER", r"[a-zA-Z_]\w*"),
]

# Define a pattern to match whitespace characters
WHITESPACE_PATTERN = r"\s+"
COMMENT_PATTERN = r"/.*"

class Lexer:
    def __init__(self, input_code) -> None:
        self.input_code = input_code
        self.tokens = []
        self._position = 0
        self._pattern = None
        self._line_number = 0

    def parse(self) -> list[Token]:
        while self._position < len(self.input_code):
            matched = False

            if self.input_code[self._position] == '\n':
                self._line_number += 1
            # Skip whitespace characters
            whitespace_match = re.match(WHITESPACE_PATTERN, self.input_code[self._position:])
            comment_match = re.match(COMMENT_PATTERN, self.input_code[self._position:])
            if whitespace_match:
                self._position += whitespace_match.end()
                continue
            elif comment_match:
                self._position += comment_match.end()
                continue

            for token in TOKEN_TYPES:
                regex = re.compile(token.pattern)
                match = regex.match(self.input_code, self._position)

                if match:
                    value = match.group(0)
                    token = Token(token.token_type, value, self._position, self._line_number)
                    self.tokens.append(token)
                    self._position = match.end()
                    matched = True
                    break

            if not matched:
                raise errors.InvalidSymbol(
                    position=self._position,
                    code=self.input_code,
                    line_number=self._line_number

                )

        return self.tokens

