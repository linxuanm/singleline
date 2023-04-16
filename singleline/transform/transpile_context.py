import ast
import networkx as nx
from typing import List


class NameContextManager:
    """
    Manages the links between a graph node and the context variables generated
    from it (e.g., the mutable variable collection of a loop).

    An instantiation of this class is treated as a singleton through a single
    compilation session as node-context links persist across the different
    scopes of a program.
    """

    pass


class ScopedExprManager:
    """
    Manages the accumulation of transpiled code in an expression form. This
    class is mainly responsible for structuring the `return` propagation up
    nested structures in the target code.
    """

    exprs: List[str]
    has_ret: bool

    def __init__(self) -> None:
        self.exprs = []
        self.has_ret = False

    def add(self, expr: str, should_ret: bool = False):
        assert isinstance(expr, str)
        
        if not should_ret:
            if self.has_ret:
                raise ValueError(
                    'This tuple layer is already sealed with a return value, '
                    'and cannot be mutated further'
                )
            self.exprs.append(expr)
        
        else:
            if self.has_ret:
                raise ValueError('This tuple layer is already marked with a return value')
            
            self.exprs.append(expr)
            self.has_ret = True

    def build(self) -> str:
        inner = ', '.join(self.exprs)

        # Marks the expression as a tuple with an appended comma.
        if len(self.exprs) == 1:
            inner += ','

        tup_expr = f'({inner})'

        # Propagates the return value up the nested tuples.
        if self.has_ret:
            tup_expr += '[-1]'

        return tup_expr
