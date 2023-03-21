import ast


def load_program(program: str):
    tree = ast.parse(program)
