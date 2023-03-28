import ast
import networkx as nx
from typing import List, Tuple

from ..misc.types import VRet


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

    def _analysis_pass(self, code: List[ast.AST]) -> Tuple(ast.AST, [ast.AST]):
        """
        Builds the control flow graph for a portion of code.

        Returns a tuple:
            - fst: the first node of the sub-graph representing the give code
            - snd: a list of all the possible ending nodes of the sub-graph

        Note that if a branch of the graph ends in a `return`, `break` or `continue`,
        it is treated as a "dead-end" ad will not be included in the out-flowing nodes
        of the sub-graph (i.e., the second value of the returned tuple).
        """

        code_segments = [NodeBundle()]
        for node in code:
            if ControlFlowGraph._is_compound_node(node):
                code_segments.append(node)
                code_segments.append(NodeBundle())
            else:
                code_segments[-1].append(node)

        blocks = [
            i for i in code_segments
            if not (isinstance(i, NodeBundle) and i.is_empty())
        ]

        first = None # Entry node for `code`.
        prev = None # Out-flowing nodes from the previous block.

        for i in blocks:
            pass

        # Dummy control-flow node.
        if first is None:
            node = NodeBundle()
            self.graph.add_node(node)
            return (node, [node])
        
        return (first, prev)

    @staticmethod
    def _is_compound_node(node: ast.AST):
        types = [ast.If, ast.For, ast.While]
        return not any(isinstance(node, t) for t in types)
