import ast
from enum import Enum, auto
from typing import List


class CFGLabels(Enum):
    """
    An enumeration of all possible labels in case a branching occurs at
    a node in the CFG.

    For instance, the `ast.If` node can have two outgoing edges labeled
    as `CFGLabels.IF` and `CFGLabels.ELSE`.
    """

    IF = auto() # `if` statement
    ELSE = auto() # `if` statement
    RET_FLAG = auto() # loops
    CONTENT = auto() # content of `ast.FunctionDef` or `ast.Module`
    IGNORE = auto() # loop interior, ignore during interrupt tracing


# A hashable wrapper for `List[ast.AST]`.
# TODO: fix the types that involves `NodeBundle` (currently incorrect)
class NodeBundle:

    bundle: List[ast.AST]

    def __init__(self, bundle: List[ast.AST] = None):
        if bundle is None: bundle = []

        self.bundle = bundle

    def append(self, node: ast.AST):
        self.bundle.append(node)

    def flatten(self):
        self.bundle = NodeBundle._flatten(self.bundle)

    def is_empty(self) -> bool:
        return len(self.bundle) == 0
    
    def __repr__(self) -> str:
        return '<NodeBundle: [{}]>'.format(
            ', '.join(ast.unparse(i) for i in self.bundle)
        )

    @staticmethod
    def _flatten(xs: any) -> List[any]:
        res = []
        for x in xs:
            if isinstance(x, list):
                res.extend(NodeBundle.flatten(x))
            else:
                res.append(x)

        return res
    