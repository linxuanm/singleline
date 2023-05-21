import ast
import networkx as nx
from typing import Union

from ..misc.identifiers import IdentifierGenerator
from ..misc.graph_utils import *
from ..misc.graph_nodes import NodeBundle, CFGLabels
from ..misc.types import CFNode
from .transpile_context import ScopedExprManager
from .replace import init_loop_mutations


def transpile(
    graph: nx.classes.DiGraph,
    id_gen: IdentifierGenerator,
    header: CFNode,
    stop: Union[CFNode, None] = None
) -> str:
    entry = get_next_from_label(graph, header, CFGLabels.CONTENT)
    transpiler = GraphTranspiler(id_gen, graph)
    return transpiler.transpile(entry, stop)


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

        # Empty bundle (e.g., empty `else` block).
        if not sep:
            return '()'

        # Iterates through all nodes and convert until reaching the next one.
        # The `stop` node is needed to execute `get_all_convergence` inside
        # each branch in sub-statements.
        for start, stop in zip(sep, sep[1 :]):
            self._transpile_node(start, stop, ctx)

        self._transpile_node(sep[-1], stop, ctx, True)
        return ctx.build()

    def _transpile_node(
        self,
        node: CFNode,
        stop: Union[CFNode, None],
        ctx: ScopedExprManager,
        try_ret: bool = False
    ) -> None:
        if isinstance(node, NodeBundle):
            for stmt in node.bundle:
                self._transpile_single(stmt, ctx)

        # `ast.If` is the only node that respects `try_ret`.
        elif isinstance(node, ast.If):
            if_branch = get_next_from_label(self.graph, node, CFGLabels.IF)
            else_branch = get_next_from_label(self.graph, node, CFGLabels.ELSE)
            
            if_code = self.transpile(if_branch, stop)
            else_code = self.transpile(else_branch, stop)
            cond_code = ast.unparse(node.test)

            ctx.add(
                f'{if_code} if {cond_code} else {else_code}',
                try_ret
            )
        
        elif isinstance(node, ast.While):
            inf = ast.parse('iter(int, 1)')
            has_ret = has_labeled_edge(self.graph, node, CFGLabels.RET_FLAG)
            init_loop_mutations(node)

        else:
            raise NotImplementedError

    def _transpile_single(self, stmt: ast.AST, ctx: ScopedExprManager) -> None:
        if isinstance(stmt, ast.Assign):
            # Preprocessor unwraps all tuple assignments, so it is safe to
            # directly index the 0-th element.
            name = stmt.targets[0]
            value = stmt.value
            code = ast.NamedExpr(name, value)
            ctx.add(ast.unparse(code))

        elif isinstance(stmt, ast.Return):
            if stmt.value is None:
                ctx.add('None', True)
            else:
                ctx.add(ast.unparse(stmt.value), True)

        elif isinstance(stmt, ast.Raise):
            ctx.add(f'(_ for i in ()).throw({ast.unparse(stmt.exc)})')

        elif isinstance(stmt, ast.Yield) or isinstance(stmt, ast.YieldFrom):
            ctx.add(f'({ast.unparse(stmt)})')

        elif isinstance(stmt, ast.FunctionDef):
            body = transpile(stmt.graph, self.id_gen, stmt)

            # some really hacky transpiling
            exp = ast.Lambda(stmt.args, ast.Tuple([]))
            code = ast.unparse(exp)[: -2] + body
            ctx.add(f'{stmt.name} := {code}')

        else:
            ctx.add(ast.unparse(stmt))
