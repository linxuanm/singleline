# SingleLine

Write your Python program in a single line!

SingleLine is a command-line tool that transforms any Python file or function into a one-liner statement. No semi-colons in the output cuz that's for donkeys!

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

Execute `singleline <file>` to generate a one-line program that works just like the original file.

Use `singleline <file> -f <function_name>` to transpile the specified function `<function_name>` into a nifty one-line lambda. Keep in mind that if `<function_name>` relies on other functions or values in `<file>`, they'll be bundled into the resulting lambda as well.

## Target Code Details

Theoretically, converting imperative program to a one-line lambda is trivial with the usage of state monad transformers (or with a haskell's `ST` equivalent); however, binding a new lambda everytime a variable in the environment is changed induces significant stack usage and will easily cause a `RecursionError`. SingleLine aims to preserve the stack usage of the source program as much as possible, and thus uses syntax such as `:=` for assignments and hacks such as `next(filter(f, xs))` for a non-recursive implementation of right folds (since Python's `reduce` doesn't short-wire).

Many similar concepts are explored and discussed in the `playground.ipynb` file.

## lmao

ok I wrote this tool to annoy Mr. Mullan lol hes now gonna grade like a million one-line lambda programs
