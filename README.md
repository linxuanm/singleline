# SingleLine

Write your Python program in a single line!

Singleline is a command-line tool that transpiles *almost* any Python program into one line. The resultant code

## Installing

THIS PROJECT IS NOT FINISHED AND NOT PUBLISHED YET!!!
But later on you can:

Use `pip` to install:
```sh
pip install singleline
```

To transpile a Python file (e.g., `script.py`) into a single line, run:
```sh
singleline script.py
```

## Usage

SingleLine offers two modes: function transpiling and file transpiling.



## Target Code Details

Theoretically, converting imperative program to a one-line lambda is trivial with the usage of state monad transformers (or with a haskell's `ST` equivalent); however, binding a new lambda everytime a variable in the environment is changed induces significant stack usage and will easily cause a `RecursionError`. SingleLine aims to preserve the max recursion depth of the source program as much as possible, and thus uses syntax such as `:=` for assignments and hacks such as `next(filter(f, xs))` for a non-recursive implementation of right folds (since Python's `reduce` doesn't short-wire).

Many similar concepts are explored and discussed in the `playground.ipynb` file.

# Caveats

While Singleline works on the majority of Python programs, there are a few caveats:

- Operation and assignment (e.g., `+=`) are transpiled to a naive assignment (e.g., `a += b` to `a = a + b`). This could be circumvented by using `operator.iadd`, but that would result in an extra import.
- Mutated variables in loops will not be tracked if mutated with `eval` or `exec` (e.g., `exec('a = 32')` inside a loop will not alter `a` as expected).

## lmao

ok I wrote this tool to annoy Mr. Mullan lol hes now gonna grade like a million one-line lambda programs
