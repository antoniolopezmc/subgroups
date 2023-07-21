# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/qfinder.py'.
"""

from os import remove
from bitarray import bitarray
from pandas import DataFrame
from subgroups.algorithms.subgroup_sets.qfinder import QFinder
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
import unittest

class TestQFinder(unittest.TestCase):
    
    def test_QFinder_init_method1(self):
        # Test with valid parameters
        obj = QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                           or_thld=1.0, p_val_thld=0.1, abs_contribution_thld=0.3,
                           contribution_thld=4, delta=0.1, write_results_in_file=True,
                           file_path='results.txt', write_stats_in_file=True,
                           stats_path='stats.txt')
        
        # Assert that the object is created without any exceptions
        self.assertIsNotNone(obj)
        
    def test_QFinder_init_method2(self):
        # Test with invalid parameters
        with self.assertRaises(TypeError):
            # Invalid type for num_subgroups
            QFinder(num_subgroups='5')
            
        with self.assertRaises(TypeError):
            # Invalid type for cats
            QFinder(num_subgroups=5, cats='3')
            
        with self.assertRaises(TypeError):
            # Invalid type for max_complexity
            QFinder(num_subgroups=5, cats=3, max_complexity='10')

        with self.assertRaises(TypeError):
            # Invalid type for coverage_thld
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld='0.5')
            
        with self.assertRaises(TypeError):
            # Invalid type for or_thld
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                        or_thld='1.0')
                        
        with self.assertRaises(TypeError):
            # Invalid type for p_val_thld
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                        or_thld=1.0, p_val_thld='0.1')
                        
        with self.assertRaises(TypeError):
            # Invalid type for abs_contribution_thld
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                        or_thld=1.0, p_val_thld=0.1, abs_contribution_thld='0.3')
                        
        with self.assertRaises(TypeError):
            # Invalid type for contribution_thld
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                        or_thld=1.0, p_val_thld=0.1, abs_contribution_thld=0.3,
                        contribution_thld='4')
                        
        with self.assertRaises(TypeError):
            # Invalid type for delta
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                        or_thld=1.0, p_val_thld=0.1, abs_contribution_thld=0.3,
                        contribution_thld=4, delta='0.2')
        
        with self.assertRaises(ValueError):
            # write_results_in_file is True but file_path is None
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                          or_thld=1.0, p_val_thld=0.1, abs_contribution_thld=0.3,
                          contribution_thld=4, delta=0.1, write_results_in_file=True)
        
        with self.assertRaises(ValueError):
            # write_stats_in_file is True but stats_path is None
            QFinder(num_subgroups=5, cats=3, max_complexity=10, coverage_thld=0.5,
                          or_thld=1.0, p_val_thld=0.1, abs_contribution_thld=0.3,
                          contribution_thld=4, delta=0.1, write_stats_in_file=True)
                          
    def test_QFinder_generate_candidate_patterns1(self):
        df = DataFrame({'bread': {0: 'yes', 1: 'yes', 2: 'no', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'milk': {0: 'yes', 1: 'no', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'beer': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'no', 5: 'yes', 6: 'no'}, 'coke': {0: 'no', 1: 'no', 2: 'yes', 3: 'no', 4: 'yes', 5: 'no', 6: 'yes'}, 'diaper': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}})        
        target = ("diaper", "yes")
        model = QFinder(num_subgroups=5)
        complexity = 3
        patterns = model._generate_candidate_patterns(df,target, complexity)
        simple_selectors = [
            Selector("bread", Operator.EQUAL, "yes"),
            Selector("milk", Operator.EQUAL, "yes"),
            Selector("beer", Operator.EQUAL, "yes"),
            Selector("coke", Operator.EQUAL, "yes"),
            Selector("bread", Operator.EQUAL, "no"),
            Selector("milk", Operator.EQUAL, "no"),
            Selector("beer", Operator.EQUAL, "no"),
            Selector("coke", Operator.EQUAL, "no"),
        ]
        simple_patterns = [Pattern([sel]) for sel in simple_selectors]
        for pat in simple_patterns:
            self.assertIn(pat, patterns)
        test_complex_patterns = [
            Pattern([Selector("bread", Operator.EQUAL,  "yes"), Selector("milk", Operator.EQUAL,  "yes")]),
            Pattern([Selector("bread", Operator.EQUAL,  "yes"), Selector("beer", Operator.EQUAL,  "yes")]),
            Pattern([Selector("bread", Operator.EQUAL,  "yes"), Selector("coke", Operator.EQUAL,  "yes")]),
            Pattern([Selector("milk", Operator.EQUAL,  "yes"), Selector("beer", Operator.EQUAL,  "yes")]),
            Pattern([Selector("milk", Operator.EQUAL,  "yes"), Selector("coke", Operator.EQUAL,  "yes")]),
            Pattern([Selector("beer", Operator.EQUAL,  "yes"), Selector("coke", Operator.EQUAL,  "no")]),
            Pattern([Selector("bread", Operator.EQUAL,  "no"), Selector("milk", Operator.EQUAL,  "no")]),
        ]
        for pat in test_complex_patterns:
            self.assertIn(pat, patterns)
        
    def test_QFinder_generate_candidate_patterns2(self):
        # Check that the value 'other' is added to the categorical variables
        df = DataFrame({'a': {0: '1', 1: '1', 2: '1', 3: '2', 4: '3'}, 'class': {0: '1', 1: '1', 2: '1', 3: '1', 4: '1'}})
        target = ("class", 1)
        model = QFinder(num_subgroups=5)
        complexity = 1
        patterns = model._generate_candidate_patterns(df,target, complexity,cats=2)
        simple_selectors = [
            Selector("a", Operator.EQUAL, '1'),
            Selector("a", Operator.EQUAL, "other"),
        ]
        simple_patterns = [Pattern([sel]) for sel in simple_selectors]
        for pat in simple_patterns:
            self.assertIn(pat, patterns)
    
    def test_QFinder_handle_individual_result(self):
        model = QFinder(num_subgroups=5)
        result = model._handle_individual_result(bitarray('11111'))
        self.assertEqual(result, 5)

        result = model._handle_individual_result(bitarray('00000'))
        self.assertEqual(result, 0)

        result = model._handle_individual_result(bitarray('10101'))
        self.assertEqual(result, 1)

        result = model._handle_individual_result(bitarray('01010'))
        self.assertEqual(result, 0)

        result = model._handle_individual_result(bitarray('11100'))
        self.assertEqual(result, 3)

        result = model._handle_individual_result(bitarray('11110'))
        self.assertEqual(result, 4)

        result = model._handle_individual_result(bitarray('11101'))
        self.assertEqual(result, 5)

    def test_QFinder_fit(self):
        df = DataFrame({'bread': {0: 'yes', 1: 'yes', 2: 'no', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'milk': {0: 'yes', 1: 'no', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'beer': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'no', 5: 'yes', 6: 'no'}, 'coke': {0: 'no', 1: 'no', 2: 'yes', 3: 'no', 4: 'yes', 5: 'no', 6: 'yes'}, 'diaper': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}})        
        target = ("diaper", "yes")
        model = QFinder(num_subgroups=5)
        model.fit(df, target)
        