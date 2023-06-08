from os import name
from os.path import expanduser
from llvmlite import ir


VOID_POINTER = ir.IntType(8).as_pointer()

bool_t = ir.IntType(1)
int8_t = ir.IntType(8)
int32_t = ir.IntType(32)
voidptr_t = int8_t.as_pointer()

true_bit = bool_t(1)
false_bit = bool_t(0)
true_byte = int8_t(1)
false_byte = int8_t(0)

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
    
    def make_bytearray(self, buf):
        """
        Make a byte array constant from *buf*.
        """
        b = bytearray(buf)
        n = len(b)
        return ir.Constant(ir.ArrayType(ir.IntType(8), n), b)

    def add_global_variable(self, ty, name, addrspace=0):
        unique_name = self.module.get_unique_name(name)
        return ir.GlobalVariable(self.module, ty, unique_name, addrspace)

    def global_constant(self, builder_or_module, name, value, linkage='internal'):
        """
        Get or create a (LLVM module-)global constant with *name* or *value*.
        """
        if isinstance(builder_or_module, ir.Module):
            module = builder_or_module
        else:
            module = builder_or_module.module
        data = module.add_global_variable(value.type, name=name)
        data.linkage = linkage
        data.global_constant = True
        data.initializer = value
        return data

    def printf(self, format, *args):
        """
        Calls printf().
        Argument `format` is expected to be a Python string.
        Values to be printed are listed in `args`.

        Note: There is no checking to ensure there is correct number of values
        in `args` and there type matches the declaration in the format string.
        """
        assert isinstance(format, str)
        mod = self.builder.module
        # Make global constant for format string
        cstring = voidptr_t
        fmt_bytes = self.make_bytearray((format + '\00').encode('ascii'))

        global_fmt = self.add_global_variable("printf_format", fmt_bytes) #ir.GlobalValue(self.module, fmt_bytes.type, name="printf_format")
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = fmt_bytes


        # global_fmt = self.global_constant(mod, "printf_format", fmt_bytes)
        fnty = ir.FunctionType(int32_t, [cstring], var_arg=True)
        # Insert printf()
        try:
            fn = mod.get_global('printf')
        except KeyError:
            fn = ir.Function(mod, fnty, name="printf")
        # Call
        ptr_fmt = self.builder.bitcast(global_fmt, cstring)
        return self.builder.call(fn, [ptr_fmt] + list(args))

    def print(self, expression):
        fmt = "%d\n"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode('utf8')))
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        printf_ty = ir.FunctionType(ir.IntType(8), [VOID_POINTER], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")
        fmt_arg = self.builder.bitcast(global_fmt, VOID_POINTER)
        var = expression["name"]
        print(self.variables[var])
        self.builder.call(printf, [fmt_arg, self.variables[var]])

    def printf_c(self, expression):
        # Step 1: Create the format string constant
        format_str = "%d\n"  # Example format string for printing an integer

        format_str_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(format_str)), bytearray(format_str.encode('utf8')))
        format_str_global = ir.GlobalVariable(self.module, format_str_const.type, name="format_str")
        format_str_global.linkage = "internal"
        format_str_global.global_constant = True
        format_str_global.initializer = format_str_const

        # Step 2: Load the printf function
        printf_func = ir.Function(self.module,
            ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True),
            name="printf"
        )

        format_str_ptr = self.builder.bitcast(format_str_global, VOID_POINTER)

        self.builder.call(printf_func, [format_str_ptr, self.builder.load(self.variables[expression])])

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
            return self.builder.load(self.variables[node["name"]])
        else:
            result = None
        return result
        # return result
        
    # full ast;
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
                    if  expression:
                        result = self.parse_node(expression)
                        self.builder.store(result, variable)
                    self.variables[variable_name] = variable

                elif node_type == "assignment_statement":
                    variable_name = node["variable_name"]
                    expression = node["expression"]

                    # Generate LLVM IR code for the expression
                    result = self.parse_node(expression)
                    
                    # Create a new LLVM variable
                    # variable = self.builder.alloca(ir.IntType(32), name=variable_name)
                    self.builder.store(result, self.variables[variable_name])
                    # # Store the variable value in the dictionary
                    # self.variables[variable_name] = variable
                elif node_type == "print_statement":
                    var_name = node["expression"]["name"]
                    self.printf_c(var_name)
        #        
        #
        #
        # if isinstance(node, dict):
        #     if node_type == "variable_declaration":
        #         variable_name = node["variable_name"]
        #         variable_type = node["variable_type"]
        #         expression = node["expression"]
        #         result = self.generate_llvm_ir(expression)
        #         # TODO types
        #         variable = self.builder.alloca(ir.IntType(32), name=variable_name)
        #         if expression:
        #             self.builder.store(result, variable)
        #
        #     elif node_type == "assignment_statement":
        #         variable_name = node["variable_name"]
        #         expression = node["expression"]
        #
        #         # Generate LLVM IR code for the expression
        #         result = self.generate_llvm_ir(expression)
        #         
        #         # Create a new LLVM variable
        #         # variable = self.builder.alloca(ir.IntType(32), name=variable_name)
        #         self.builder.store(result, self.variables[variable_name])
        #         # # Store the variable value in the dictionary
        #         # self.variables[variable_name] = variable
        #
        #     elif node_type == "binary_operation":
        #         operator = node["operator"]
        #         left_operand = node["left_operand"]
        #         right_operand = node["right_operand"]
        #
        #         # Generate LLVM IR code for the left and right operands
        #         left_value = self.generate_llvm_ir(left_operand)
        #         right_value = self.generate_llvm_ir(right_operand)
        #         # Perform the binary operation based on the operator
        #         if operator == "PLUS":
        #             result = self.builder.add(left_value, right_value)
        #         elif operator == "MINUS":
        #             result = self.builder.sub(left_value, right_value)
        #         elif operator == "MULTIPLY":
        #             result = self.builder.mul(left_value, right_value)
        #         elif operator == "DIVIDE":
        #             result = self.builder.sdiv(left_value, right_value)
        #         else:
        #             raise ValueError(f"Invalid operator: {operator}")
        #         return result
        #     
        #     elif node_type == "integer_literal":
        #         return ir.Constant(ir.IntType(32), node["value"])
        #     elif node_type == "print_statement":
        #         # TODO expression
        #         # self.print(node["expression"])
        #         self.printf("%d\n", self.variables[node["expression"]["name"]])
        #         return 
        #
        # elif isinstance(node, list):
        #     # Traverse nested lists recursively
        #     for item in node:
        #         result = self.generate_llvm_ir(item)
        # # Handle other types or unsupported cases
        # return result 


    def _generate_llvm_ir(self, node):
        if isinstance(node, dict):
            node_type = node["node_type"]
            if node_type == "variable_declaration":
                variable_name = node["variable_name"]
                variable_type = node["variable_type"]
                expression = node["expression"]
                result = self.generate_llvm_ir(expression)
                # TODO types
                variable = self.builder.alloca(ir.IntType(32), name=variable_name)
                if expression:
                    self.builder.store(result, variable)

            elif node_type == "assignment_statement":
                variable_name = node["variable_name"]
                expression = node["expression"]

                # Generate LLVM IR code for the expression
                result = self.generate_llvm_ir(expression)
                
                # Create a new LLVM variable
                # variable = self.builder.alloca(ir.IntType(32), name=variable_name)
                self.builder.store(result, self.variables[variable_name])
                # # Store the variable value in the dictionary
                # self.variables[variable_name] = variable

            elif node_type == "binary_operation":
                print(node)
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
            
            elif node_type == "integer_literal":
                return ir.Constant(ir.IntType(32), node["value"])
            elif node_type == "print_statement":
                # TODO expression
                # self.print(node["expression"])
                self.printf("%d\n", self.variables[node["expression"]["name"]])
                return 

        elif isinstance(node, list):
            # Traverse nested lists recursively
            for item in node:
                result = self.generate_llvm_ir(item)
        # Handle other types or unsupported cases
        return result 

