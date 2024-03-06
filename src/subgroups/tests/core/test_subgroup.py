# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'core/subgroup.py'.
"""

from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.core.operator import Operator
from pandas import DataFrame, Series
import unittest

class TestSubgroup(unittest.TestCase):

    def test_Subgroup_general(self):
        subgroup1 = Subgroup.generate_from_str("Description: [], Target: age = 34")
        self.assertEqual(subgroup1.description, Pattern([]))
        self.assertEqual(subgroup1.target, Selector.generate_from_str("age = 34"))
        subgroup2 = Subgroup.generate_from_str("Description: [at1 = 'a', at2 >= 78], Target: age = 34")
        subgroup3 = subgroup2.copy()
        self.assertNotEqual(id(subgroup2), id(subgroup3))
        self.assertNotEqual(id(subgroup2.description), id(subgroup3.description))
        self.assertNotEqual(id(subgroup2.description._list_of_selectors), id(subgroup3.description._list_of_selectors))
        self.assertEqual(id(subgroup2.target), id(subgroup3.target))
        self.assertIsNot(subgroup2, subgroup3)
        self.assertIsNot(subgroup2.description, subgroup3.description)
        self.assertIsNot(subgroup2.description._list_of_selectors, subgroup3.description._list_of_selectors)
        self.assertIs(subgroup2.target, subgroup3.target)
        subgroup4 = Subgroup(Pattern([Selector("at1", Operator.EQUAL, 'a'), Selector("at2", Operator.GREATER_OR_EQUAL, 78)]), Selector("age", Operator.EQUAL, 34))
        self.assertNotEqual(subgroup1, subgroup2)
        self.assertEqual(subgroup2, subgroup4)
        self.assertEqual(subgroup3, subgroup4)
        self.assertEqual(str(Subgroup(Pattern([Selector("a", Operator.NOT_EQUAL, 'value'), Selector("b", Operator.GREATER_OR_EQUAL, 78)]), Selector("age", Operator.LESS, 34))), str(Subgroup.generate_from_str("Description: [a != value, b >= 78], Target: age < 34")))
    
    def test_Subgroup_filter(self):
        df = DataFrame({"a" : [1,5,6,9], "b" : [55,69,52,51], "target" : [0,1,0,1]})
        subgroup1 = Subgroup(Pattern.generate_from_str("[a > 5, b < 55]"), Selector("target", Operator.EQUAL, 1))
        series_tp, series_fp, series_TP = subgroup1.filter(df)
        self.assertEqual(len(series_tp), 4)
        self.assertEqual(len(series_fp), 4)
        self.assertEqual(len(series_TP), 4)
        self.assertTrue((series_tp == Series([False, False, False, True])).all())
        self.assertTrue((series_fp == Series([False, False, True, False])).all())
        self.assertTrue((series_TP == Series([False, True, False, True])).all())
        series_FP = ~ series_TP
        self.assertTrue((series_FP == Series([True, False, True, False])).all())
        df_only_tp = DataFrame({"a" : [9], "b" : [51], "target" : [1]})
        df_only_fp = DataFrame({"a" : [6], "b" : [52], "target" : [0]})
        df_only_TP = DataFrame({"a" : [5,9], "b" : [69,51], "target" : [1,1]})
        df_series_tp = df[series_tp]
        df_series_tp.reset_index(drop=True, inplace=True)
        df_series_fp = df[series_fp]
        df_series_fp.reset_index(drop=True, inplace=True)
        df_series_TP = df[series_TP]
        df_series_TP.reset_index(drop=True, inplace=True)
        self.assertTrue((df_series_tp == df_only_tp).all().all())
        self.assertTrue((df_series_fp == df_only_fp).all().all())
        self.assertTrue((df_series_TP == df_only_TP).all().all())
        self.assertEqual(len(df_only_tp), 1)
        self.assertEqual(len(df_only_fp), 1)
        self.assertEqual(len(df_only_TP), 2)
        self.assertEqual(sum(series_tp), 1)
        self.assertEqual(sum(series_fp), 1)
        self.assertEqual(sum(series_TP), 2)
        self.assertRaises(KeyError, subgroup1.filter, DataFrame({"at1" : [1,5,6,9], "b" : [55,69,52,51], "target" : [0,1,0,1]}))
        self.assertRaises(KeyError, subgroup1.filter, DataFrame({"a" : [1,5,6,9], "b" : [55,69,52,51], "class" : [0,1,0,1]}))
    
    def test_Subgroup_is_refinement_method(self) -> None:
        s1 = Subgroup.generate_from_str("Description: [lug_boot = 'high'], Target: safety = 'acc'")
        s2 = Subgroup.generate_from_str("Description: [doors = '4'], Target: safety = 'acc'")
        s3 = Subgroup.generate_from_str("Description: [doors = '4', lug_boot = 'high'], Target: safety = 'acc'")
        s4 = Subgroup.generate_from_str("Description: [lug_boot = 'high', at5 = 'v', doors = '4'], Target: safety = 'acc'")
        s5 = Subgroup.generate_from_str("Description: [at5 = 'v'], Target: safety = 'acc'")
        s6 = Subgroup.generate_from_str("Description: [at7 = 'z'], Target: safety = 'acc'")
        s7 = Subgroup.generate_from_str("Description: [at5 = 'v', lug_boot = 'high', doors = '4'], Target: safety = 'acc'")
        s8 = Subgroup.generate_from_str("Description: [lug_boot = 'high', at5 = 'v'], Target: safety = 'acc'")
        self.assertTrue(s1.is_refinement(s3, refinement_of_itself = False))
        self.assertTrue(s1.is_refinement(s4, refinement_of_itself = False))
        self.assertTrue(s2.is_refinement(s3, refinement_of_itself = False))
        self.assertTrue(s2.is_refinement(s4, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s1, refinement_of_itself = False))
        self.assertFalse(s4.is_refinement(s1, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s2, refinement_of_itself = False))
        self.assertFalse(s4.is_refinement(s2, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s1, refinement_of_itself = False))
        self.assertFalse(s2.is_refinement(s2, refinement_of_itself = False))
        self.assertFalse(s4.is_refinement(s7, refinement_of_itself = False))
        self.assertTrue(s8.is_refinement(s7, refinement_of_itself = False))
        self.assertFalse(s5.is_refinement(s1, refinement_of_itself = False))
        self.assertFalse(s5.is_refinement(s3, refinement_of_itself = False))
        self.assertFalse(s6.is_refinement(s1, refinement_of_itself = False))
        self.assertFalse(s6.is_refinement(s3, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s5, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s5, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s6, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s6, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s1, refinement_of_itself = False))
        self.assertFalse(s2.is_refinement(s2, refinement_of_itself = False))
        self.assertTrue(s1.is_refinement(s1, refinement_of_itself = True))
        self.assertTrue(s2.is_refinement(s2, refinement_of_itself = True))
        s9 = Subgroup.generate_from_str("Description: [lug_boot = 'high'], Target: safety = 'other'")
        s10 = Subgroup.generate_from_str("Description: [doors = '4'], Target: safety = 'other'")
        s11 = Subgroup.generate_from_str("Description: [doors = '4', lug_boot = 'high'], Target: safety = 'other'")
        s12 = Subgroup.generate_from_str("Description: [lug_boot = 'high', at5 = 'v', doors = '4'], Target: safety = 'other'")
        s13 = Subgroup.generate_from_str("Description: [at5 = 'v'], Target: safety = 'other'")
        s14 = Subgroup.generate_from_str("Description: [at7 = 'z'], Target: safety = 'other'")
        s15 = Subgroup.generate_from_str("Description: [at5 = 'v', lug_boot = 'high', doors = '4'], Target: safety = 'other'")
        self.assertFalse(s1.is_refinement(s11, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s12, refinement_of_itself = False))
        self.assertFalse(s2.is_refinement(s11, refinement_of_itself = False))
        self.assertFalse(s2.is_refinement(s12, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s9, refinement_of_itself = False))
        self.assertFalse(s4.is_refinement(s9, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s10, refinement_of_itself = False))
        self.assertFalse(s4.is_refinement(s10, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s10, refinement_of_itself = False))
        self.assertFalse(s2.is_refinement(s10, refinement_of_itself = False))
        self.assertFalse(s4.is_refinement(s15, refinement_of_itself = False))
        self.assertFalse(s8.is_refinement(s15, refinement_of_itself = False))
        self.assertFalse(s5.is_refinement(s9, refinement_of_itself = False))
        self.assertFalse(s5.is_refinement(s11, refinement_of_itself = False))
        self.assertFalse(s6.is_refinement(s9, refinement_of_itself = False))
        self.assertFalse(s6.is_refinement(s11, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s13, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s13, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s14, refinement_of_itself = False))
        self.assertFalse(s3.is_refinement(s14, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s9, refinement_of_itself = False))
        self.assertFalse(s2.is_refinement(s10, refinement_of_itself = False))
        self.assertFalse(s1.is_refinement(s9, refinement_of_itself = True))
        self.assertFalse(s2.is_refinement(s10, refinement_of_itself = True))
