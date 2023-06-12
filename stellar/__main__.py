import os
import sys
from pprint import pprint

import llvm_code_generator
import st_compiler
import st_lexer
import st_parser
import st_semantics


def process_file(file_path):
    with open(file_path, "r") as file:
        code = file.read()

        lexer = st_lexer.Lexer(code)
        tokens = lexer.parse()
        print("\n\nLexer:\n")
        pprint(tokens, sort_dicts=False)

        parser = st_parser.Parser(tokens)
        ast = parser.parse()
        print("\n\nParser:\n")
        pprint(ast, sort_dicts=False)

        semantic_analyzer = st_semantics.SemanticAnalyzer(ast)
        semantic_analyzer.analyze()

        llvm_generator = llvm_code_generator.LlvmGenerator(ast)
        print("\n\nCompiler:\n")
        print(llvm_generator.module)

        print("\nResult:")
        stellar_compiler = st_compiler.StellarCompiler(str(llvm_generator.module))
        stellar_compiler.compile()


def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".stl"):
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
        if path.endswith(".stl"):
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
