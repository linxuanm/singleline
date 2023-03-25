
import ast
from typing import Tuple

from .analysis import PreprocessTransformer, CFGVisitor
from .misc import IdentifierGenerator


def load_program(program: str) -> Tuple[ast.AST, IdentifierGenerator]:
    """
    Parses and preprocesses a program. Also returns its name generator.
    """

    tree = ast.parse(program)
    preprocessor = PreprocessTransformer()
    tree = preprocessor.visit(tree)

    # reloads to automatically update line numbers and other attributes
    # TODO: check if this is needed
    print(ast.unparse(tree))
    tree = ast.parse(ast.unparse(tree))

    cfg = CFGVisitor()
    cfg.visit(tree)

    return tree
