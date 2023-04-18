# Utility code for performing replacing operation on source code.

import ast
from typing import List, Set

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

    def __init__(self) -> None:
        self.scope = []

    def visit_For(self, node: ast.For) -> None:
        targets = [node.target] if isinstance(targets, ast.Name) else node.target
        mutated_vars = {i.id for i in targets}

        self._collect_mutations(mutated_vars, node, True)

    def visit_While(self, node: ast.While) -> None:
        self._collect_mutations(set(), node, True)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        all_args = node.args.args + node.args.kwonlyargs

        if hasattr(node.args, 'posonlyargs'):
            all_args += node.args.posonlyargs

        if node.args.vararg is not None:
            all_args.append(node.args.vararg)

        if node.args.kwarg is not None:
            all_args.append(node.args.kwarg)

        mutated_vars = {i.arg for i in all_args}
        self._collect_mutations(mutated_vars, node)

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
