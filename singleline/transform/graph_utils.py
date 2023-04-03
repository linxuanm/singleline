import ast
import networkx as nx
from typing import Set, Dict, Tuple

from ..analysis import CFGLabels


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

    succs = graph[node]
    print(' 123',succs)
    #while len(succs) == 1:
        
    
    def _search_path(node: ast.AST) -> Dict[ast.AST, int]:
        front = [node]
        visited = {node: 0}
        while front:
            curr = front.pop()
            for succ in get_successors(graph, curr):
                if curr not in visited:
                    visited[succ] = visited[curr] + 1
                    front.append(succ)
        
        return visited
    
    all_paths = [_search_path(i) for i in get_successors(graph, node)]
    path_sets = [set(i.keys()) for i in all_paths]
    common_nodes = set.intersection(*path_sets)
    #print('Common: ', all_paths)

    if not common_nodes:
        return node
    
    def node_depth(k):
        return max(d[k] for d in all_paths)
    
    last_common = max(common_nodes, key=node_depth)
    return last_common
