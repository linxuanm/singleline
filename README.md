# SingleLine

Write your Python program in a single line!

SingleLine is a command-line tool that transforms any Python file or function into a one-liner statement. And guess what? No semi-colons in the output cuz that's for donkeys!

## Installing

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

Execute singleline `<file>` to generate a one-line program that works just like the original file.

Use singleline `<file> -f <function_name>` to transpile the specified function `<function_name>` into a nifty one-line lambda. Keep in mind that if `<function_name>` relies on other functions or values in `<file>`, they'll be bundled into the resulting program as well.

## lmao

ok I wrote this tool to annoy Mr. Mullan lol hes now gonna grade like a million one-line lambda programs
