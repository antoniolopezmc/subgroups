# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'core/selector.py'.
"""

from subgroups.core.selector import Selector
from weakref import WeakValueDictionary
from subgroups.core.operator import Operator
import unittest

class TestSelector(unittest.TestCase):

    def setUp(self) -> None:
        # IMPORTANT: DO NOT NEVER DO THIS WHEN USING THE LIBRARY!!!
        # - In this case, we have to do it in order to avoid stored selectors from previous tests and, therefore, to start this test with 0 selectors.
        Selector._dict_of_selectors = WeakValueDictionary()

    def test_Selector_creation_process(self) -> None:
        # --------------------------------------------------------------
        self.assertEqual(len(Selector._dict_of_selectors), 0)
        selector1 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector2 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector3 = Selector("a", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector4 = Selector("a", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector5 = Selector("a", Operator.LESS, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector6 = Selector("a", Operator.LESS, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector7 = Selector("a", Operator.GREATER, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 4)
        selector8 = Selector("qwe", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector9 = Selector("qwe", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector10 = Selector("qwe", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector11 = Selector("qwe", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector12 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector13 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector14 = Selector("qwe", Operator.GREATER_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        # --------------------------------------------------------------
        self.assertEqual(id(selector1), id(selector2))
        self.assertEqual(id(selector3), id(selector4))
        self.assertEqual(id(selector5), id(selector6))
        self.assertNotEqual(id(selector1), id(selector7))
        self.assertNotEqual(id(selector2), id(selector7))
        self.assertNotEqual(id(selector3), id(selector7))
        self.assertNotEqual(id(selector4), id(selector7))
        self.assertNotEqual(id(selector5), id(selector7))
        self.assertNotEqual(id(selector6), id(selector7))
        # --------------------------------------------------------------
        self.assertIs(selector1, selector2)
        self.assertIs(selector3, selector4)
        self.assertIs(selector5, selector6)
        self.assertIsNot(selector1, selector7)
        self.assertIsNot(selector2, selector7)
        self.assertIsNot(selector3, selector7)
        self.assertIsNot(selector4, selector7)
        self.assertIsNot(selector5, selector7)
        self.assertIsNot(selector6, selector7)
        # --------------------------------------------------------------
        self.assertEqual(id(selector8), id(selector9))
        self.assertEqual(id(selector10), id(selector11))
        self.assertEqual(id(selector12), id(selector13))
        self.assertNotEqual(id(selector8), id(selector14))
        self.assertNotEqual(id(selector9), id(selector14))
        self.assertNotEqual(id(selector10), id(selector14))
        self.assertNotEqual(id(selector11), id(selector14))
        self.assertNotEqual(id(selector12), id(selector14))
        self.assertNotEqual(id(selector13), id(selector14))
        # --------------------------------------------------------------
        self.assertIs(selector8, selector9)
        self.assertIs(selector10, selector11)
        self.assertIs(selector12, selector13)
        self.assertIsNot(selector8, selector14)
        self.assertIsNot(selector9, selector14)
        self.assertIsNot(selector10, selector14)
        self.assertIsNot(selector11, selector14)
        self.assertIsNot(selector12, selector14)
        self.assertIsNot(selector13, selector14)
        # --------------------------------------------------------------
        self.assertNotEqual(id(selector1), id(selector8))
        self.assertNotEqual(id(selector2), id(selector9))
        self.assertNotEqual(id(selector3), id(selector10))
        self.assertNotEqual(id(selector4), id(selector11))
        self.assertNotEqual(id(selector5), id(selector12))
        self.assertNotEqual(id(selector6), id(selector13))
        self.assertNotEqual(id(selector7), id(selector14))
        # --------------------------------------------------------------
        self.assertIsNot(selector1, selector8)
        self.assertIsNot(selector2, selector9)
        self.assertIsNot(selector3, selector10)
        self.assertIsNot(selector4, selector11)
        self.assertIsNot(selector5, selector12)
        self.assertIsNot(selector6, selector13)
        self.assertIsNot(selector7, selector14)
        # --------------------------------------------------------------
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        del selector1
        del selector2
        del selector3
        del selector4
        del selector5
        del selector6
        del selector7
        del selector8
        del selector9
        del selector10
        del selector11
        del selector12
        del selector13
        del selector14
        self.assertEqual(len(Selector._dict_of_selectors), 0)

    def test_Selector_deletion_process(self) -> None:
        # --------------------------------------------------------------
        self.assertEqual(len(Selector._dict_of_selectors), 0)
        selector1 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector2 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector3 = Selector("a", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector4 = Selector("a", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector5 = Selector("a", Operator.LESS, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector6 = Selector("a", Operator.LESS, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector7 = Selector("a", Operator.GREATER, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 4)
        selector8 = Selector("qwe", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector9 = Selector("qwe", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector10 = Selector("qwe", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector11 = Selector("qwe", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector12 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector13 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector14 = Selector("qwe", Operator.GREATER_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        # --------------------------------------------------------------
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        del selector1
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        del selector2
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        del selector3
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        del selector4
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        del selector5
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        del selector6
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        del selector7
        self.assertEqual(len(Selector._dict_of_selectors), 4)
        del selector8
        self.assertEqual(len(Selector._dict_of_selectors), 4)
        del selector9
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        del selector10
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        del selector11
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        del selector12
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        del selector13
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        del selector14
        self.assertEqual(len(Selector._dict_of_selectors), 0)
        # --------------------------------------------------------------
        self.assertEqual(len(Selector._dict_of_selectors), 0)
        selector1 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector2 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector3 = Selector("a", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector4 = Selector("a", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector5 = Selector("a", Operator.LESS, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector6 = Selector("a", Operator.LESS, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector7 = Selector("a", Operator.GREATER, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 4)
        selector8 = Selector("qwe", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector9 = Selector("qwe", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector10 = Selector("qwe", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector11 = Selector("qwe", Operator.EQUAL, 45)
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector12 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector13 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector14 = Selector("qwe", Operator.GREATER_OR_EQUAL, 52)
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        # --------------------------------------------------------------
        self.assertEqual(len(Selector._dict_of_selectors), 8)
        selector14 = None
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector13 = None
        self.assertEqual(len(Selector._dict_of_selectors), 7)
        selector12 = None
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector11 = None
        self.assertEqual(len(Selector._dict_of_selectors), 6)
        selector10 = None
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector9 = None
        self.assertEqual(len(Selector._dict_of_selectors), 5)
        selector8 = None
        self.assertEqual(len(Selector._dict_of_selectors), 4)
        selector7 = None
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector6 = None
        self.assertEqual(len(Selector._dict_of_selectors), 3)
        selector5 = None
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector4 = None
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector3 = None
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector2 = None
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector1 = None
        self.assertEqual(len(Selector._dict_of_selectors), 0)

    def test_Selector_same_value_different_type(self) -> None:
        self.assertEqual(len(Selector._dict_of_selectors), 0)
        selector1 = Selector("a", Operator.EQUAL, 23)
        self.assertEqual(len(Selector._dict_of_selectors), 1)
        selector2 = Selector("a", Operator.EQUAL, "23") # The type of the value is different. For this reason, the selector must be also different.
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        selector3 = Selector("a", Operator.EQUAL, 23)
        selector4 = Selector("a", Operator.EQUAL, "23")
        self.assertEqual(len(Selector._dict_of_selectors), 2)
        self.assertEqual(id(selector1), id(selector3))
        self.assertEqual(id(selector2), id(selector4))
        self.assertNotEqual(id(selector1), id(selector2))
        self.assertNotEqual(id(selector3), id(selector4))
        self.assertIs(selector1, selector3)
        self.assertIs(selector2, selector4)
        self.assertIsNot(selector1, selector2)
        self.assertIsNot(selector3, selector4)

    def test_Selector_attributes(self) -> None:
        # These examples must run ok.
        selector1 = Selector("attribute_name_1", Operator.EQUAL, "value_1")
        self.assertEqual(selector1.attribute_name, "attribute_name_1")
        self.assertEqual(selector1.operator, Operator.EQUAL)
        self.assertEqual(selector1.value, "value_1")
        self.assertIs(type(selector1.value), str)
        self.assertEqual(str(selector1), "attribute_name_1 = \'value_1\'")
        selector2 = Selector("attribute_name_2", Operator.NOT_EQUAL, "value_2")
        self.assertEqual(selector2.attribute_name, "attribute_name_2")
        self.assertEqual(selector2.operator, Operator.NOT_EQUAL)
        self.assertEqual(selector2.value, "value_2")
        self.assertIs(type(selector2.value), str)
        self.assertEqual(str(selector2), "attribute_name_2 != \'value_2\'")
        selector3 = Selector("attribute_name_3", Operator.LESS, 90)
        self.assertEqual(selector3.attribute_name, "attribute_name_3")
        self.assertEqual(selector3.operator, Operator.LESS)
        self.assertEqual(selector3.value, 90)
        self.assertIs(type(selector3.value), int)
        self.assertEqual(str(selector3), "attribute_name_3 < 90")
        selector4 = Selector("attribute_name_4", Operator.LESS_OR_EQUAL, 5.045)
        self.assertEqual(selector4.attribute_name, "attribute_name_4")
        self.assertEqual(selector4.operator, Operator.LESS_OR_EQUAL)
        self.assertEqual(selector4.value, 5.045)
        self.assertIs(type(selector4.value), float)
        self.assertEqual(str(selector4), "attribute_name_4 <= 5.045")
        selector5 = Selector("attribute_name_5", Operator.EQUAL, "5.045")
        self.assertEqual(selector5.attribute_name, "attribute_name_5")
        self.assertEqual(selector5.operator, Operator.EQUAL)
        self.assertEqual(selector5.value, "5.045")
        self.assertIs(type(selector5.value), str)
        self.assertEqual(str(selector5), "attribute_name_5 = \'5.045\'")
        # These examples must not raise an exception.
        selector6 = Selector("", Operator.GREATER_OR_EQUAL, 60)
        selector7 = Selector("attribute_name_7", Operator.NOT_EQUAL, "")
        # These examples must raise an exception.
        self.assertRaises(TypeError, Selector, 45, Operator.GREATER_OR_EQUAL, 60)
        self.assertRaises(TypeError, Selector, "attribute_name_9", 45, 60)
        self.assertRaises(TypeError, Selector, "attribute_name_10", "hello", 60)
        self.assertRaises(ValueError, Selector, "attribute_name_11", Operator.GREATER_OR_EQUAL, "value_11") # If the value is of type str, only the operators "=" and "!=" are available.

    def test_Selector_match_method(self) -> None:
        selector1 = Selector("a", Operator.EQUAL, 23)
        selector2 = Selector("a", Operator.GREATER, 23)
        self.assertTrue(selector1.match("a", 23))
        self.assertFalse(selector1.match("a", 30))
        self.assertFalse(selector1.match("z", 30))
        self.assertFalse(selector1.match("a", 30.0))
        self.assertFalse(selector1.match("a", "23"))
        self.assertTrue(selector2.match("a", 30))
        self.assertFalse(selector2.match("a", 5))
        self.assertFalse(selector2.match("z", 5))
        self.assertTrue(selector2.match("a", 30.0))
        # These examples must raise an exception (the exception that appears in 'except').
        self.assertRaises(TypeError, selector2.match, "a", "30") # The method raises a TypeError exception with these parameters, because we cannot apply the operator '>' between a str and an int.
        selector3 = Selector("attribute_name_3", Operator.EQUAL, "value_3")
        self.assertRaises(TypeError, selector3.match, 12, "value_3")

    def test_Selector_generate_from_str_method(self) -> None:
        self.assertEqual(Selector.generate_from_str("a = 23"), Selector("a", Operator.EQUAL, 23))
        self.assertEqual(Selector.generate_from_str("a != 23"), Selector("a", Operator.NOT_EQUAL, 23))
        self.assertEqual(Selector.generate_from_str("a < 23"), Selector("a", Operator.LESS, 23))
        self.assertEqual(Selector.generate_from_str("a > 23"), Selector("a", Operator.GREATER, 23))
        self.assertEqual(Selector.generate_from_str("a <= 23"), Selector("a", Operator.LESS_OR_EQUAL, 23))
        self.assertEqual(Selector.generate_from_str("a >= 23"), Selector("a", Operator.GREATER_OR_EQUAL, 23))
        self.assertIs(type(Selector.generate_from_str("a >= 23").value), int)
        self.assertEqual(Selector.generate_from_str("a > 23.06"), Selector("a", Operator.GREATER, 23.06))
        self.assertIs(type(Selector.generate_from_str("a > 23.06").value), float)
        self.assertEqual(Selector.generate_from_str("a != 'hello'"), Selector("a", Operator.NOT_EQUAL, "hello"))
        self.assertIs(type(Selector.generate_from_str("a != 'hello'").value), str)
        self.assertEqual(Selector.generate_from_str("a != 'hello'").value, "hello")
        self.assertEqual(Selector.generate_from_str('a != "hello"'), Selector("a", Operator.NOT_EQUAL, "hello"))
        self.assertIs(type(Selector.generate_from_str('a != "hello"').value), str)
        self.assertEqual(Selector.generate_from_str('a != "hello"').value, "hello")
        self.assertEqual(Selector.generate_from_str("a != \'hello\'"), Selector("a", Operator.NOT_EQUAL, "hello"))
        self.assertIs(type(Selector.generate_from_str("a != \'hello\'").value), str)
        self.assertEqual(Selector.generate_from_str("a != \'hello\'").value, "hello")
        self.assertEqual(Selector.generate_from_str('a != \"hello\"'), Selector("a", Operator.NOT_EQUAL, "hello"))
        self.assertIs(type(Selector.generate_from_str('a != \"hello\"').value), str)
        self.assertEqual(Selector.generate_from_str('a != \"hello\"').value, "hello")
        self.assertEqual(Selector.generate_from_str("a != hello"), Selector("a", Operator.NOT_EQUAL, "hello"))
        self.assertIs(type(Selector.generate_from_str("a != hello").value), str)
        self.assertEqual(Selector.generate_from_str("a != hello").value, "hello")
        self.assertEqual(Selector.generate_from_str("a != 25.36.12"), Selector("a", Operator.NOT_EQUAL, "25.36.12"))
        self.assertIs(type(Selector.generate_from_str("a != 25.36.12").value), str)
        self.assertEqual(Selector.generate_from_str("a != 25.36.12").value, "25.36.12")
        self.assertRaises(ValueError, Selector.generate_from_str, "a < 'hello'") # If the value is a string, only equal and not equal operators are valid.

    def test_Selector_comparisons(self) -> None:
        selector1 = Selector("a", Operator.EQUAL, 23)
        selector2 = Selector("a", Operator.EQUAL, 23)
        selector3 = Selector("a", Operator.NOT_EQUAL, 23)
        selector4 = Selector("b", Operator.EQUAL, 23)
        selector5 = Selector("a", Operator.EQUAL, 25)
        # ------------------------------------------------------------------
        self.assertTrue(selector1 == selector2)
        self.assertTrue(selector1 <= selector2)
        self.assertTrue(selector1 >= selector2)
        self.assertTrue(selector1 != selector3)
        self.assertTrue(selector1 < selector3)
        self.assertFalse(selector1 > selector3)
        self.assertTrue(selector1 <= selector3)
        self.assertFalse(selector1 >= selector3)
        self.assertTrue(selector1 < selector4)
        self.assertFalse(selector1 == selector5)
        self.assertTrue(selector1 != selector5)
        self.assertTrue(selector1 < selector5)
        self.assertTrue(selector1 <= selector5)
        self.assertFalse(selector1 > selector5)
        self.assertFalse(selector1 >= selector5)
        # ------------------------------------------------------------------
        self.assertEqual(selector1, selector2)
        self.assertLessEqual(selector1, selector2)
        self.assertGreaterEqual(selector1, selector2)
        self.assertNotEqual(selector1, selector3)
        self.assertLess(selector1, selector3)
        self.assertLessEqual(selector1, selector3)
        self.assertLessEqual(selector1, selector3)
        self.assertLess(selector1, selector3)
        self.assertLess(selector1, selector4)
        self.assertNotEqual(selector1, selector5)
        self.assertNotEqual(selector1, selector5)
        self.assertLess(selector1, selector5)
        self.assertLessEqual(selector1, selector5)
        self.assertLessEqual(selector1, selector5)
        self.assertLess(selector1, selector5)
