import ast
import unittest
import networkx as nx

from .context import singleline
from .plot import plot_graph


SIMPLE_FUNC = """
a = a + 1
if a == 2:
    a += 2
elif a == 3:
    abc()
b = 3
print(b)
"""

COMPLEX_FUNC = """
def foo():
    a = a + 1
    if a == 2:
        return 'television'
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


class ControlFlowGraphTest(unittest.TestCase):

    def test_simple_linear(self):
        tree, id_gen = singleline.analysis.preprocess(SIMPLE_FUNC)
        singleline.analysis.control_flow_pass(tree)

        graph = tree.graph

        last = singleline.misc.get_last_convergence(graph, tree)
        for i, ans in zip(last.bundle, ['b=3', 'print(b)']):
            self.assertEqual(ast.unparse(i).replace(' ', ''), ans)

    def test_complex_func(self):
        tree, id_gen = singleline.analysis.preprocess(COMPLEX_FUNC)
        singleline.analysis.control_flow_pass(tree)

        print(id_gen.invalid_pool)

        graph = tree.graph

        last = singleline.misc.get_last_convergence(graph, tree)


if __name__ == '__main__':
    unittest.main()
