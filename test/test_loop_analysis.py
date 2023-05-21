import ast
import unittest

from .context import singleline

SIMP_LOOP_MUT = """
a = 0
b = 3

while a < 20:
    print(a)
    a += 1
    b = b * a + 1

print(f'End: {a} {b}')
"""


class MutatedVarTest(unittest.TestCase):

    def test_simple_loop(self):
        tree, id_gen = singleline.analysis.preprocess(SIMP_LOOP_MUT)
        singleline.analysis.control_flow_pass(tree)

        singleline.transform.init_loop_mutations(tree.body[2])

        self.assertEqual(tree.body[2].mutated_vars, {'a', 'b'})
