import re

# Define token types and corresponding patterns
TOKEN_TYPES = [
    ("INTEGER", r"\d+"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MULTIPLY", r"\*"),
    ("DIVIDE", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("EQUALS", r"="),
    ("SEMICOLON", r";"),
    ("LBRACE", r"{"),
    ("RBRACE", r"}"),
    ("TYPE", r":\s*(int|float|str|list|dict)"),
    ("STRING", r'"(?:\\.|[^"])*"'),
    # ('FLOAT', r'\d+\.\d+'),
    ("DOT", r"\."),
    ("CLUSTER", r"Cluster"),
    ("GALAXY", r"Galaxy"),
    ("BLACK_HOLE", r"Black_hole"),
    ("STAR_SYSTEM", r"Star_system"),
    ("COMET", r"Comet"),
    ("PLANET", r"Planet"),
    ("ASTEROID", r"Asteroid"),
    ('PRINT', r'print'),
    ("IDENTIFIER", r"[a-zA-Z_]\w*"),

]

# Define a pattern to match whitespace characters
WHITESPACE_PATTERN = r"\s+"


# Lexer implementation
def lexer(input_code):
    tokens = []
    position = 0
    pattern = None

    while position < len(input_code):
        matched = False

        # Skip whitespace characters
        whitespace_match = re.match(WHITESPACE_PATTERN, input_code[position:])
        if whitespace_match:
            whitespace_length = whitespace_match.end()
            position += whitespace_length
            continue

        for token_type, pattern in TOKEN_TYPES:
            regex = re.compile(pattern)
            match = regex.match(input_code, position)

            if match:
                value = match.group(0)
                token = (token_type, value)
                tokens.append(token)
                position = match.end()
                matched = True
                break

        if not matched:
            print(tokens)
            raise ValueError(
                f"Invalid token at position {position}: {input_code[position]}"
            )

    return tokens
