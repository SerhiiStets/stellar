from ctypes import CFUNCTYPE

import llvmlite.binding as llvm


class StellarCompiler:
    def __init__(self, llvm_module: str) -> None:
        self.llvm_module = llvm_module

    def _save_to_exe(self, module):
        target_machine = llvm.Target.from_default_triple().create_target_machine()
        with open("output.exe", "wb") as f:
            f.write(target_machine.emit_object(module))

    def _save_to_bitcode(self, module):
        with open("output.bc", "wb") as f:
            f.write(module.to_bitcode())

    def _save_to_assembly(self, module):
        with open("output.ll", "w") as f:
            f.write(str(module))

    def _create_execution_engine(self):
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

    def _compile_ir(self, engine, llvm_ir):
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

    def compile(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()  # yes, even this one

        engine = self._create_execution_engine()

        self._compile_ir(engine, self.llvm_module)

        self._save_to_assembly(self.llvm_module)

        func_ptr = engine.get_function_address("main")

        # Run the function via ctypes
        cfunc = CFUNCTYPE(None)(func_ptr)
        cfunc()
