# Utility code for performing replacing operation on source code.

import ast
from typing import Union

from ..analysis import MutationRecorder


def init_loop_mutations(loop: Union[ast.For, ast.While]) -> None:
    recorder = MutationRecorder()
    recorder.visit(loop)
