import ast

from .misc.identifiers import IdentifierGenerator


class PreprocessTransformer(ast.NodeTransformer):
    """
    This class is responsible for applying preprocessing transformations
    to the AST to allow easy handling of syntax sugar. It is meant to
    apply rudimentary code transformation without keeping a context or
    performing static analysis.

    The current list of preprocessing operations are:
    - Rewriting indexed assignments (e.g., `a[0] = 2` to `a.__setitem__(0, 2)`)
    - Rewriting augmented assignments (e.g., `a += b` to `a = a + b`)
    - Unwrapping tuple assignments
    """

    id_gen: IdentifierGenerator

    def __init__(self):
        self.id_gen = IdentifierGenerator()

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.stmt:
        return self.visit(ast.Assign(
            [node.target],
            ast.BinOp(node.target, node.op, node.value),
            lineno=node.lineno
        ))
    
    def visit_Assign(self, node: ast.Assign) -> ast.stmt:
        chain = node.targets + [node.value]

        return [
            self._mutate_assign(k, v)
            for v, k in zip(chain[:: -1], chain[-2 :: -1])
        ]
    
    def _mutate_assign(self, var: ast.expr, val: ast.expr):

        # assignment to a subscript
        if isinstance(var, ast.Subscript):
            return ast.Expr(ast.Call(
                ast.Attribute(var.value, '__setitem__'),
                [self._parse_slice(var.slice), val],
                []
            ))
        
        # packed assignment
        if isinstance(var, ast.List) or isinstance(var, ast.Tuple):
            name = self.id_gen.throwaway()
            init = ast.Assign([ast.Name(name)], val, lineno=0)
            return [
                init,
                *[
                    self._mutate_assign(
                        v,
                        ast.Subscript(ast.Name(name), ast.Constant(idx))
                    ) for idx, v in enumerate(var.elts)
                ]
            ]
        
        return ast.Assign([var], val, lineno=0)
    
    def _parse_slice(self, slice: ast.expr) -> ast.expr:
        if isinstance(slice, ast.Slice):
            return ast.Call(
                ast.Name('slice'),
                [
                    slice.lower or ast.Constant(value=None),
                    slice.upper or ast.Constant(value=None),
                    slice.step or ast.Constant(value=None)
                ],
                []
            )
        
        return slice


def load_program(program: str):
    """
    Parses and preprocesses a program.
    """

    tree = ast.parse(program)
    preprocessor = PreprocessTransformer()
    tree = preprocessor.visit(tree)

    # reloads to automatically update line numbers and other attributes
    # TODO: check if this is needed
    tree = ast.parse(ast.unparse(tree))



    return tree
