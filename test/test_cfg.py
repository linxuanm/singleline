import ast
import unittest

from .context import singleline


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
        cfg = singleline.analysis.CFGVisitor()
        cfg.visit(tree)

        self.assertTrue(tree.body[0].has_return)
        self.assertFalse(tree.body[0].body[1].has_break)
        self.assertTrue(tree.body[0].body[1].orelse[0].body[0].has_break)
        self.assertTrue(tree.body[0].body[1].orelse[0].body[0].body[2].has_break)

if __name__ == '__main__':
    unittest.main()
