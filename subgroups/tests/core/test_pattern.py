# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'core/pattern.py'.
"""

from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.operator import Operator
from subgroups.core.subgroup import Subgroup
from pandas import Series, DataFrame
import unittest

class TestPattern(unittest.TestCase):

    def test_Pattern_general(self) -> None:
        self.assertEqual(Pattern.generate_from_str("[]"), Pattern([]))
        pattern_1 = Pattern([Selector("name", Operator.EQUAL, "name1"), Selector("age", Operator.LESS, 25), \
                            Selector("age", Operator.GREATER, 78), Selector("att2", Operator.GREATER_OR_EQUAL, 25), \
                            Selector("age", Operator.GREATER, 78), Selector("att2", Operator.GREATER_OR_EQUAL, 25)])
        self.assertEqual(Pattern.generate_from_str("[age < 25, name = 'name1', name = name1, att2 >= 25, age > 78, age < 25]"), pattern_1)
        self.assertEqual(len(pattern_1), 4)
        pattern_2 = Pattern([Selector("name", Operator.EQUAL, "name1"), Selector("name", Operator.EQUAL, "name1"), \
                            Selector("name", Operator.EQUAL, "name1"), Selector("name", Operator.EQUAL, "name1"), \
                            Selector("age", Operator.GREATER, 78), Selector("name", Operator.EQUAL, "name1")])
        self.assertEqual(len(pattern_2), 2)
        self.assertIn(Selector("name", Operator.EQUAL, "name1"), pattern_2)
        self.assertNotIn(Selector("att2", Operator.GREATER_OR_EQUAL, 128), pattern_2)
        self.assertNotIn(Selector("att2", Operator.GREATER_OR_EQUAL, 128), pattern_1)
        pattern_2.add_selector(Selector("att2", Operator.GREATER_OR_EQUAL, 128))
        self.assertEqual(len(pattern_2), 3)
        self.assertIn(Selector("att2", Operator.GREATER_OR_EQUAL, 128), pattern_2)
        self.assertEqual(pattern_2.get_selector(0), Selector("age", Operator.GREATER, 78))
        pattern_2.add_selector(Selector("aaaaa", Operator.GREATER_OR_EQUAL, -789))
        self.assertEqual(pattern_2.get_selector(0), Selector("aaaaa", Operator.GREATER_OR_EQUAL, -789))
        self.assertEqual(len(pattern_2), 4)
        self.assertEqual(str(pattern_2), str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = name1]")))
        self.assertEqual(str(pattern_2), str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = 'name1']")))
        self.assertEqual(str(pattern_2), str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = name1, aaaaa >= -789, age > 78, att2 >= 128, name = name1]")))
        self.assertEqual(str(pattern_2), str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = 'name1', aaaaa >= -789, age > 78, att2 >= 128, name = 'name1']")))
        self.assertEqual(str(pattern_2), "[aaaaa >= -789, age > 78, att2 >= 128, name = 'name1']")
        self.assertEqual(pattern_1, pattern_1)
        self.assertEqual(pattern_1, pattern_1.copy())
        self.assertNotEqual(pattern_1, pattern_2)
        self.assertNotEqual(pattern_1, pattern_2.copy())
        self.assertNotEqual(id(pattern_1._list_of_selectors), id(pattern_1.copy()._list_of_selectors))
        self.assertNotEqual(id(pattern_2._list_of_selectors), id(pattern_2.copy()._list_of_selectors))
        self.assertNotEqual(id(pattern_1._list_of_selectors), id(pattern_2.copy()._list_of_selectors))
        self.assertIsNot(pattern_1._list_of_selectors, pattern_1.copy()._list_of_selectors)
        self.assertIsNot(pattern_2._list_of_selectors, pattern_2.copy()._list_of_selectors)
        self.assertIsNot(pattern_1._list_of_selectors, pattern_2.copy()._list_of_selectors)
        index = 0
        for elem in pattern_2:
            self.assertEqual(elem, pattern_2.get_selector(index))
            index = index + 1
        pattern_2.remove_selector(Selector.generate_from_str("age > 78"))
        self.assertEqual(len(pattern_2), 3)
        self.assertEqual(pattern_2.get_selector(0), Selector.generate_from_str("aaaaa >= -789"))
        self.assertEqual(pattern_2.get_selector(1), Selector.generate_from_str("att2 >= 128"))
        pattern_2.remove_selector(Selector.generate_from_str("age > 78"))
        self.assertEqual(len(pattern_2), 3)
        self.assertEqual(pattern_2.get_selector(0), Selector.generate_from_str("aaaaa >= -789"))
        self.assertEqual(pattern_2.get_selector(1), Selector.generate_from_str("att2 >= 128"))
        pattern_2.add_selector(Selector.generate_from_str("name = 'name1'"))
        self.assertEqual(len(pattern_2), 3)
        self.assertEqual(pattern_2.get_selector(0), Selector.generate_from_str("aaaaa >= -789"))
        self.assertEqual(pattern_2.get_selector(1), Selector.generate_from_str("att2 >= 128"))
        pattern_3 = Pattern([])
        self.assertEqual(len(pattern_3), 0)
        pattern_3.remove_selector(Selector("age", Operator.GREATER, 78))
        self.assertEqual(len(pattern_3), 0)
        self.assertRaises(IndexError, pattern_3.get_selector, 125)
        pattern_4 = Pattern.generate_from_str("[age < 25, name = 'name1', name = name1, att2 >= 25, age > 78, age < 25]")
        self.assertEqual(len(pattern_4), 4)
        pattern_4.add_selector(Selector("zzzz", Operator.EQUAL, "value4"))
        self.assertEqual(len(pattern_4), 5)
        pattern_4.remove_selector(Selector("zzzz", Operator.EQUAL, "value4"))
        self.assertEqual(len(pattern_4), 4)
        self.assertEqual(str(pattern_4), "[age < 25, age > 78, att2 >= 25, name = 'name1']")
        pattern_4.remove_selector_by_index(1)
        self.assertEqual(len(pattern_4), 3)
        self.assertEqual(str(pattern_4), "[age < 25, att2 >= 25, name = 'name1']")
        self.assertRaises(IndexError, pattern_3.remove_selector_by_index, 125)
        Pattern([]).remove_selector(Selector.generate_from_str("aaaaa >= -789"))

    def test_Pattern_is_contained_method(self) -> None:
        self.assertTrue((Pattern([]).is_contained(DataFrame({"a" : [1,2,3], "b" : [7,8,9], "c" : ["a", "b", "c"]}))).all())
        self.assertTrue((Pattern.generate_from_str("[a < 25, b >= 25, c = 'b']").is_contained(DataFrame({"a" : [1,2,3], "b" : [7,8,9], "c" : ["a", "b", "c"]})) == Series([False, False, False])).all())
        self.assertTrue((Pattern.generate_from_str("[a < 25, b >= 25, c = 'b']").is_contained(DataFrame({"a" : [1,2,3], "b" : [7,125,9], "c" : ["a", "b", "c"]})) == Series([False, True, False])).all())
        self.assertTrue((Pattern.generate_from_str("[a < 25, b >= 25, c = 'b']").is_contained(DataFrame({"a" : [1,2,3], "b" : [71,125,25], "c" : ["b", "b", "b"]})) == Series([True, True, True])).all())
        self.assertRaises(KeyError, Pattern.generate_from_str("[age < 25, name = 'name1', att2 >= 25, age > 78]").is_contained, DataFrame({"a" : [1,2,3], "b" : [7,8,9], "c" : ["a", "b", "c"]}))

    def test_Pattern_is_refinement_method(self) -> None:
        s1 = Subgroup.generate_from_str("Description: [lug_boot = 'high'], Target: safety = 'acc'")
        s2 = Subgroup.generate_from_str("Description: [doors = '4'], Target: safety = 'acc'")
        s3 = Subgroup.generate_from_str("Description: [doors = '4', lug_boot = 'high'], Target: safety = 'acc'")
        s4 = Subgroup.generate_from_str("Description: [lug_boot = 'high', at5 = 'v', doors = '4'], Target: safety = 'acc'")
        s5 = Subgroup.generate_from_str("Description: [at5 = 'v'], Target: safety = 'acc'")
        s6 = Subgroup.generate_from_str("Description: [at7 = 'z'], Target: safety = 'acc'")
        s7 = Subgroup.generate_from_str("Description: [at5 = 'v', lug_boot = 'high', doors = '4'], Target: safety = 'acc'")
        s8 = Subgroup.generate_from_str("Description: [lug_boot = 'high', at5 = 'v'], Target: safety = 'acc'")
        self.assertTrue(s1.description.is_refinement(s3.description, refinement_of_itself = False))
        self.assertTrue(s1.description.is_refinement(s4.description, refinement_of_itself = False))
        self.assertTrue(s2.description.is_refinement(s3.description, refinement_of_itself = False))
        self.assertTrue(s2.description.is_refinement(s4.description, refinement_of_itself = False))
        self.assertFalse(s3.description.is_refinement(s1.description, refinement_of_itself = False))
        self.assertFalse(s4.description.is_refinement(s1.description, refinement_of_itself = False))
        self.assertFalse(s3.description.is_refinement(s2.description, refinement_of_itself = False))
        self.assertFalse(s4.description.is_refinement(s2.description, refinement_of_itself = False))
        self.assertFalse(s1.description.is_refinement(s1.description, refinement_of_itself = False))
        self.assertFalse(s2.description.is_refinement(s2.description, refinement_of_itself = False))
        self.assertFalse(s4.description.is_refinement(s7.description, refinement_of_itself = False))
        self.assertTrue(s8.description.is_refinement(s7.description, refinement_of_itself = False))
        self.assertFalse(s5.description.is_refinement(s1.description, refinement_of_itself = False))
        self.assertFalse(s5.description.is_refinement(s3.description, refinement_of_itself = False))
        self.assertFalse(s6.description.is_refinement(s1.description, refinement_of_itself = False))
        self.assertFalse(s6.description.is_refinement(s3.description, refinement_of_itself = False))
        self.assertFalse(s1.description.is_refinement(s5.description, refinement_of_itself = False))
        self.assertFalse(s3.description.is_refinement(s5.description, refinement_of_itself = False))
        self.assertFalse(s1.description.is_refinement(s6.description, refinement_of_itself = False))
        self.assertFalse(s3.description.is_refinement(s6.description, refinement_of_itself = False))
        self.assertFalse(s1.description.is_refinement(s1.description, refinement_of_itself = False))
        self.assertFalse(s2.description.is_refinement(s2.description, refinement_of_itself = False))
        self.assertTrue(s1.description.is_refinement(s1.description, refinement_of_itself = True))
        self.assertTrue(s2.description.is_refinement(s2.description, refinement_of_itself = True))
