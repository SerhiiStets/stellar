from llvmlite import ir


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

    def generate_llvm_ir(self, node):
        if isinstance(node, dict):
            if node["node_type"] == "assignment_statement":
                variable_name = node["variable_name"]
                expression = node["expression"]

                # Generate LLVM IR code for the expression
                result = self.generate_llvm_ir(expression)

                # Create a new LLVM variable
                variable = self.builder.alloca(ir.IntType(32), name=variable_name)
                self.builder.store(result, variable)

                # Store the variable value in the dictionary
                self.variables[variable_name] = variable

            elif node["node_type"] == "binary_operation":
                operator = node["operator"]
                left_operand = node["left_operand"]
                right_operand = node["right_operand"]

                # Generate LLVM IR code for the left and right operands
                left_value = self.generate_llvm_ir(left_operand)
                right_value = self.generate_llvm_ir(right_operand)
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

                return result

            elif node["node_type"] == "integer_literal":
                return ir.Constant(ir.IntType(32), node["value"])

            # Handle other node types here

            # Traverse nested dictionary values recursively
            for value in node.values():
                result = self.generate_llvm_ir(value)
                if result is not None:
                    return result

        elif isinstance(node, list):
            # Traverse nested lists recursively
            for item in node:
                result = self.generate_llvm_ir(item)
                if result is not None:
                    return result

        # Handle other types or unsupported cases
        return None

