import os
import sys
from pprint import pprint

import compiler
import llvm_code_generator
import new_lexer
import new_parser


def process_file(file_path):
    with open(file_path, "r") as file:
        code = file.read()

        lexer = new_lexer.Lexer(code)
        tokens = lexer.parse()
        print(f"\n\nLexer:\n")
        pprint(tokens, sort_dicts=False)

        parser = new_parser.Parser(tokens)
        ast = parser.parse()
        print(f"\n\nParser:\n")
        pprint(ast, sort_dicts=False)

        llvm_generator = llvm_code_generator.LlvmGenerator(ast)
        print("\n\nCompiler:\n")
        print(llvm_generator.module)

        print("\nResult:")
        compiler.compile_stellar(str(llvm_generator.module))


def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".st"):
                file_path = os.path.join(root, file)
                process_file(file_path)


def main():
    # Check the command-line arguments
    if len(sys.argv) < 2:
        print("Please provide a file or directory path as an argument.")
        return

    path = sys.argv[1]

    if os.path.isfile(path):
        # If the provided path is a file, process it
        if path.endswith(".st"):
            process_file(path)
        else:
            raise Exception("Not a stellar file.")
    elif os.path.isdir(path):
        # TODO
        # If the provided path is a directory, process all files within it
        process_directory(path)
    else:
        print("Invalid path. Please provide a valid file or directory path.")


if __name__ == "__main__":
    main()
