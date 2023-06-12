from abc import ABC, abstractmethod


class Analyzer(ABC):
    @abstractmethod
    def traverse(self, node):
        pass


class SemanticAnalyzer(Analyzer):
    def __init__(self, ast) -> None:
        self.ast = ast
        self.var_scope_table: dict = {}

    def analyze(self):
        self.traverse(self.ast)

    def traverse(self, node):
        if isinstance(node, dict):
            node_type = node["node_type"]

            if node_type == "variable_declaration":
                self.analyze_variable_declaration(node)
            elif node_type == "assignment_statement":
                self.analyze_assignment(node)
            #
            # if "expression" in node.keys():
            #     self.traverse(node["expression"])

        elif isinstance(node, list):
            for el in node:
                self.traverse(el)

    def analyze_variable_declaration(self, node):
        variable_name = node["variable_name"]
        variable_type = node["variable_type"]
        self.var_scope_table[variable_name] = {"type": variable_type}
        # TODO better solution
        # Very complicated and not really readable
        if "expression" in node.keys():
            if node["expression"]:
                self.analyze_expression(node["expression"], variable_type)
        elif "left_operand" in node.keys():
            self.analyze_expression(node["left_operand"], variable_type)
            self.analyze_expression(node["right_operand"], variable_type)

    def analyze_assignment(self, node):
        variable_name = node["variable_name"]

        # If var is assigned however nor inialized before
        # raise error
        if variable_name not in self.var_scope_table.keys():
            # TODO
            raise RuntimeError()
        variable_type = self.var_scope_table[variable_name]["type"]
        if "expression" in node.keys():
            self.analyze_expression(node["expression"], variable_type)
        elif "left_operand" in node.keys():
            self.analyze_expression(node["left_operand"], variable_type)
            self.analyze_expression(node["right_operand"], variable_type)

    def analyze_expression(self, node, check_type=None):
        node_type = node["node_type"]
        # For variables
        if node_type == "variable":
            if node["name"] not in self.var_scope_table.keys():
                # TODO
                raise RuntimeError()
            if check_type:
                if self.var_scope_table[node["name"]]["type"] != check_type:
                    # TODO
                    raise RuntimeError()
        # For literals like (3, "a", 4.5)
        elif "value" in node.keys():
            if node_type != check_type:
                # TODO
                raise RuntimeError()
        elif node_type == "LIST":
            self.analyze_list(node["expression"])
            # TODO im not sure return here would travest all possible scenarios
            # for ast tree in expression
            return

        # Continue parsing if expression tree is not empty
        if "expression" in node.keys():
            self.analyze_expression(node["expression"], check_type)
        elif "left_operand" in node.keys():
            self.analyze_expression(node["left_operand"], check_type)
            self.analyze_expression(node["right_operand"], check_type)

    def analyze_list(self, node):
        types = []
        for el in node:
            if not types:
                types.append(el["node_type"])
            if el["node_type"] not in types:
                # TODO
                raise RuntimeError()
