import ast
from typing import Set

from ..misc import IdentifierGenerator
from ..misc.types import VRet


class PreprocessTransformer(ast.NodeTransformer):
    """
    This class is responsible for applying preprocessing transformations
    to the AST to allow easy handling of syntax sugar. It is meant to
    apply rudimentary code transformation without keeping a context or
    performing static analysis, as well as obtain some trivial information
    about the program such as used identifier names.

    The current list of preprocessing operations are:
    - Rewriting indexed assignments (e.g., `a[0] = 2` to `a.__setitem__(0, 2)`)
    - Rewriting augmented assignments (e.g., `a += b` to `a = a + b`)
    - Unwrapping tuple assignments
    - Unwrapping `import` statements
    """

    used_id: Set[str]
    id_gen: IdentifierGenerator

    def __init__(self):
        self.used_id = set()
        self.id_gen = IdentifierGenerator(self.used_id)

    def visit_AugAssign(self, node: ast.AugAssign) -> VRet:
        return self.visit(ast.Assign(
            [node.target],
            ast.BinOp(node.target, node.op, node.value),
            lineno=node.lineno
        ))
    
    def visit_Assign(self, node: ast.Assign) -> VRet:
        chain = node.targets + [node.value]

        return [
            self._mutate_assign(k, v)
            for v, k in zip(chain[:: -1], chain[-2 :: -1])
        ]
    
    def visit_Import(self, node: ast.Import) -> VRet:
        names = [i.name for i in node.names]

        modules = [
            ast.Call(ast.Name('__import__'), [ast.Constant(i)], [])
            for i in names
        ]

        aliases = [i.asname if i.asname is not None else i.name for i in node.names]
        # `import xyz.abc` imports the left-most module `xyz` to the
        # left-most name `xyz`, thus `xyz = __import__('xyz.abc')`
        asn_names = [i.split('.')[0] for i in aliases]

        assigns = [
            self._mutate_assign(ast.Name(name), module)
            for name, module in zip(asn_names, modules)
        ]

        return assigns
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> VRet:
        module = node.module
        call = ast.Call(ast.Name('__import__'), [ast.Constant(module)], [])
        packed_var_name = self.id_gen.throwaway()
        init = self._mutate_assign(ast.Name(packed_var_name), call)

        # gets the `['def', 'ghi']` part of `from abc.def.ghi import foo`s
        additional_path = module.split('.')[1 :]

        # generators the `__.abc.def` in `foo = __.abc.def.foo`
        def _gen_prefix():
            root = ast.Name(packed_var_name)
            for name in additional_path:
                root = ast.Attribute(root, name)
            
            return root

        var_names = [i.name for i in node.names]
        packed_rhs = [
            ast.Attribute(_gen_prefix(), name)
            for name in var_names
        ]

        aliases = [i.asname if i.asname is not None else i.name for i in node.names]
        assigns = [
            self._mutate_assign(ast.Name(name), rhs)
            for name, rhs in zip(aliases, packed_rhs)
        ]

        return [init] + assigns
    
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
    