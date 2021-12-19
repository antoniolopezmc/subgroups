# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'core/operator.py'.
"""

from subgroups.core.operator import Operator
from pandas import Series
import unittest

class TestOperator(unittest.TestCase):

    def test_Operator_evaluate_method(self) -> None:
        # --------------------------------------------------------------
        # Operator EQUAL.
        # - int type.
        self.assertTrue(Operator.EQUAL.evaluate(2, 2))
        self.assertFalse(Operator.EQUAL.evaluate(2, 3))
        # - float type.
        self.assertTrue(Operator.EQUAL.evaluate(2.0, 2.0))
        self.assertFalse(Operator.EQUAL.evaluate(2.0, 3.0))
        # - str type.
        self.assertTrue(Operator.EQUAL.evaluate("abc", "abc"))
        self.assertFalse(Operator.EQUAL.evaluate("abc", "azz"))
        # - int and float types.
        self.assertTrue(Operator.EQUAL.evaluate(2, 2.0))
        self.assertFalse(Operator.EQUAL.evaluate(2.0, 3))
        # - str and any numeric types (they support this operator).
        self.assertFalse(Operator.EQUAL.evaluate("a", 23))
        self.assertFalse(Operator.EQUAL.evaluate(1.0, "cbf"))
        self.assertFalse(Operator.EQUAL.evaluate(1.0, "1.0"))
        self.assertFalse(Operator.EQUAL.evaluate(2.0, "1.0"))
        # --------------------------------------------------------------
        # Operator NOT_EQUAL.
        # - int type.
        self.assertTrue(Operator.NOT_EQUAL.evaluate(2, 3))
        self.assertFalse(Operator.NOT_EQUAL.evaluate(2, 2))
        # - float type.
        self.assertTrue(Operator.NOT_EQUAL.evaluate(2.0, 3.0))
        self.assertFalse(Operator.NOT_EQUAL.evaluate(2.0, 2.0))
        # - str type.
        self.assertTrue(Operator.NOT_EQUAL.evaluate("abc", "azz"))
        self.assertFalse(Operator.NOT_EQUAL.evaluate("abc", "abc"))
        # - int and float types.
        self.assertTrue(Operator.NOT_EQUAL.evaluate(2.0, 3))
        self.assertFalse(Operator.NOT_EQUAL.evaluate(2, 2.0))
        # - str and any numeric types (they support this operator).
        self.assertTrue(Operator.NOT_EQUAL.evaluate("a", 23))
        self.assertTrue(Operator.NOT_EQUAL.evaluate(1.0, "cbf"))
        self.assertTrue(Operator.NOT_EQUAL.evaluate(1.0, "1.0"))
        self.assertTrue(Operator.NOT_EQUAL.evaluate(1.0, "2.0"))
        # --------------------------------------------------------------
        # Operator LESS.
        # - int type.
        self.assertTrue(Operator.LESS.evaluate(2, 21))
        self.assertFalse(Operator.LESS.evaluate(23, 3))
        # - float type.
        self.assertTrue(Operator.LESS.evaluate(2.0, 21.0))
        self.assertFalse(Operator.LESS.evaluate(23.0, 3.0))
        # - str type.
        self.assertTrue(Operator.LESS.evaluate("abc", "bcd"))
        self.assertFalse(Operator.LESS.evaluate("bcd", "abc"))
        # - int and float types.
        self.assertTrue(Operator.LESS.evaluate(2.0, 3))
        self.assertFalse(Operator.LESS.evaluate(20, 2.0))
        # - str and any numeric types (they do not support this operator).
        self.assertRaises(TypeError, Operator.LESS.evaluate, "a", 23.0)
        self.assertRaises(TypeError, Operator.LESS.evaluate, "12", 23.0)
        self.assertRaises(TypeError, Operator.LESS.evaluate, "120", 23.0)
        self.assertRaises(TypeError, Operator.LESS.evaluate, "23.0", 23.0)
        # --------------------------------------------------------------
        # Operator GREATER.
        # - int type.
        self.assertTrue(Operator.GREATER.evaluate(21, 2))
        self.assertFalse(Operator.GREATER.evaluate(3, 23))
        # - float type.
        self.assertTrue(Operator.GREATER.evaluate(21.0, 2.0))
        self.assertFalse(Operator.GREATER.evaluate(3.0, 23.0))
        # - str type.
        self.assertTrue(Operator.GREATER.evaluate("bcd", "abc"))
        self.assertFalse(Operator.GREATER.evaluate("abc", "bcd"))
        # - int and float types.
        self.assertTrue(Operator.GREATER.evaluate(20.0, 3))
        self.assertFalse(Operator.GREATER.evaluate(2, 2.1))
        # - str and any numeric types (they do not support this operator).
        self.assertRaises(TypeError, Operator.GREATER.evaluate, "a", 23.0)
        self.assertRaises(TypeError, Operator.GREATER.evaluate, "12", 23.0)
        self.assertRaises(TypeError, Operator.GREATER.evaluate, "120", 23.0)
        self.assertRaises(TypeError, Operator.GREATER.evaluate, "23.0", 23.0)
        # --------------------------------------------------------------
        # Operator LESS_OR_EQUAL.
        # - int type.
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate(2, 21))
        self.assertFalse(Operator.LESS_OR_EQUAL.evaluate(23, 3))
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate(2, 2))
        # - float type.
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate(2.0, 21.0))
        self.assertFalse(Operator.LESS_OR_EQUAL.evaluate(23.0, 3.0))
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate(2.0, 2.0))
        # - str type.
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate("abc", "bcd"))
        self.assertFalse(Operator.LESS_OR_EQUAL.evaluate("bcd", "abc"))
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate("abc", "abc"))
        # - int and float types.
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate(2.0, 3))
        self.assertFalse(Operator.LESS_OR_EQUAL.evaluate(20, 2.0))
        self.assertTrue(Operator.LESS_OR_EQUAL.evaluate(2.0, 2))
        # - str and any numeric types (they do not support this operator).
        self.assertRaises(TypeError, Operator.LESS_OR_EQUAL.evaluate, "a", 23.0)
        self.assertRaises(TypeError, Operator.LESS_OR_EQUAL.evaluate, "12", 23.0)
        self.assertRaises(TypeError, Operator.LESS_OR_EQUAL.evaluate, "120", 23.0)
        self.assertRaises(TypeError, Operator.LESS_OR_EQUAL.evaluate, "23.0", 23.0)
        # --------------------------------------------------------------
        # Operator GREATER_OR_EQUAL.
        # - int type.
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate(21, 2))
        self.assertFalse(Operator.GREATER_OR_EQUAL.evaluate(3, 23))
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate(2, 2))
        # - float type.
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate(21.0, 2.0))
        self.assertFalse(Operator.GREATER_OR_EQUAL.evaluate(3.0, 23.0))
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate(2.0, 2.0))
        # - str type.
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate("bcd", "abc"))
        self.assertFalse(Operator.GREATER_OR_EQUAL.evaluate("abc", "bcd"))
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate("abc", "abc"))
        # - int and float types.
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate(20.0, 3))
        self.assertFalse(Operator.GREATER_OR_EQUAL.evaluate(1, 2.0))
        self.assertTrue(Operator.GREATER_OR_EQUAL.evaluate(2.0, 2))
        # - str and any numeric types (they do not support this operator).
        self.assertRaises(TypeError, Operator.GREATER_OR_EQUAL.evaluate, "a", 23.0)
        self.assertRaises(TypeError, Operator.GREATER_OR_EQUAL.evaluate, "12", 23.0)
        self.assertRaises(TypeError, Operator.GREATER_OR_EQUAL.evaluate, "120", 23.0)
        self.assertRaises(TypeError, Operator.GREATER_OR_EQUAL.evaluate, "23.0", 23.0)
        # --------------------------------------------------------------

    def test_Operator_evaluate_method_with_pandasSeries(self) -> None:
        self.assertTrue((Operator.EQUAL.evaluate(Series([1,2,3,4,5]), 5) == Series([False, False, False, False, True])).all())
        self.assertTrue((Operator.EQUAL.evaluate(45, Series([1,2,3,4,5])) == Series([False, False, False, False, False])).all())
        self.assertTrue((Operator.NOT_EQUAL.evaluate("45", Series(["1","2","3","4","5"])) == Series([True, True, True, True, True])).all())
        self.assertTrue((Operator.NOT_EQUAL.evaluate(Series(["1","2","3","4","5"]), "5") == Series([True, True, True, True, False])).all())
        self.assertTrue((Operator.EQUAL.evaluate("45", Series([1,2,3,4,5])) == Series([False, False, False, False, False])).all())
        self.assertTrue((Operator.LESS.evaluate(45, Series([1,2,3,4,5])) == Series([False, False, False, False, False])).all())
        self.assertTrue((Operator.GREATER.evaluate(45, Series([1,2,3,4,5])) == Series([True, True, True, True, True])).all())

    def test_Operator_generate_from_str_method(self) -> None:
        self.assertEqual(Operator.generate_from_str("="), Operator.EQUAL)
        self.assertEqual(Operator.generate_from_str("!="), Operator.NOT_EQUAL)
        self.assertEqual(Operator.generate_from_str("<"), Operator.LESS)
        self.assertEqual(Operator.generate_from_str(">"), Operator.GREATER)
        self.assertEqual(Operator.generate_from_str("<="), Operator.LESS_OR_EQUAL)
        self.assertEqual(Operator.generate_from_str(">="), Operator.GREATER_OR_EQUAL)

    def test_Operator_string_representation(self) -> None:
        self.assertEqual(str(Operator.EQUAL), "=")
        self.assertEqual(str(Operator.NOT_EQUAL), "!=")
        self.assertEqual(str(Operator.LESS), "<")
        self.assertEqual(str(Operator.GREATER), ">")
        self.assertEqual(str(Operator.LESS_OR_EQUAL), "<=")
        self.assertEqual(str(Operator.GREATER_OR_EQUAL), ">=")
