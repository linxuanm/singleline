import ast
from typing import List, Tuple

from ..misc.types import VRet


def has_interrupt(code: List[ast.AST]) -> Tuple[bool, bool]:
    visitor = InterruptVisitor()
    visitor.visit(code)

    return visitor.has_break, visitor.has_return


class InterruptVisitor(ast.NodeVisitor):
    """
    Responsible for determining various interrupt statements in an
    `ast.AST` and its children. It determines if an interrupt can be
    possibly reached in a control flow, and is used to generate the
    necessary flags for a loop.
    """

    has_return: bool
    has_break: bool
    func_stack: int
    loop_stack: int

    # Note that `has_continue` does not exist as it does not require an
    # external flag to be defined, and can be encoded in the `while` lambda
    # instead (by returning `False` to `f` in `next(filter(f, ...)))`.

    def __init__(self):
        self.has_return = False
        self.has_break = False
        self.func_stack = 0
        self.loop_stack = 0
    
    def visit_Return(self, node: ast.Return) -> VRet:
        if self.func_stack == 0:
            self.has_return = True

        self.generic_visit(node)

    def visit_Break(self, node: ast.Break) -> VRet:
        if self.loop_stack == 0:
            self.has_break = True

        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> VRet:
        self.func_stack += 1
        self.generic_visit(node)
        self.func_stack -= 1

    def visit_For(self, node: ast.For) -> VRet:
        self.loop_stack += 1
        self.generic_visit(node)
        self.loop_stack -= 1

    def visit_While(self, node: ast.While) -> VRet:
        self.loop_stack += 1
        self.generic_visit(node)
        self.loop_stack -= 1
