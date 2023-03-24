import ast

from .analysis import PreprocessTransformer


def load_program(program: str):
    """
    Parses and preprocesses a program.
    """

    tree = ast.parse(program)
    preprocessor = PreprocessTransformer()
    tree = preprocessor.visit(tree)

    # reloads to automatically update line numbers and other attributes
    # TODO: check if this is needed
    print(ast.unparse(tree))
    tree = ast.parse(ast.unparse(tree))

    return tree

