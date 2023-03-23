from typing import Dict, Set


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

    def __init__(self):
        self.tracked_vars = {}

    def live_at(self, var: str, line: int):
        return line in self.tracked_vars[var]