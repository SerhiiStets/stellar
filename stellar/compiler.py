from pprint import pprint
import llvmlite.binding as llvm
import llvmlite.ir as ir
from ctypes import CFUNCTYPE, c_double


def save_to_assembly(module):
    with open('output.ll', 'w') as f:
        f.write(str(module))

def save_to_exe(module):
    target_machine = llvm.Target.from_default_triple().create_target_machine()
    with open('output.exe', 'wb') as f:
        f.write(target_machine.emit_object(module))

def save_to_bitcode(module):
    with open('output.bc', 'wb') as f:
        f.write(module.to_bitcode())

def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine

def compile_ir(engine, llvm_ir):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a LLVM module object from the IR
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    # Now add the module and make sure it is ready for execution
    engine.add_module(mod)
    engine.finalize_object()
    engine.run_static_constructors()
    return mod

# Usefull types
double = ir.DoubleType()
fnty = ir.FunctionType(double, (double, double))

def compile():
    # Step 1: Define LLVM modules and functions
    module = ir.Module(name=__file__)
    # main_func = ir.Function(module, ir.FunctionType(double, []), name="main")
    main_func = ir.Function(module, ir.FunctionType(ir.VoidType(), []), name="main")
    

    entry_block = main_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry_block)

    a = builder.alloca(ir.DoubleType(), name="a")
    value = builder.fadd(ir.Constant(ir.DoubleType(), 1), ir.Constant(ir.DoubleType(), 1))
    value = builder.fmul(value, ir.Constant(ir.DoubleType(), 3))
    value = builder.fsub(value, ir.Constant(ir.DoubleType(), 2))

    builder.store(value, a)
    builder.ret_void()

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()  # yes, even this one

    engine = create_execution_engine()

    print(str(module))

    compile_ir(engine, str(module))

    save_to_assembly(module)

    func_ptr = engine.get_function_address("main")

    # Run the function via ctypes
    cfunc = CFUNCTYPE(None)(func_ptr)
    cfunc()

def compile_stellar(llvm_module: str):
    # # Step 1: Define LLVM modules and functions
    # module = ir.Module(name=__file__)
    # # main_func = ir.Function(module, ir.FunctionType(double, []), name="main")
    # main_func = ir.Function(module, ir.FunctionType(ir.VoidType(), []), name="main")
    # 
    #
    # entry_block = main_func.append_basic_block(name="entry")
    # builder = ir.IRBuilder(entry_block)
    #
    # a = builder.alloca(ir.DoubleType(), name="a")
    # value = builder.fadd(ir.Constant(ir.DoubleType(), 1), ir.Constant(ir.DoubleType(), 1))
    # value = builder.fmul(value, ir.Constant(ir.DoubleType(), 3))
    # value = builder.fsub(value, ir.Constant(ir.DoubleType(), 2))
    #
    # builder.store(value, a)
    # builder.ret_void()

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()  # yes, even this one

    engine = create_execution_engine()

    compile_ir(engine, str(llvm_module))

    save_to_assembly(llvm_module)

    func_ptr = engine.get_function_address("main")

    # Run the function via ctypes
    cfunc = CFUNCTYPE(None)(func_ptr)
    cfunc()

if __name__ == "__main__":
    compile()
