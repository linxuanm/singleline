import ast
from typing import List, Union

# return type of a `NodeTransformer`'s visit methods
VRet = Union[ast.AST, List[ast.AST], None]
