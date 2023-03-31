import ast
import unittest
import networkx as nx

from .context import singleline
from .plot import plot_graph


SIMPLE_FUNC = """
def foo(a):
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
    b = 3
    return k
"""


class ControlFlowGraphTest(unittest.TestCase):

    def test_simple_return(self):
        tree = ast.parse(SIMPLE_FUNC)
        singleline.analysis.control_flow_pass(tree)

        plot_graph(tree.body[0].graph)


if __name__ == '__main__':
    unittest.main()
