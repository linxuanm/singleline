import ast
from typing import List

from ..misc.types import VRet


# TODO: Rewrite this part with a concrete graph representation so that the
# transpiling process can be written as a structure-directed translation
# rather than the current "based on random and arbitrary heuistics" translation.

# Currently this is the only static analysis pass.
# The various attributes associated with each `ast.AST` defines the control
# flow graph in the imaginery IR (see the `.ipynb` files for more technical
# details).
class CFGVisitor(ast.NodeVisitor):
    """
    Generates the control flow graph of the source program so that lambda
    and branching structures can be determined statically.
    """

    # A stack of entered loops (to link `break` and `continue` statements).
    loop_stack: List[ast.AST]
    # Each `while` and `for` introduces a new "loop scope" to track `break`.
    loop_scope: List[List[ast.AST]]
    # Denotes whether the module has an explicit return statement.
    has_return: bool

    def __init__(self):
        self.curr_node = None
        self.loop_stack = []
        self.loop_scope = [[]]
        self.has_return = False

    def visit_For(self, node: ast.For) -> VRet:
        node.has_break = False
        
        self.loop_stack.append(node)
        self.loop_scope.append([])
        self.generic_visit(node)
        self.loop_scope.pop()
        self.loop_stack.pop()

    def visit_While(self, node: ast.AST) -> VRet:
        node.has_break = False

        self.loop_stack.append(node)
        self.loop_scope.append([])
        self.generic_visit(node)
        self.loop_scope.pop()
        self.loop_stack.pop()

    def visit_If(self, node: ast.If) -> VRet:
        node.has_break = False

        assert len(self.loop_scope) != 0
        self.loop_scope[-1].append(node)
        self.generic_visit(node)
        self.loop_scope[-1].pop()

    def visit_Break(self, node: ast.Break) -> VRet:
        assert len(self.loop_stack) != 0
        self.loop_stack[-1].has_break = True

        assert len(self.loop_scope) != 0
        for i in self.loop_scope[-1]:
            i.has_break = True

        self.generic_visit(node)

    def visit_Continue(self, node: ast.Continue) -> VRet:
        assert len(self.loop_stack) != 0
        self.loop_stack[-1].has_break = True

        assert len(self.loop_scope) != 0
        for i in self.loop_scope[-1]:
            i.has_break = True

        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> VRet:
        self.has_return = True

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> VRet:
        sub_cfg = CFGVisitor()
        sub_cfg.generic_visit(node)
        node.has_return = sub_cfg.has_return
