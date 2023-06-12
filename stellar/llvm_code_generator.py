from abc import ABC, abstractmethod

from llvmlite import ir

bool_t = ir.IntType(1)
int8 = ir.IntType(8)
int32 = ir.IntType(32)
flt32 = ir.FloatType()
flt64 = ir.DoubleType()
void_pointer = ir.IntType(8).as_pointer()

true_bit = bool_t(1)
false_bit = bool_t(0)
true_byte = int8(1)
false_byte = int8(0)

PRINT_MAP = {
    "INT": "%d",
    "STR": "%s",
    "FLOAT": "%f",
    # TODO list
}


class LlvmGenerator:
    def __init__(self, ast) -> None:
        self.ast = ast

        # Create a new LLVM module
        self.module = ir.Module()

        # Define a dictionary to store variable values
        self.variables: dict = {}

        # Create a new LLVM function
        self.function_type = ir.FunctionType(ir.VoidType(), [])
        self.function = ir.Function(self.module, self.function_type, name="main")
        self.block = self.function.append_basic_block(name="entry")

        # Create a new LLVM builder
        self.builder = ir.IRBuilder(self.block)

        # Load the printf function
        self.printf_func = ir.Function(
            self.module,
            ir.FunctionType(int32, [void_pointer], var_arg=True),
            name="printf",
        )

        self.generate_llvm_ir(self.ast)

        self.builder.ret_void()

    def printf(self, expression):
        if not len(expression):
            # TODO, print \n
            pass

        elif expression["node_type"] == "variable":
            variable_name = expression["name"]
            variable = self.variables[variable_name]
            variable_type = variable["type"]

            format_str = f"{PRINT_MAP[variable_type]}\n"

            format_str_ptr = Str(self.builder, format_str).get()

            self.builder.call(
                self.printf_func, [format_str_ptr, self.builder.load(variable["var"])]
            )
        elif expression["node_type"] in PRINT_MAP:
            format_str = f"{PRINT_MAP[expression['node_type']]}\n"
            format_str_ptr = Str(self.builder, format_str).get()

            value = VariableGeneratorFactory.create_generator(self.builder, expression)

            self.builder.call(self.printf_func, [format_str_ptr, value.get()])

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
        elif node["node_type"] in PRINT_MAP.keys():
            value = VariableGeneratorFactory.create_generator(self.builder, node)
            return value.get()
        elif node["node_type"] == "variable":
            return self.builder.load(self.variables[node["name"]]["var"])
        else:
            result = None
        return result

    def generate_llvm_ir(self, tree):
        for node in tree:
            node_type = node["node_type"]
            if node_type == "variable_declaration":
                variable_name = node["variable_name"]
                variable_type = node["variable_type"]
                expression = node["expression"]
                # TODO types
                if variable_type == "INT":
                    variable = self.builder.alloca(int32, name=variable_name)
                elif variable_type == "STR":
                    variable = self.builder.alloca(void_pointer, name=variable_name)
                elif variable_type == "FLOAT":
                    variable = self.builder.alloca(flt64, name=variable_name)
                elif variable_type == "LIST":
                    # TODO
                    continue
                else:
                    variable = None

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


class LLVMGenerator(ABC):
    @abstractmethod
    def get(self):
        ...


class VariableGeneratorFactory:
    @staticmethod
    def create_generator(builder, expression):
        if expression["node_type"] == "STR":
            return Str(builder, expression["value"])
        elif expression["node_type"] == "INT":
            return Int(expression["value"])
        elif expression["node_type"] == "FLOAT":
            return Float(expression["value"])
        else:
            # TODO
            raise ValueError(f"Unsupported node type: {expression['node_type']}")


class Str(LLVMGenerator):
    def __init__(self, builder: ir.IRBuilder, string: str) -> None:
        self.builder = builder
        self.string = string

    def get(self):
        # Create a local format string
        format_type = ir.ArrayType(int8, len(self.string) + 1)  # +1 for null terminator
        format_variable = self.builder.alloca(
            format_type
        )  # Allocate memory for the format string
        # Store each character of the format string in the allocated memory
        for i, char in enumerate(self.string):
            # Get the pointer to the i-th character in the format string
            ptr = self.builder.gep(
                format_variable, [ir.Constant(int32, 0), ir.Constant(int32, i)]
            )
            # Store the ASCII value of the character in the memory location
            self.builder.store(ir.Constant(int8, ord(char)), ptr)

        # Add a null terminator to the end of the format string
        ptr = self.builder.gep(
            format_variable,
            [ir.Constant(int32, 0), ir.Constant(int32, len(self.string))],
        )
        self.builder.store(ir.Constant(int8, 0), ptr)
        # Bitcast the format string variable to an i8* type and return it
        return self.builder.bitcast(format_variable, void_pointer)


class Float(LLVMGenerator):
    def __init__(self, flt) -> None:
        self.flt = flt

    def get(self) -> ir.Constant:
        return ir.Constant(flt64, self.flt)


class Int(LLVMGenerator):
    def __init__(self, integer) -> None:
        self.integer = integer

    def get(self) -> ir.Constant:
        return ir.Constant(int32, self.integer)


class List(LLVMGenerator):
    def get(self):
        pass


# class Printf:
#     def __init__(self, module: ir.Module, builder: ir.IRBuilder) -> None:
#         self.module = module
#         self.builder = builder
#         # Load the printf function
#         self.printf_func = ir.Function(
#             self.module,
#             ir.FunctionType(int32, [void_pointer], var_arg=True),
#             name="printf",
#         )
#
#     def __call__(self):
#         self.builder.call(self.printf_func, [a, self.builder.load(variable["var"])])
