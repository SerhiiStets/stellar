from llvmlite import ir

bool_t = ir.IntType(1)
int8 = ir.IntType(8)
int32 = ir.IntType(32)
void_pointer = ir.IntType(8).as_pointer()

true_bit = bool_t(1)
false_bit = bool_t(0)
true_byte = int8(1)
false_byte = int8(0)

PRINT_MAP = {
    "INT": "%d",
    "STR": "%s",
}

TYPE_MAP = {"INT": int32, "BOOL": bool_t}

class LlvmGenerator:
    def __init__(self, node) -> None:
        # Create a new LLVM module
        self.module = ir.Module()

        # Create a new LLVM function
        self.function_type = ir.FunctionType(ir.VoidType(), [])
        self.function = ir.Function(self.module, self.function_type, name="main")
        self.block = self.function.append_basic_block(name="entry")

        # Create a new LLVM builder
        self.builder = ir.IRBuilder(self.block)

        # Define a dictionary to store variable values
        self.variables = {}
        self.node = node
        self.generate_llvm_ir(node)

        self.builder.ret_void()

    def printf(self, expression):
        if not len(expression):
            pass

        elif expression["node_type"] == "variable":
            variable_name = expression["name"]
            variable = self.variables[variable_name]
            variable_type = variable["type"]

            format_str = f"{PRINT_MAP[variable_type]}\n"

            format_str_const = ir.Constant(
                ir.ArrayType(int8, len(format_str)),
                bytearray(format_str.encode("utf8")),
            )
            format_str_global = ir.GlobalVariable(
                self.module, format_str_const.type, name="format_str"
            )
            format_str_global.linkage = "internal"
            format_str_global.global_constant = True
            format_str_global.initializer = format_str_const

            # Load the printf function
            printf_func = ir.Function(
                self.module,
                ir.FunctionType(int32, [void_pointer], var_arg=True),
                name="printf",
            )

            # Create a pointer to the format string
            format_str_ptr = self.builder.bitcast(format_str_global, void_pointer)

            self.builder.call(
                printf_func, [format_str_ptr, self.builder.load(variable["var"])]
            )
        elif expression["node_type"] in PRINT_MAP:
            pass

    def parse_node(self, node):
        if node["node_type"] == "binary_operation":
            operator = node["operator"]
            left_operand = node["left_operand"]
            right_operand = node["right_operand"]

            # Generate LLVM IR code for the left and right operands
            left_value = self.parse_node(left_operand)

            right_value = self.parse_node(right_operand)
            # Perform the binary operation based on the operator
            if operator == "PLUS":
                result = self.builder.add(left_value, right_value)
            elif operator == "MINUS":
                result = self.builder.sub(left_value, right_value)
            elif operator == "MULTIPLY":
                result = self.builder.mul(left_value, right_value)
            elif operator == "DIVIDE":
                result = self.builder.sdiv(left_value, right_value)
            else:
                raise ValueError(f"Invalid operator: {operator}")
        elif node["node_type"] == "INT":
            return ir.Constant(ir.IntType(32), node["value"])
        elif node["node_type"] == "variable":
            return self.builder.load(self.variables[node["name"]]["var"])
        else:
            result = None
        return result

    def generate_llvm_ir(self, tree):
        if isinstance(tree, list):
            for node in tree:
                node_type = node["node_type"]
                if node_type == "variable_declaration":
                    variable_name = node["variable_name"]
                    variable_type = node["variable_type"]
                    expression = node["expression"]
                    # TODO types
                    variable = self.builder.alloca(ir.IntType(32), name=variable_name)
                    if expression:
                        result = self.parse_node(expression)
                        self.builder.store(result, variable)
                    self.variables[variable_name] = {
                        "type": variable_type,
                        "var": variable,
                    }

                elif node_type == "assignment_statement":
                    variable_name = node["variable_name"]
                    expression = node["expression"]

                    # Generate LLVM IR code for the expression
                    result = self.parse_node(expression)

                    # Create a new LLVM variable
                    self.builder.store(result, self.variables[variable_name]["var"])
                elif node_type == "print_statement":
                    expression = node["expression"]
                    self.printf(expression)
        elif isinstance(tree, dict):
            # TODO
            pass
