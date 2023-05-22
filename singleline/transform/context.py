from _ast import For, Name
import ast
from typing import Any, Set


class LocalVariableVisitor(ast.NodeVisitor):
    """
    Responsible for keeping track of the defined local variables within a scope.
    This is used in conjunction with mutated variable analysis during loop
    transpilation to identify the variables that needs to be stored.

    Unlike `MutationRecorder`, this class keeps a record on-the-fly as the
    relevant scope is scanned, and is a more generalized version of mutation
    recording that does not treat loops as different scopes.

    The transpiled loop representation is as follow:

    1. Find all mutated variables in the loop. For the ones that are contained
    in `LocalVariableVisitor` before the loop, initialize the store list to
    their value. Otherwise, set their initial value to `None`.
    2. 
    """

    vars: Set[str]

    def __init__(self):
        self.vars = set()

    def visit_Name(self, node: Name) -> Any:
        if isinstance(node.ctx, ast.Store):
            self.vars.add(node.id)
        
        return self.generic_visit(node)

    def visit_For(self, node: For) -> Any:
        pass