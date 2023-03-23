import ast


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

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.stmt:
        return self.visit(ast.Assign(
            [node.target],
            ast.BinOp(node.target, node.op, node.value),
            lineno=0
        ))
    
    def visit_Assign(self, node: ast.Assign) -> ast.stmt:
        chain = node.targets + [node.value]

        return [
            self._mutate_assign(k, v)
            for v, k in zip(chain[:: -1], chain[-2 :: -1])
        ]
    
    def _mutate_assign(self, var: ast.expr, val: ast.expr):
        if isinstance(var, ast.Subscript):
            return ast.Call(
                ast.Attribute(var.value, '__setitem__'),
                [self._parse_slice(var.slice), val],
                []
            )
        
        return ast.Assign([var], val, lineno=0)
    
    def _parse_slice(self, slice: ast.expr):
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

    print(ast.unparse(tree))
    
    return tree

