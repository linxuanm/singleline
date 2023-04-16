# Testing `ast.If` and `ast.FunctionDef` transpilation.
import ast
import unittest
import textwrap
import networkx as nx

from .context import singleline
from .plot import plot_graph


def format(code):
    return textwrap.dedent(code).strip('\n')


TESTS = {
    format("""
    def greet(time):
        if time < 12:
            return "Good morning!"
        elif time < 18:
            return "Good afternoon!"
        else:
            return "Good evening!"

    print(greet(10))
    """): "Good morning!",

    format("""
    def triangle_type(a, b, c):
        if a == b == c:
            return "Equilateral"
        elif a == b or b == c or a == c:
            return "Isosceles"
        else:
            return "Scalene"

    print(triangle_type(3, 3, 3))
    """): "Equilateral",

    format("""
    def odd_or_even(number):
        if number % 2 == 0:
            return "Even"
        else:
            return "Odd"

    print(odd_or_even(7))
    """): "Odd",

    format("""
    def grade(score):
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    print(grade(85))
    """): "B",

    format("""
    def max_of_two(a, b):
        if a > b:
            return a
        else:
            return b

    print(max_of_two(4, 7))
    """): "7",

    format("""
    def leap_year(year):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return "Leap year"
        else:
            return "Not a leap year"

    print(leap_year(2020))
    """): "Leap year",

    format("""
    def age_group(age):
        if age < 13:
            return "Child"
        elif age < 18:
            return "Teenager"
        elif age < 65:
            return "Adult"
        else:
            return "Senior"

    print(age_group(25))
    """): "Adult",

    format("""
    def sign(x):
        if x > 0:
            return "Positive"
        elif x < 0:
            return "Negative"
        else:
            return "Zero"

    print(sign(-5))
    """): "Negative",

    format("""
    def discount(price, customer):
        if customer == "student":
            return price * 0.9
        elif customer == "senior":
            return price * 0.8
        else:
            return price

    print(discount(100, "senior"))
    """): "80.0",

    format("""
    def vowel_or_consonant(char):
        if char.lower() in "aeiou":
            return "Vowel"
        else:
            return "Consonant"

    print(vowel_or_consonant("A"))
    """): "Vowel"
}


class ControlFlowGraphTest(unittest.TestCase):

    def test_output(self):
        for code, expect in TESTS.items():
            tree, id_gen = singleline.analysis.preprocess(code)
            singleline.analysis.control_flow_pass(tree)

            graph = tree.graph
            code = singleline.transform.transpile(graph, id_gen, tree)
            
            print(code)


if __name__ == '__main__':
    unittest.main()
