import ast
import networkx as nx
from typing import Dict, List, Union

from .graph_nodes import *
from .types import CFNode


def clean_up_graph(graph: nx.classes.DiGraph) -> None:
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


def get_all_convergence(
    graph: nx.classes.DiGraph,
    node: ast.AST,
    end: Union[ast.AST, None] = None
) -> List[CFNode]:
    """
    Given a node in a graph, this function searches through all its successors
    to see if they converge back into a single node after some point. Returns
    all such nodes.

    If no successors converge, returns the given node.

    TODO: find a better algorithm for this O(N^2) abomination.
    """

    def _merge_path(a: Dict[CFNode, int], b: Dict[CFNode, int]) -> Dict[CFNode, int]:
        return {k: max(a[k], b[k]) for k in a if k in b}
    
    def _search_path(node: CFNode, path: Dict[CFNode, int]) -> Dict[CFNode, int]:

        # Get all successors and remove visited nodes (not necessary right now,
        # but in case the CFG becomes cyclic in the future due to some new encoding
        # requirement on the target language side).
        succs = set(get_successors(graph, node)) - path.keys() - {end}
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
    common_nodes.pop(node)

    sequence = list(common_nodes.keys())
    seq_ordered = sorted(sequence, key=common_nodes.__getitem__)
    return seq_ordered
