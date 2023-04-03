import ast
import networkx as nx
from typing import Union


def get_last_convergence(graph: nx.classes.DiGraph, node: ast.AST) -> ast.AST:
    """
    Given a node in a graph, this function searches through all its successors
    to see if they converge back into a single node after some point. Returns
    the last such node.

    If no sucessors converge, returns the given node.
    """
    pass
