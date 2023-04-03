import ast
import networkx as nx

from ..misc.identifiers import IdentifierGenerator


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

    def transpile(self, node: ast.AST) -> str:
        """
        Transpiles a code given a node in the CFG.
        """
        
        assert node in self.graph

        # Flatten the nodes into layers to determine execution path coercion.
        layers = []

        exprs = []
        while node is not None:
            node = next(self.graph.successors(node), None)

    def transpile_single(self, stmt: ast.AST) -> str:
        if isinstance(stmt, ast.Assign):
            # Preprocessor unwraps all tuple assignments, so it is safe to
            # directly index the 0-th element.
            name = stmt.targets[0]
            value = stmt.value
            stmt = ast.NamedExpr(name, value)

        return ast.unparse(stmt)
