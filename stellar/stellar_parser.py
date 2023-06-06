def parse_type(token):
    if token[0] == "TYPE":
        return token[1]
    else:
        return "unknown"


def parse_variable_declaration(tokens):
    variable_name = tokens.pop(0)[1]  # Get the variable name token
    type_token = tokens.pop(0)  # Get the type token
    variable_type = parse_type(type_token)
    tokens.pop(0)  # Skip the equals sign token
    value_token = tokens.pop(0)  # Get the value token

    return {
        "node_type": "variable_declaration",
        "variable_name": variable_name,
        "variable_type": variable_type,
        "value": value_token[1],
    }


# def parse_expression(tokens):
#     if tokens[0][0] == "INTEGER":
#         value = int(tokens.pop(0)[1])
#         return {"node_type": "integer_literal", "value": value}
#
#     if tokens[0][0] == "FLOAT":
#         value = float(tokens.pop(0)[1])
#         return {"node_type": "float_literal", "value": value}
#
#     if tokens[0][0] == "STRING":
#         value = tokens.pop(0)[1].strip('"')
#         return {"node_type": "string_literal", "value": value}
#
#     if tokens[0][0] == "IDENTIFIER":
#         name = tokens.pop(0)[1]
#         return {"node_type": "variable", "name": name}
#
#     raise ValueError(f"Invalid expression at position {tokens[0][2]}")

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

    while tokens and tokens[0][0] in ["MULTIPLY", "DIVIDE"]:
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

    raise ValueError(f"Invalid expression at position {tokens[0][2]}")

def parse_statement(tokens):
    if tokens[0][0] == "PRINT":
        tokens.pop(0)  # Skip the 'print' token

        expression = parse_expression(tokens)

        return {"node_type": "print_statement", "expression": expression}

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

    return {"node_type": "assignment_statement", "variable_name": "", "expression": ""}


def parse__black_hole(tokens):
    # Parse method parameters
    parameters = []
    tokens.pop(0)  # Skip the opening parenthesis token
    while tokens[0][0] != "RPAREN":
        token = tokens.pop(0)

        if token[0] == "IDENTIFIER":
            parameter_name = token[1]  # Get the parameter name token

            tokens.pop(0)  # Skip the colon token
            parameter_type = tokens.pop(0)[1]  # Get the parameter type token

            parameter = {
                "node_type": "parameter",
                "parameter_name": parameter_name,
                "parameter_type": parameter_type,
            }
            parameters.append(parameter)

    tokens.pop(0)  # Skip the closing parenthesis token
    tokens.pop(0)  # Skip the opening brace token

    while tokens[0][0] != "RBRACE":
        tokens.pop(0)
    # Parse method body
    body = "" #parse_statement(tokens)

    tokens.pop(0)  # Skip the closing brace token

    return {
        "node_type": "black_hole_declaration",
        "method_name": "black_hole",
        "parameters": parameters,
        "body": body,
    }


def parse_star_system(tokens):
    method_name = tokens.pop(0)[1]  # Get the method name token
    # Parse method parameters
    parameters = []
    tokens.pop(0)  # Skip the opening parenthesis token
    while tokens[0][0] != "RPAREN":
        token = tokens.pop(0)

        if token[0] == "IDENTIFIER":
            parameter_name = token[1]  # Get the parameter name token

            tokens.pop(0)  # Skip the colon token
            parameter_type = tokens.pop(0)[1]  # Get the parameter type token

            parameter = {
                "node_type": "parameter",
                "parameter_name": parameter_name,
                "parameter_type": parameter_type,
            }
            parameters.append(parameter)

    tokens.pop(0)  # Skip the closing parenthesis token
    tokens.pop(0)  # Skip the opening brace token

    while tokens[0][0] != "RBRACE":
        tokens.pop(0)
    # Parse method body
    body = "" #parse_statement(tokens)

    tokens.pop(0)  # Skip the closing brace token

    return {
        "node_type": "method_declaration",
        "method_name": method_name,
        "parameters": parameters,
        "body": body,
    }


def parse_galaxy(tokens):
    galaxy_name = tokens.pop(0)[1]  # Get the galaxy name token

    # Parse base classes if present
    base_classes = []
    if tokens[0][0] == "LPAREN":
        tokens.pop(0)  # Skip the opening parenthesis token
        while tokens[0][0] != "RPAREN":
            base_class_name = tokens.pop(0)[1]  # Get the base class name token
            base_classes.append(base_class_name)
            if tokens[0][0] == "COMMA":
                tokens.pop(0)  # Skip the comma token
        tokens.pop(0)  # Skip the closing parenthesis token
    else:
        raise ValueError(f"Expected '(' after Galaxy name, received {tokens[0][0]}")

    # Parse class body
    body = []
    if not tokens[0][0] == "LBRACE":
        raise ValueError(f"Expected '{{', received {tokens[0][0]}")
    else:
        tokens.pop(0)  # Skip the opening brace token

    while tokens[0][0] != "RBRACE":
        token = tokens.pop(0)

        if token[0] in ("COMET", "PLANET", "ASTEROID"):
            # Parse variable declaration
            variable_declaration = parse_variable_declaration(tokens)
            body.append(variable_declaration)

        elif token[0] == "BLACK_HOLE":
            # parse method declaration
            method_declaration = parse__black_hole(tokens)
            body.append(method_declaration)

        elif token[0] == "STAR_SYSTEM":
            # parse method declaration
            method_declaration = parse_star_system(tokens)
            body.append(method_declaration)

    tokens.pop(0)  # Skip the closing brace token

    return {
        "node_type": "galaxy_declaration",
        "class_name": galaxy_name,
        "base_classes": base_classes,
        "body": body,
    }


def parse_program(tokens):
    program = []

    while tokens:
        token, value = tokens[0][0], tokens[0][1]
        if token == "GALAXY":
            tokens.pop(0)
            galaxy = parse_galaxy(tokens)
            # galaxy = parse_galaxy(tokens)
            program.append(galaxy)
        else:
            a = parse_statement(tokens)
            program.append(a)

    return program
