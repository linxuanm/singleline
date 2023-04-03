import ast
import networkx as nx
from typing import Set, Dict, Tuple

from ..analysis import CFGLabels


def get_last_convergence(graph: nx.classes.DiGraph, node: ast.AST) -> ast.AST:
    """
    Given a node in a graph, this function searches through all its successors
    to see if they converge back into a single node after some point. Returns
    the last such node.

    If no sucessors converge, returns the given node.

    TODO: find a better algorithm for this O(N^2) abomination.
    """

    def _get_successors(node: ast.AST):
        return (
            i for i in graph.successors(node)
            if graph[node][i]['label'] != CFGLabels.IGNORE
        )
    
    def _search_path(node: ast.AST) -> Dict[ast.AST, int]:
        front = [node]
        visited = {node: 0}
        while front:
            curr = front.pop()
            for succ in _get_successors(curr):
                if curr not in visited:
                    visited[succ] = visited[curr] + 1
                    front.append(succ)
        
        return visited
    
    pass
