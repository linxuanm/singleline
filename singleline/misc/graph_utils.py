import ast
import networkx as nx
from enum import Enum, auto
from typing import Set, Dict, List


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

    @staticmethod
    def _flatten(xs: any) -> List[any]:
        res = []
        for x in xs:
            if isinstance(x, list):
                res.extend(NodeBundle.flatten(x))
            else:
                res.append(x)

        return res
    

class DummyBundle(NodeBundle):
    """
    A dummy bundle that is non-empty but ignored during transpiling. Used
    as a placeholder node during graph construction and analysis (e.g., as
    the `return` path of a loop). An instantiation of this class will not
    be picked up as an empty bundle and get removed/optimized during graph
    rewrite.
    """

    def is_empty(self) -> bool:
        return False


def clean_up_graph(graph: nx.classes.DiGraph):
    """
    Removes all placeholder empty `NodeBundle` from the graph.
    """

    empty_nodes = [
        i for i in graph.nodes
        if isinstance(i, NodeBundle) and i.is_empty()
    ]

    for node in empty_nodes:
        for pred in graph.predecessors(node):
            for succ in graph.successors(node):
                orig_label = graph[pred][node].get('label')
                if orig_label is None:
                    graph.add_edge(pred, succ)
                else:
                    graph.add_edge(pred, succ, label=orig_label)
    
    graph.remove_nodes_from(empty_nodes)


def get_successors(graph: nx.classes.DiGraph, node: ast.AST):
    return (
        i for i in graph.successors(node)
        if graph[node][i].get('label') != CFGLabels.IGNORE
    )


def get_last_convergence(graph: nx.classes.DiGraph, node: ast.AST) -> ast.AST:
    """
    Given a node in a graph, this function searches through all its successors
    to see if they converge back into a single node after some point. Returns
    the last such node.

    If no successors converge, returns the given node.

    TODO: find a better algorithm for this O(N^2) abomination.
    """

    def _merge_path(a: Dict[ast.AST, int], b: Dict[ast.AST, int]) -> Dict[ast.AST, int]:
        return {k: max(a[k], b[k]) for k in a if k in b}
    
    def _search_path(node: ast.AST, path: Dict[ast.AST, int]) -> Dict[ast.AST, int]:

        # Get all successors and remove visited nodes (not necessary right now,
        # but in case the CFG becomes cyclic in the future due to some new encoding
        # requirement on the target language side).
        succs = set(get_successors(graph, node)) - path.keys()
        if not succs:
            return path

        result = None
        for succ in succs:
            new_path = {**path}
            new_path[succ] = path[node] + 1

            branch_path = _search_path(succ, new_path)
            if result is None:
                result = branch_path
            else:
                result = _merge_path(result, branch_path)
        
        return result
    
    init_path = {node: 0}
    common_nodes = _search_path(node, init_path)

    if not common_nodes:
        return node
    
    last_common = max(common_nodes, key=common_nodes.__getitem__)
    return last_common
