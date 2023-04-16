
import ast
from typing import Tuple

from .analysis import preprocess, control_flow_pass
from .transform import transpile


def compile(program: str) -> str:
    tree, id_gen = preprocess(program)
    control_flow_pass(tree)

    graph = tree.graph
    code = transpile(graph, id_gen, tree)

    return code
