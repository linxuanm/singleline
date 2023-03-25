import ast
import networkx as nx
from typing import List

from ..misc.types import VRet


class ControlFlowGraph:
    """
    Generates the control flow graph of the source program so that lambda
    and branching structures can be determined statically.
    """

    graph: nx.DiGraph

    def __init__(self):
        self.graph = nx.DiGraph()
