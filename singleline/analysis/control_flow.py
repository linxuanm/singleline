import ast
import networkx as nx
from typing import List

from ..misc.types import VRet


# A hashable wrapper for `List[ast.AST]`.
class NodeBundle:

    bundle: List[ast.AST]

    def __init__(self, bundle: List[ast.AST] = None):
        if bundle is None: bundle = []

        self.bundle = bundle

    def append(self, node: ast.AST):
        self.bundle.append(node)


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

    def analysis_pass(self, code: List[ast.AST]):
        batch = NodeBundle()
        for node in code:
            pass

    def _is_compound_node(self, node: ast.AST):
        types = [ast.If, ast.For, ast.While]
