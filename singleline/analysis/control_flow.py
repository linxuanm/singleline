import ast
import networkx as nx
from typing import List, Hashable

from ..misc.types import VRet


# A hashable wrapper for `List[ast.AST]`.
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

    @staticmethod
    def _flatten(xs: any) -> List[any]:
        res = []
        for x in xs:
            if isinstance(x, list):
                res.extend(NodeBundle.flatten(x))
            else:
                res.append(x)

        return res


class ControlFlowGraph:
    """
    Generates the control flow graph of the source program so that lambda
    and branching structures can be determined statically.
    """

    graph: nx.classes.DiGraph

    def __init__(self):
        self.graph = nx.classes.DiGraph()

        # entry point
        self.graph.add_node('main')

    def analysis_pass(self, code: List[ast.AST], prev: Hashable = 'main'):
        batch = NodeBundle()
        for node in code:
            if ControlFlowGraph._is_compound_node(node):
                break

            batch.append(node)

        batch.flatten()
        # self.graph.add_node

    @staticmethod
    def _is_compound_node(node: ast.AST):
        types = [ast.If, ast.For, ast.While]
        return not any(isinstance(node, t) for t in types)
