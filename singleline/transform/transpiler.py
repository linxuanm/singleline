import ast
import networkx as nx
from typing import Union

from ..misc.identifiers import IdentifierGenerator
from ..misc.graph_utils import get_all_convergence
from ..misc.graph_nodes import NodeBundle
from ..misc.types import CFNode
from .transpile_context import ScopedExprManager


class GraphTranspiler:
    """
    This class is responsible for transpiling a sub-graph into a single-line
    code, as well as keep track of the session/environment of each syntax
    construct (e.g., through `ContextManager`).
    """

    id_gen: IdentifierGenerator
    graph: nx.classes.DiGraph

    def __init__(self, id_gen: IdentifierGenerator, graph: nx.classes.DiGraph):
        self.id_gen = id_gen
        self.graph = graph

    def transpile(self, node: CFNode, stop: Union[CFNode, None]) -> str:
        """
        Transpiles a code given a node in the CFG.
        """
        
        assert node in self.graph

        ctx = ScopedExprManager()
        sep = get_all_convergence(self.graph, node, stop)

        # Iterates through all nodes and convert until reaching the next one.
        # The `stop` node is needed to execute `get_all_convergence` inside
        # each branch in sub-statements.
        for start, stop in zip(sep, sep[1 :]):
            self._transpile_node(start, stop, ctx)

        self._transpile_node(sep[-1], stop, ctx)

    def _transpile_node(self, node: CFNode, ctx: ScopedExprManager) -> None:
        if isinstance(node, NodeBundle):
            for stmt in node.bundle:
                self._transpile_single(stmt, ctx)

    def _transpile_single(self, stmt: ast.AST, ctx: ScopedExprManager) -> None:
        if isinstance(stmt, ast.Assign):
            # Preprocessor unwraps all tuple assignments, so it is safe to
            # directly index the 0-th element.
            name = stmt.targets[0]
            value = stmt.value
            code = ast.NamedExpr(name, value)
            ctx.add(ast.unparse(code))

        elif isinstance(stmt, ast.Return):
            code = stmt.value
            ctx.add_ret(code)

        ctx.add(ast.unparse(stmt))
