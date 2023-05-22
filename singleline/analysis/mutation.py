from _ast import ClassDef, Name
import ast
from typing import Any, List, Set

from ..misc import get_params
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

    scope: List[Set[str]]

    # TODO: add func def, class def, etc

    def __init__(self) -> None:
        self.scope = []

    def visit_For(self, node: ast.For) -> Any:
        targets = [node.target] if isinstance(targets, ast.Name) else node.target
        mutated_vars = {i.id for i in targets}

        self._collect_mutations(mutated_vars, node, True)
        return self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        self._collect_mutations(set(), node, True)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        if self.scope:
            self.scope[-1].add(node.name)

        mutated_vars = get_params(node)
        self._collect_mutations(mutated_vars, node)
    
    def visit_Name(self, node: Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.scope[-1].add(node.id)

    def _collect_mutations(
        self, mutated_vars: Set[str], node: ast.AST, propagate: bool = False
    ) -> None:
        self.scope.append(mutated_vars)
        self.generic_visit(node)
        self.scope.pop()

        node.mutated_vars = mutated_vars

        # Propagate mutated variables to parent scope.
        if propagate and self.scope:
            self.scope[-1].update(mutated_vars)
