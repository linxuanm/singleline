class FunctionDataFlow:
    """
    A global graph that traces the result of dataflow analysis of functions.
    Only functions are of interest here due to how their invocation causes
    their free variables to be live in the call site.

    Essentially, each function `f` must track down all variables (set `V`)
    in all scopes that might be assigned `f`. Then every function is 
    """