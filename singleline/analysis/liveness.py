from typing import Dict, Set


"""
Note to self: a function call on `f` at line `n` makes the set of
free variables in `f` live on line `n - 1`. Due to scoping this makes
the liveness of a variable propagate up the call stack, (e.g., if `x`
is live in `foo()`, and `bar()` might call `foo()`, then `x` is also
live in `bar()`).

SCOPE MATTERS!!! Encode the function scope along side with the variable
names in liveness & reference resolver.
"""

class LivenessData:
    """
    Tracks the result of liveness analysis on a function.

    Attached to the `liveness` attribute of an instance of `ast.FunctionDef`
    during static analysis.

    Note that this does not apply to indexed (i.e. subscript) assigments, as
    they are rewritten into function calls during preprocessing.
    """
    
    # tracked_vars[var_name] = { <live at lines> }
    tracked_vars: Dict[str, Set[int]]
    live_out: Set[str]

    def __init__(self):
        self.tracked_vars = {}
        self.live_out = set()

    def live_at(self, var: str, line: int):
        return line in self.tracked_vars[var]