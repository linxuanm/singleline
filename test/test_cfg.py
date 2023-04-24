import ast
import unittest
import networkx as nx

from .context import singleline
from .utils import plot_graph


SIMPLE_FUNC = """
a = int(input())
a = a + 1
if a == 2:
    a += 2
elif a == 3:
    assert 2 == 1, 'nope'
b = 3
print(a, b)
"""

COMPLEX_FUNC = """
def foo():
    a = a + 1
    if a == 2:
        c = 2
    elif a == 3:
        for i in range(10):
            if i > 5:
                break
            print(123)
            if a == 20:
                continue
                import numpy as np
    b = 3
    print(b)

foo()
"""

RET_FUNC = """
def foo(a, b):
    if a == 3:
        if b == 4:
            return 42
        print(123)
    print(456)
"""


class ControlFlowGraphTest(unittest.TestCase):

    def test_simple_linear(self):
        tree, id_gen = singleline.analysis.preprocess(SIMPLE_FUNC)
        singleline.analysis.control_flow_pass(tree)

        graph = tree.graph

        common = singleline.misc.get_all_convergence(graph, tree)
        for i, ans in zip(common[-1].bundle, ['b=3', 'print(a,b)']):
            self.assertEqual(ast.unparse(i).replace(' ', ''), ans)

    def test_complex_func(self):
        tree, id_gen = singleline.analysis.preprocess(COMPLEX_FUNC)
        singleline.analysis.control_flow_pass(tree)

        graph: nx.classes.DiGraph = tree.body[0].graph

        common = singleline.misc.get_all_convergence(graph, tree.body[0])
        for i, ans in zip(common[-1].bundle, ['b=3', 'print(b)']):
            self.assertEqual(ast.unparse(i).replace(' ', ''), ans)

    def test_simple_transpile(self):
        tree, id_gen = singleline.analysis.preprocess(RET_FUNC)

        code = singleline.compile(RET_FUNC)
        print(code)
        # TODO: finish this


if __name__ == '__main__':
    unittest.main()
