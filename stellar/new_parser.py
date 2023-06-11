from abc import ABC, abstractmethod

from new_lexer import Token

variables = {}


class BaseParser(ABC):
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.ast = []

    @abstractmethod
    def parse(self):
        ...


class Parser(BaseParser):
    def __init__(self, tokens: list[Token]) -> None:
        super().__init__(tokens)
        self.parsers = {
            "IDENTIFIER": AssignmentStatementParser,
            "PRINT": PrintParser,
        }

    def parse(self):
        while self.tokens:
            token_type = self.tokens[0].token_type
            if token_type in self.parsers:
                parser = self.parsers[token_type](self.tokens)
                self.ast.append(parser.parse())
                self.tokens.pop(0)
            else:
                # TODO
                parser = ParseNothing(self.tokens)
                self.tokens.pop(0)

        return self.ast


class AssignmentStatementParser(BaseParser):
    def parse(self):
        variable_name = self.tokens[0].pattern
        self.tokens.pop(0)

        if self.tokens[0].token_type == "EQUALS":
            self.tokens.pop(0)
            expression_parser = ExpressionParser(self.tokens)
            expression = expression_parser.parse()
            variables[variable_name]["expression"] = expression
            return {
                "node_type": "assignment_statement",
                "variable_name": variable_name,
                "expression": expression,
            }
        elif self.tokens[0].token_type == "COLON":
            self.tokens.pop(0)  # skip COLON
            variable_type_token = self.tokens.pop(0)
            expression = None
            if "TYPE_" in variable_type_token.token_type:
                variable_type = variable_type_token.token_type[5:]
            else:
                # TODO
                raise RuntimeError()

            if self.tokens[0].token_type == "EQUALS":
                self.tokens.pop(0)
                expression_parser = ExpressionParser(self.tokens)
                expression = expression_parser.parse()
            elif self.tokens[0].token_type != "SEMICOLON":
                # TODO
                raise RuntimeError()

            variables[variable_name] = {
                "variable_type": variable_type,
                "expression": expression,
            }
            return {
                "node_type": "variable_declaration",
                "variable_name": variable_name,
                "variable_type": variable_type,
                "expression": expression,
            }
        else:
            return []


class ExpressionParser(BaseParser):
    """Precedence climbing method."""

    def parse(self):
        left_parser = TermParser(self.tokens)
        left_operand = left_parser.parse()

        while (
            self.tokens
            and self.tokens[0].token_type in ["PLUS", "MINUS"]
            and self.tokens[0].token_type != "SEMICOLON"
            and self.tokens[0].token_type != "RPAREN"
        ):
            operator = self.tokens.pop(0).token_type
            right_parser = TermParser(self.tokens)
            right_operand = right_parser.parse()
            left_operand = {
                "node_type": "binary_operation",
                "operator": operator,
                "left_operand": left_operand,
                "right_operand": right_operand,
            }

        return left_operand


class TermParser(ExpressionParser):
    def parse(self):
        left_factor = FactorParser(self.tokens)
        left_operand = left_factor.parse()

        while (
            self.tokens
            and self.tokens[0].token_type in ["MULTIPLY", "DIVIDE"]
            and self.tokens[0].token_type != "SEMICOLON"
            and self.tokens[0].token_type != "RPAREN"
        ):
            operator = self.tokens.pop(0).token_type
            right_parser = FactorParser(self.tokens)
            right_operand = right_parser.parse()
            left_operand = {
                "node_type": "binary_operation",
                "operator": operator,
                "left_operand": left_operand,
                "right_operand": right_operand,
            }

        return left_operand


class FactorParser(ExpressionParser):
    def parse(self):
        if self.tokens[0].token_type == "LPAREN":
            self.tokens.pop(0)
            parser = ExpressionParser(self.tokens)
            expression = parser.parse()
            self.tokens.pop(0)
            return expression
        else:
            parser = PrimaryParser(self.tokens)
            return parser.parse()


class PrimaryParser(BaseParser):
    def parse(self):
        if self.tokens[0].token_type == "INTEGER":
            value = self.tokens.pop(0).pattern
            return {"node_type": "INT", "value": value}

        if self.tokens[0].token_type == "FLOAT":
            value = self.tokens.pop(0).pattern
            return {"node_type": "FLOAT", "value": value}

        if self.tokens[0].token_type == "STRING":
            value = self.tokens.pop(0).pattern
            return {"node_type": "STR", "value": value[1:-1]}

        if self.tokens[0].token_type == "IDENTIFIER":
            name = self.tokens.pop(0).pattern
            if name in variables:
                if variables[name]["expression"]:
                    return {"node_type": "variable", "name": name}
                else:
                    raise ValueError(f"{name} is delcared by no value assigned!")
            else:
                raise ValueError(f"{name} variable is not declared!")

        raise ValueError(f"Invalid expression at position {self.tokens[0]}")


class PrintParser(BaseParser):
    def parse(self):
        self.tokens.pop(0)  # pop print
        if self.tokens[0].token_type != "LPAREN":
            raise RuntimeError()

        expression_parser = ExpressionParser(self.tokens)
        expression = expression_parser.parse()
        return {"node_type": "print_statement", "expression": expression}


class ParseNothing(BaseParser):
    def parse(self):
        return []


if __name__ == "__main__":
    tokens = []
    a = Parser(tokens)
