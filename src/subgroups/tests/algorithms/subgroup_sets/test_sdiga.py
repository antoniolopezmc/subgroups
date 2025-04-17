# -*- coding: utf-8 -*-

# Contributors:
#    Iván García Alcaraz <igalcaraz19@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/subgroup_sets/sdiga.py'.
"""
import unittest
from pandas import DataFrame
from subgroups.algorithms.subgroup_sets.sdiga import SDIGA
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.core.subgroup import Subgroup
from subgroups.core.pattern import Pattern



class TestSDIGA(unittest.TestCase):

    def test_SDIGA_init_method(self):
        # Test valid initialization
        sdiga = SDIGA(max_generation=10, population_size=20, crossover_prob=0.6, mutation_prob=0.01, 
                      support_weight=0.4, confidence_weight=0.3, min_confidence=0.5)
        self.assertEqual(sdiga.max_generation, 10)
        self.assertEqual(sdiga.population_size, 20)
        self.assertEqual(sdiga.crossover_prob, 0.6)
        self.assertEqual(sdiga.mutation_prob, 0.01)
        self.assertEqual(sdiga.support_weight, 0.4)
        self.assertEqual(sdiga.confidence_weight, 0.3)
        self.assertEqual(sdiga.min_confidence, 0.5)

        # Test invalid parameters
        # Check for invalid types
        with self.assertRaises(TypeError):
            SDIGA(max_generation="10", population_size=20, crossover_prob=0.6, mutation_prob=0.01, 
                      support_weight=0.4, confidence_weight=0.3, min_confidence=0.5)
        # Check for invalid values
        with self.assertRaises(ValueError):
            # Invalid values for max_generation
            SDIGA(max_generation=0, population_size=20, crossover_prob=0.6, mutation_prob=0.01, 
                      support_weight=0.4, confidence_weight=0.3, min_confidence=0.5)
        with self.assertRaises(ValueError):
            # Invalid values for population_size
            SDIGA(max_generation=10, population_size=0, crossover_prob=0.6, mutation_prob=0.01, 
                      support_weight=0.4, confidence_weight=0.3, min_confidence=0.5)
        with self.assertRaises(ValueError):
            # Invalid values for crossover_prob
            SDIGA(max_generation=10, population_size=20, crossover_prob=1.5, mutation_prob=0.1, 
                  support_weight=1, confidence_weight=1, min_confidence=0.5)
        with self.assertRaises(ValueError):
            # Invalid values for mutation_prob
            SDIGA(max_generation=10, population_size=20, crossover_prob=0.8, mutation_prob=-0.1, 
                  support_weight=1, confidence_weight=1, min_confidence=0.5)
    
    def test_SDIGA_init_method2(self):

        # Test invalid write_results_in_file or file_path parameter
        with self.assertRaises(TypeError):
            # Invalid type for file_path when write_results_in_file is True
            SDIGA(max_generation=10, population_size=20, crossover_prob=0.6, mutation_prob=0.01, 
                  support_weight=0.4, confidence_weight=0.3, min_confidence=0.5, write_results_in_file=True, file_path=24)
        with self.assertRaises(TypeError):
            # Invalid type for file_path when write_results_in_file is True
            SDIGA(max_generation=10, population_size=20, crossover_prob=0.6, mutation_prob=0.01, 
                  support_weight=0.4, confidence_weight=0.3, min_confidence=0.5, write_results_in_file=True, file_path=None)
        with self.assertRaises(TypeError):
            # Invalid type for file_path when write_results_in_file is False
            SDIGA(max_generation=10, population_size=20, crossover_prob=0.6, mutation_prob=0.01, 
                  support_weight=0.4, confidence_weight=0.3, min_confidence=0.5, write_results_in_file=False, file_path=24)


    def test_SDIGA_fit_method(self):
        # Test with valid dataset 
        df = DataFrame({"a1": ["a", "b", "c", "c"], "a2": ["q", "q", "s", "q"], 
                        "class": ["n", "y", "n", "y"]})
        target = ("class", "y")
        sdiga = SDIGA(max_generation=10, population_size=5, crossover_prob=0.8, mutation_prob=0.1, 
                      support_weight=1, confidence_weight=1, min_confidence=0.5)
        sdiga.fit(df, target)
        self.assertEqual(sdiga.TP, 2)
        self.assertEqual(sdiga.FP, 2)
        self.assertGreater(sdiga.selected_subgroups, 0)

        # Test with invalid dataset
        df_invalid = DataFrame({"a1": [1, 2, 3, 4], "class": [0, 1, 0, 1]})
        with self.assertRaises(DatasetAttributeTypeError):
            sdiga.fit(df_invalid, target)

    #TODO: Ask for filter rows and columns with cromosome

if __name__ == "__main__":
    unittest.main()