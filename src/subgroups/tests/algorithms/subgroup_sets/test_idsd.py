# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles <franciscojose.morac@um.es>

"""Tests of the functionality contained in the file 'algorithms/subgroup_sets/idsd.py'.
"""

from os import remove
from pandas import DataFrame
from subgroups.algorithms.subgroup_sets.idsd import IDSD
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
import unittest

class TestIDSD(unittest.TestCase):

    def test_IDSD_init_method1(self):
        # Test with valid parameters
        obj = IDSD(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                           or_thld=1.0, p_val_thld=0.1, abs_contribution_thld=0.3,
                           contribution_thld=4, write_results_in_file=True,
                           file_path='results.txt')    
        # Assert that the object is created without any exceptions
        self.assertIsNotNone(obj)
    
    def test_IDSD_init_method2(self):
        # Test with valid parameters, only the required ones
        obj = IDSD(num_subgroups=5)
        # Assert that the object is created without any exceptions
        self.assertIsNotNone(obj)
    
    def test_IDSD_init_method3(self):
        # Test with invalid parameters
        with self.assertRaises(TypeError):
            # Invalid type for num_subgroups
            IDSD(num_subgroups='5')
        
        with self.assertRaises(TypeError):
            # Invalid type for cats
            IDSD(num_subgroups=5, cats='3')
        
        with self.assertRaises(TypeError):
            # Invalid type for max_complexity
            IDSD(num_subgroups=5, max_complexity='10')
        
        with self.assertRaises(TypeError):
            # Invalid type for coverage_thld
            IDSD(num_subgroups=5, coverage_thld='0.5')
        
        with self.assertRaises(TypeError):
            # Invalid type for or_thld
            IDSD(num_subgroups=5, or_thld='1.0')
        
        with self.assertRaises(TypeError):
            # Invalid type for p_val_thld
            IDSD(num_subgroups=5, p_val_thld='0.1')
        
        with self.assertRaises(TypeError):
            # Invalid type for abs_contribution_thld
            IDSD(num_subgroups=5, abs_contribution_thld='0.3')
        
        with self.assertRaises(TypeError):
            # Invalid type for contribution_thld
            IDSD(num_subgroups=5, contribution_thld='4')

        with self.assertRaises(TypeError):
            # Invalid type for write_results_in_file
            IDSD(num_subgroups=5, write_results_in_file='True')
        
        with self.assertRaises(ValueError):
            # 'write_results_in_file' is True but 'file_path' is None
            IDSD(num_subgroups=5, write_results_in_file=True)
        
        with self.assertRaises(TypeError):
            # Invalid type for file_path
            IDSD(num_subgroups=5, file_path=5)
        
        with self.assertRaises(ValueError):
            # num_subgroups is negative
            IDSD(num_subgroups=-5)
        
        with self.assertRaises(ValueError):
            # num_subgroups is zero
            IDSD(num_subgroups=0)
        
        with self.assertRaises(ValueError):
            # cats is less tan -1
            IDSD(num_subgroups=5, cats=-3)
        
        with self.assertRaises(ValueError):
            # cats is zero
            IDSD(num_subgroups=5, cats=0)
        
        with self.assertRaises(ValueError):
            # coverage_thld is not in the range [0, 1]
            IDSD(num_subgroups=5, coverage_thld=1.5)

        with self.assertRaises(ValueError):
            # or_thld is negative
            IDSD(num_subgroups=5, or_thld=-1.0)
        
        with self.assertRaises(ValueError):
            # p_val_thld is not in the range [0, 1]
            IDSD(num_subgroups=5, p_val_thld=1.5)
        
        with self.assertRaises(ValueError):
            # abs_contribution_thld is not greater than 0
            IDSD(num_subgroups=5, abs_contribution_thld=-1)
        
        with self.assertRaises(ValueError):
            # contribution_thld is negative
            IDSD(num_subgroups=5, contribution_thld=-4)
        
        with self.assertRaises(TypeError):
            # not all the required parameters are provided
            IDSD()

    def test_IDSD_reduce_categories(self):
        # Check that the 'other' value is added to the reduced dataframe
        obj = IDSD(num_subgroups=1, cats = 2)
        df = DataFrame({'a': ["1", "2", "1", "1", "3"], 'b': ["1", "2", "1", "1", "2"], 'c':["other", "2", "other", "other", "3"], 'class': ["1", "1", "0", "0", "1"]})
        target = ("class", "1")
        reduced_df = obj._reduce_categories(df, target)
        self.assertIn('other', reduced_df['a'].unique())
        self.assertNotIn("other", reduced_df['b'].unique())
        self.assertIn("other_", reduced_df['c'].unique())
    
    def test_IDSD_generate_selectors(self):
        # Check that the method returns the correct selectors
        obj = IDSD(num_subgroups=1, cats = 2)
        df = DataFrame({'a': ["1", "2", "1", "1", "3"], 'b': ["1", "2", "1", "1", "2"], 'c':["other", "2", "other", "other", "3"], 'class': ["1", "1", "0", "0", "1"]})
        target = ("class", "1")
        reduced_df = obj._reduce_categories(df, target)
        selectors = obj._generate_selectors(reduced_df, target)
        self.assertIn(Selector("a", Operator.EQUAL, "1"), selectors)
        self.assertIn(Selector("a", Operator.EQUAL, "other"), selectors)
        self.assertIn(Selector("b", Operator.EQUAL, "1"), selectors)
        self.assertIn(Selector("b", Operator.EQUAL, "2"), selectors)
        self.assertIn(Selector("c", Operator.EQUAL, "other"), selectors)
        self.assertIn(Selector("c", Operator.EQUAL, "other_"), selectors)

    def test_IDSD_compute_rank(self):
        model = IDSD(num_subgroups=1)
        self.assertEqual(model._compute_rank([1,0,1,1,1]), 1)
        self.assertEqual(model._compute_rank([0,1,1,1,1]), 0)
        self.assertEqual(model._compute_rank([0,0,1,1,1]), 0)
        self.assertEqual(model._compute_rank([1,1,1,1,1]), 5)
        self.assertEqual(model._compute_rank([1,1,1,1,0]), 4)
    
    def test_IDSD_redundant(self):
        # Check that the method returns the correct redundancy
        model = IDSD(num_subgroups=1)
        p1 = Pattern([Selector("a", Operator.EQUAL, "1"), Selector("b", Operator.EQUAL, "1")])
        p2 = Pattern([Selector("a", Operator.EQUAL, "1"), Selector("c", Operator.EQUAL, "1")])
        p3 = Pattern([Selector("a", Operator.EQUAL, "1")])
        self.assertTrue(model._redundant(p1, p3))
        self.assertTrue(model._redundant(p3, p1))
        self.assertFalse(model._redundant(p1, p2))
        self.assertFalse(model._redundant(p2, p1))
        self.assertTrue(model._redundant(p2, p3))
        self.assertTrue(model._redundant(p3, p2))
    
    def test_IDSD_top_k_update1(self):
        # Check that the method updates the top-k list correctly
        model = IDSD(num_subgroups=3)
        model._top_k_subgroups = [(Pattern([Selector("a", Operator.EQUAL, "1")]), 3, 0.5), 
                        (Pattern([Selector("b", Operator.EQUAL, "1")]), 3, 0.3),
                        (Pattern([Selector("c", Operator.EQUAL, "1")]), 3, 0.2)]
        new_pattern = Pattern([Selector("a", Operator.EQUAL, "1"), Selector("b", Operator.EQUAL, "1")])
        new_pat_rank = 4
        new_pat_credibility_values = dict({"odds_ratio": 0.1})
        model._top_k_update(new_pattern, new_pat_credibility_values, new_pat_rank)
        self.assertEqual(len(model._top_k_subgroups), 2)
        
    def test_IDSD_top_k_update2(self):
        # Check that the method updates the top-k list correctly
        model = IDSD(num_subgroups=3)
        model._top_k_subgroups = [(Pattern([Selector("a", Operator.EQUAL, "1")]), 3, 0.5), 
                        (Pattern([Selector("b", Operator.EQUAL, "1")]), 3, 0.3),
                        (Pattern([Selector("c", Operator.EQUAL, "1")]), 3, 0.2)]
        new_pattern = Pattern([Selector("a", Operator.EQUAL, "1"),
                               Selector("b", Operator.EQUAL, "1"),
                               Selector("c", Operator.EQUAL, "1")])
        new_pat_rank = 4
        new_pat_credibility_values = dict({"odds_ratio": 0.1})
        model._top_k_update(new_pattern, new_pat_credibility_values, new_pat_rank)
        self.assertEqual(len(model._top_k_subgroups), 1)
        
    def test_IDSD_top_k_update3(self):
        # Check that the method updates the top-k list correctly
        model = IDSD(num_subgroups=3)
        model._top_k_subgroups = [(Pattern([Selector("a", Operator.EQUAL, "1")]), 5, 0.5), 
                        (Pattern([Selector("b", Operator.EQUAL, "1")]), 3, 0.3),
                        (Pattern([Selector("c", Operator.EQUAL, "1")]), 3, 0.2)]
        new_pattern = Pattern([Selector("a", Operator.EQUAL, "1"), Selector("b", Operator.EQUAL, "1")])
        new_pat_rank = 4
        new_pat_credibility_values = dict({"odds_ratio": 0.1})
        # Only b = 1 should be removed
        model._top_k_update(new_pattern, new_pat_credibility_values, new_pat_rank)
        self.assertEqual(len(model._top_k_subgroups), 3)

    def test_IDSD_fit(self):
        df = DataFrame({'bread': {0: 'yes', 1: 'yes', 2: 'no', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'milk': {0: 'yes', 1: 'no', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'beer': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'no', 5: 'yes', 6: 'no'}, 'coke': {0: 'no', 1: 'no', 2: 'yes', 3: 'no', 4: 'yes', 5: 'no', 6: 'yes'}, 'diaper': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}})        
        target = ("diaper", "yes")
        model = IDSD(num_subgroups=5, write_results_in_file=True, file_path='results.txt')
        model.fit(df, target)
        # Description: [bread = 'no'], Target: diaper = 'yes' ; Rank : 2 ; coverage : 0.14285714285714285 ; odds_ratio : inf ; p_value : 0.6830913983096085 ; absolute_contribution : 1 ; contribution_ratio : 1.0 ; 
        # Description: [milk = 'no'], Target: diaper = 'yes' ; Rank : 2 ; coverage : 0.14285714285714285 ; odds_ratio : inf ; p_value : 0.6830913983096085 ; absolute_contribution : 1 ; contribution_ratio : 1.0 ; 
        # Description: [beer = 'yes'], Target: diaper = 'yes' ; Rank : 2 ; coverage : 0.5714285714285714 ; odds_ratio : inf ; p_value : 0.4142161782425249 ; absolute_contribution : 1 ; contribution_ratio : 1.0 ; 
        # Description: [coke = 'yes'], Target: diaper = 'yes' ; Rank : 2 ; coverage : 0.42857142857142855 ; odds_ratio : inf ; p_value : 0.4795001221869537 ; absolute_contribution : 1 ; contribution_ratio : 1.0 ; 
        # Description: [bread = 'yes', milk = 'no'], Target: diaper = 'yes' ; Rank : 2 ; coverage : 0.14285714285714285 ; odds_ratio : inf ; p_value : 0.6830913983096085 ; absolute_contribution : 1 ; contribution_ratio : inf ; 
        file_to_parse = open("./results.txt", "r")
        list_of_writte_results = []
        for line in file_to_parse:
            list_of_writte_results.append(line)
        list_of_subgroups= [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_writte_results]
        self.assertEqual(len(list_of_subgroups), 5)
        self.assertIn(Subgroup.generate_from_str("Description: [bread = 'no'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [milk = 'no'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [coke = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [bread = 'yes', milk = 'no'], Target: diaper = 'yes'"), list_of_subgroups)
        file_to_parse.close()
        remove("./results.txt")


    