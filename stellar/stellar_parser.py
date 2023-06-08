from os import write


def parse_type(token):
    if token[0] == "TYPE":
        return token[1]
    else:
        return "unknown"


def parse_variable_declaration(tokens):
    variable_name = tokens[0][1]  # Get the variable name token
    type_token = tokens[0][0]  # Get the type token
    variable_type = parse_type(type_token)

    return {
        "node_type": "variable_declaration",
        "variable_name": variable_name,
        "variable_type": variable_type,
    }

def parse_expression(tokens):
    return parse_addition(tokens)

def parse_addition(tokens):
    left_operand = parse_multiplication(tokens)

    while tokens and tokens[0][0] in ["PLUS", "MINUS"] or tokens[0][0] not in ["SEMICOLON"]:
        operator = tokens.pop(0)[0]
        right_operand = parse_multiplication(tokens)

        left_operand = {
            "node_type": "binary_operation",
            "operator": operator,
            "left_operand": left_operand,
            "right_operand": right_operand,
        }

    return left_operand

def parse_multiplication(tokens):
    left_operand = parse_primary(tokens)

    while tokens and tokens[0][0] in ["MULTIPLY", "DIVIDE"] or tokens[0][0] not in ["SEMICOLON"]:
        operator = tokens.pop(0)[0]
        right_operand = parse_primary(tokens)

        left_operand = {
            "node_type": "binary_operation",
            "operator": operator,
            "left_operand": left_operand,
            "right_operand": right_operand,
        }

    return left_operand

def parse_primary(tokens):
    if tokens[0][0] == "INTEGER":
        value = int(tokens.pop(0)[1])
        return {"node_type": "integer_literal", "value": value}

    if tokens[0][0] == "FLOAT":
        value = float(tokens.pop(0)[1])
        return {"node_type": "float_literal", "value": value}

    if tokens[0][0] == "STRING":
        value = tokens.pop(0)[1].strip('"')
        return {"node_type": "string_literal", "value": value}

    if tokens[0][0] == "IDENTIFIER":
        name = tokens.pop(0)[1]
        return {"node_type": "variable", "name": name}

    raise ValueError(f"Invalid expression at position {tokens[0][1]}")

def parse_print(tokens):
    if tokens[0][0] != "LPAREN":
        raise RuntimeError()
    tokens.pop(0)
    expression = None
    token_type = None

    while tokens[0][0] != "RPAREN":
        if tokens[0][0] == "IDENTIFIER":
            expression = parse_variable_declaration(tokens)
        else:
            expression = parse_primary(tokens)
        tokens.pop(0)
    tokens.pop(0)

    if tokens[0][0] != "SEMICOLON":
        raise RuntimeError()
    tokens.pop(0)
    return {"node_type": "print_statement", "expression": expression}
        

def parse_statement(tokens):
    if tokens[0][0] == "IDENTIFIER" and tokens[1][0] == "EQUALS":
        variable_name = tokens.pop(0)[1]  # Get the variable name token

        tokens.pop(0)  # Skip the equals token
        expression = parse_expression(tokens)
        tokens.pop(0)  # Skip the semicolon token
        return {
            "node_type": "assignment_statement",
            "variable_name": variable_name,
            "expression": expression,
        }
    tokens.pop(0)
    return {"node_type": "assignment_statement", "variable_name": "", "expression": ""}


MAP = {
    "PRINT": parse_print,
}

def parse_program(tokens):
    program = []

    while tokens:
        token, value = tokens[0][0], tokens[0][1]
        print(tokens)
        if token == "PRINT":
            tokens.pop(0)  # Skip the 'print' token
            program.append(parse_print(tokens))

        elif token == "IDENTIFIER" and tokens[1][0] == "EQUALS":
            a = parse_statement(tokens)
            program.append(a)

    return program
