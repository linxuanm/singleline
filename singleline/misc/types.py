import ast
from typing import List, Union

from .graph_nodes import *

# return type of a `NodeTransformer`'s visit methods
VRet = Union[ast.AST, List[ast.AST], None]

# type of a node in a control-flow graph
CFNode = Union[ast.AST, NodeBundle]
