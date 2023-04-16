import os
import argparse

from ..compile import load_program


def main():
    parser = argparse.ArgumentParser(
        description='Converts Python code to one-liners!'
    )

    parser.add_argument('input', type=str, help='the input file')
    parser.add_argument('-o', '--output', type=str, help='the output file')

    args = parser.parse_args()

    in_file = args.input
    out_file = args.output

    if out_file is None:
        out_file = os.path.splitext(in_file)[0] + '_singleline.py'

    with open(in_file, 'r') as f:
        content = f.read()
