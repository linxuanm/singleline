from typing import Set


class LambdaScope:
    """
    Stores the variable usage information of a function.

    Attached to the `lambda_scope` attribute of an instance of `ast.FunctionDef`
    during static analysis.

    This class' primary use is to keep track of free & bounded variables in
    a function in the source language.
    """

    free_vars: Set[str]

    def __init__(self):
        pass