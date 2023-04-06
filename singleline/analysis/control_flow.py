import ast
import networkx as nx
from typing import List, Tuple, Union

from ..misc.types import VRet
from ..misc.graph_utils import NodeBundle, DummyBundle, clean_up_graph, CFGLabels
from .interrupt import has_interrupt


def control_flow_pass(node: Union[ast.Module, ast.FunctionDef]):
    """
    Populates the `graph` attribute of a module or function with the CFG
    of its content with an instance of `nx.DiGraph`.
    """

    cfg = ControlFlowGraph()
    cfg.build_cfg(node, node.body)
    node.graph = cfg.graph
    clean_up_graph(node.graph)


class ControlFlowGraph:
    """
    Generates the control flow graph of the source program so that lambda
    and branching structures can be determined statically.
    """

    graph: nx.classes.DiGraph

    def __init__(self):
        self.graph = nx.classes.DiGraph()
    
    def build_cfg(self, head: ast.AST, code: List[ast.AST]):
        # `head` is an `ast.AST` that represents the container for `code`. It is
        # used as an entry point to the graph.

        self.graph.add_node(head)
        top, _ = self._analysis_pass(code)
        self.graph.add_edge(head, top)

    def _analysis_pass(self, code: List[ast.AST]) -> Tuple[ast.AST, List[ast.AST]]:
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
        interrupt = False
        for node in code:
            if ControlFlowGraph._is_compound_node(node):
                code_segments.append(node)
                code_segments.append(NodeBundle())
            else:
                code_segments[-1].append(node)

            if isinstance(node, ast.FunctionDef):
                control_flow_pass(node)

            if ControlFlowGraph._is_interrupt_node(node):
                interrupt = True
                break

        first = None # Entry node for `code`.
        prev = None # Out-flowing nodes from the previous block.

        for i in code_segments:
            curr_in, curr_out = self._expand_single_node(i)
            if first is None:
                first = curr_in
            
            if prev is not None:
                for in_node in prev:
                    self.graph.add_edge(in_node, curr_in)
            
            prev = curr_out

        # Empty control-flow node as body.
        if first is None:
            node = NodeBundle()
            self.graph.add_node(node)
            return (node, [node])
        
        return (first, [] if interrupt else prev)
    
    def _expand_single_node(self, node) -> Tuple[ast.AST, List[ast.AST]]:
        """
        Adds the control-flow graph of `node` as a separate, disconnected
        sub-graph to `self.graph`, and returns the entry node and list of
        out-flowing nodes of the generated graph to be connected to the rest
        of the control-flow graph.
        """

        if isinstance(node, NodeBundle): # Straight line code.
            self.graph.add_node(node)
            return (node, [node])
        elif isinstance(node, ast.If): # If statement.
            self.graph.add_node(node)
            if_in, if_out = self._analysis_pass(node.body)
            else_in, else_out = self._analysis_pass(node.orelse)

            self.graph.add_edge(node, if_in, label=CFGLabels.IF)
            self.graph.add_edge(node, else_in, label=CFGLabels.ELSE)

            return (node, if_out + else_out)
        elif isinstance(node, ast.While) or isinstance(node, ast.For):
            return self._build_loop_graph(node)
        
        raise NotImplementedError(type(node))
        
    def _build_loop_graph(self, node: ast.AST) -> Tuple[ast.AST, ast.AST]:
        self.graph.add_node(node)
        has_break, has_ret = has_interrupt(node.body)

        # Populate some properties of the loop.
        node.has_break = has_break,
        node.has_ret = has_ret

        # Node that links to the code pieces following this loop.
        out_node = NodeBundle()
        self.graph.add_node(out_node)
        self.graph.add_edge(node, out_node)

        # The inner section of a loop is created as a sub_graph connected
        # with an edge labeled as `CFGLabels.IGNORE` to prevent the graph
        # rewriting process from treating the interior of a loop as an outcome
        # of this loop (e.g., since the inner section of a loop always ends
        # in graph nodes with no outgoing edges due to its compilation to a
        # lambda `f` in `next(filter(f, xs))`, the transformer of a surronding
        # `if` node may mistaken the loop node for being able to raise an
        # interruption in the surronding function due to the existence of
        # terminal nodes in the sub-graph of the loop).

        inner_in, _ = self._analysis_pass(node.body)
        self.graph.add_edge(node, inner_in, label=CFGLabels.IGNORE)

        # If the loop can interrupt with `return`, use a dummy node that has
        # no outgoing edges to tell the graph rewriter that an interruption
        # may occur.
        if has_ret:
            dummy_node = DummyBundle()
            self.graph.add_node(dummy_node)
            self.graph.add_edge(node, dummy_node, label=CFGLabels.RET_FLAG)

        return (node, [out_node])

    @staticmethod
    def _is_compound_node(node: ast.AST):
        types = [ast.If, ast.For, ast.While]
        return any(isinstance(node, t) for t in types)
    
    @staticmethod
    def _is_interrupt_node(node: ast.AST):
        types = [ast.Break, ast.Continue, ast.Return]
        return any(isinstance(node, t) for t in types)
