# Utility code for performing replacing operation on source code.

import ast
from typing import List

from ..misc.types import VRet


class MutationRecorder(ast.NodeVisitor):
    """
    Records information associated with the mutation of variables in a
    given `ast.AST`. The relevant information are attached to instances
    of `ast.AST` in the form of attributes. Specifically, the following
    syntax tree nodes will receive mutation information:
    - Loops (to determine what to put in the loop's "variable store")
    - Function definitions (to deduce how far variable replacements should
    propagate in nested function definitions)

    Note that `MutationRecorder.visit` must be called with a node that is
    either a loop or a function definition when called externally.
    """

    scope: List[ast.AST]

    def __init__(self) -> None:
        self.scope = []

    def visit_For(self, node: ast.For) -> None:
        pass
