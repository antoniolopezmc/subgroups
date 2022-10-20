# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/gmsl.py'.
"""

from pandas import DataFrame, read_csv
from subgroups.algorithms.subgroup_lists.nominal_target.gmsl import GMSL
from subgroups.core import Subgroup, Pattern, Selector, Operator
from subgroups.data_structures.subgroup_list import SubgroupList
from subgroups.utils.mdl import universal_code_for_integer, log2_multinomial_with_recurrence
from bitarray import bitarray
from math import comb
from numpy import log2
from os import remove
from subgroups.algorithms import VLSD
from subgroups.quality_measures import WRAcc, WRAccOptimisticEstimate1
from regex import compile
from subgroups.exceptions import DatasetAttributeTypeError
import unittest

class TestGMSL(unittest.TestCase):

    def test_GMSL_mdl_functions_1(self) -> None:
        df = DataFrame({"at1" : ["a", "a", "b"], "at2" : ["c", "d", "c"], "at3" : ["e", "e", "j"], "target" : ["no", "yes", "yes"]})
        target = ("target", "yes")
        dataset_target_positives = (df[target[0]] == target[1])
        dataset_target_negatives = ~dataset_target_positives
        bitarray_of_positives = bitarray(dataset_target_positives.to_list(), endian="big")
        bitarray_of_negatives = bitarray(dataset_target_negatives.to_list(), endian="big")
        self.assertEqual(bitarray_of_positives, bitarray("011", endian="big"))
        self.assertEqual(bitarray_of_negatives, bitarray("100", endian="big"))
        ###############
        ## EXAMPLE 1 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        candidate = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("010", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("100", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 2)
        expected_result = (-1*log2(1/3)-2*log2(2/3)) - (-0*log2(1/3)-1*log2(2/3)) - (-1*log2(1/2)-1*log2(1/2)+log2_multinomial_with_recurrence(2,2))
        self.assertEqual(result, expected_result)
        result_data_model_candidate_example_1 = result
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(0) - universal_code_for_integer(1) - universal_code_for_integer(1) - log2(comb(3, 1)) - log2(2)
        self.assertEqual(result, expected_result)
        result_model_candidate_example_1 = result
        # Check aliasing and subgroup list state.
        self.assertEqual(len(sl), 0)
        self.assertEqual(sl.default_rule_bitarray_of_positives, bitarray_of_positives)
        self.assertEqual(sl.default_rule_bitarray_of_negatives, bitarray_of_negatives)
        self.assertEqual(sl.default_rule_bitarray_of_positives, bitarray(dataset_target_positives.to_list(), endian="big"))
        self.assertEqual(sl.default_rule_bitarray_of_negatives, bitarray(dataset_target_negatives.to_list(), endian="big"))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_positives), id(bitarray_of_positives))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_negatives), id(bitarray_of_negatives))
        ###############
        ## EXAMPLE 2 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        candidate = Subgroup(Pattern([Selector("at2", Operator.EQUAL, "c")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("001", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("100", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 2)
        expected_result = (-1*log2(1/3)-2*log2(2/3)) - (-0*log2(1/3)-1*log2(2/3)) - (-1*log2(1/2)-1*log2(1/2)+log2_multinomial_with_recurrence(2,2))
        self.assertEqual(result, expected_result)
        self.assertEqual(result, result_data_model_candidate_example_1)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(0) - universal_code_for_integer(1) - universal_code_for_integer(1) - log2(comb(3, 1)) - log2(2)
        self.assertEqual(result, expected_result)
        self.assertEqual(result, result_model_candidate_example_1)
        # Check aliasing and subgroup list state.
        self.assertEqual(len(sl), 0)
        self.assertEqual(sl.default_rule_bitarray_of_positives, bitarray_of_positives)
        self.assertEqual(sl.default_rule_bitarray_of_negatives, bitarray_of_negatives)
        self.assertEqual(sl.default_rule_bitarray_of_positives, bitarray(dataset_target_positives.to_list(), endian="big"))
        self.assertEqual(sl.default_rule_bitarray_of_negatives, bitarray(dataset_target_negatives.to_list(), endian="big"))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_positives), id(bitarray_of_positives))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_negatives), id(bitarray_of_negatives))
        ###############
        ## EXAMPLE 3 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        sl.add_subgroup( Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector(target[0], Operator.EQUAL, target[1])), bitarray("010", endian="big"), bitarray("100", endian="big") )
        candidate = Subgroup(Pattern([Selector("at2", Operator.EQUAL, "c")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("001", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("100", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Default rule after adding the subgroup.
        defrule_bitarray_of_positives_after_adding = sl.default_rule_bitarray_of_positives
        defrule_bitarray_of_negatives_after_adding = sl.default_rule_bitarray_of_negatives
        defrule_bitarray_of_positives_after_adding_copy = sl.default_rule_bitarray_of_positives.copy()
        defrule_bitarray_of_negatives_after_adding_copy = sl.default_rule_bitarray_of_negatives.copy()
        # First subgroup after adding the subgroup.
        s1_subgroup = sl.get_subgroup(0)
        s1_bitarray_of_positives = sl.get_subgroup_bitarray_of_positives(0)
        s1_bitarray_of_negatives = sl.get_subgroup_bitarray_of_negatives(0)
        s1_subgroup_copy = sl.get_subgroup(0).copy()
        s1_bitarray_of_positives_copy = sl.get_subgroup_bitarray_of_positives(0).copy()
        s1_bitarray_of_negatives_copy = sl.get_subgroup_bitarray_of_negatives(0).copy()
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 1)
        #expected_result = (-0*log2(1/3)-1*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-0*log2(0/1)-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        expected_result = (-0*log2(1/3)-1*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        self.assertEqual(result, expected_result)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(1) - universal_code_for_integer(2) - universal_code_for_integer(1) - log2(comb(3, 1)) - log2(2)
        self.assertEqual(result, expected_result)
        # Check aliasing and subgroup list state.
        self.assertEqual(len(sl), 1)
        self.assertNotEqual(id(sl.default_rule_bitarray_of_positives), id(bitarray_of_positives))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_negatives), id(bitarray_of_negatives))
        self.assertEqual(sl.default_rule_bitarray_of_positives, defrule_bitarray_of_positives_after_adding)
        self.assertEqual(sl.default_rule_bitarray_of_positives, defrule_bitarray_of_positives_after_adding_copy)
        self.assertEqual(sl.default_rule_bitarray_of_negatives, defrule_bitarray_of_negatives_after_adding)
        self.assertEqual(sl.default_rule_bitarray_of_negatives, defrule_bitarray_of_negatives_after_adding_copy)
        self.assertEqual(id(sl.default_rule_bitarray_of_positives), id(defrule_bitarray_of_positives_after_adding))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_positives), id(defrule_bitarray_of_positives_after_adding_copy))
        self.assertEqual(id(sl.default_rule_bitarray_of_negatives), id(defrule_bitarray_of_negatives_after_adding))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_negatives), id(defrule_bitarray_of_negatives_after_adding_copy))
        self.assertEqual(sl.get_subgroup(0), s1_subgroup)
        self.assertEqual(id(sl.get_subgroup(0)), id(s1_subgroup))
        self.assertEqual(s1_bitarray_of_positives, sl.get_subgroup_bitarray_of_positives(0))
        self.assertEqual(s1_bitarray_of_negatives, sl.get_subgroup_bitarray_of_negatives(0))
        self.assertEqual(id(s1_bitarray_of_positives), id(sl.get_subgroup_bitarray_of_positives(0)))
        self.assertEqual(id(s1_bitarray_of_negatives), id(sl.get_subgroup_bitarray_of_negatives(0)))
        self.assertEqual(sl.get_subgroup(0), s1_subgroup_copy)
        self.assertNotEqual(id(sl.get_subgroup(0)), id(s1_subgroup_copy))
        self.assertEqual(s1_bitarray_of_positives_copy, sl.get_subgroup_bitarray_of_positives(0))
        self.assertEqual(s1_bitarray_of_negatives_copy, sl.get_subgroup_bitarray_of_negatives(0))
        self.assertNotEqual(id(s1_bitarray_of_positives_copy), id(sl.get_subgroup_bitarray_of_positives(0)))
        self.assertNotEqual(id(s1_bitarray_of_negatives_copy), id(sl.get_subgroup_bitarray_of_negatives(0)))
        ###############
        ## EXAMPLE 4 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        sl.add_subgroup( Subgroup(Pattern([Selector("at3", Operator.EQUAL, "j")]), Selector(target[0], Operator.EQUAL, target[1])), bitarray("001", endian="big"), bitarray("000", endian="big") )
        sl.add_subgroup( Subgroup(Pattern([Selector("at2", Operator.EQUAL, "d")]), Selector(target[0], Operator.EQUAL, target[1])), bitarray("010", endian="big"), bitarray("000", endian="big") )
        candidate = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("010", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("100", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Default rule after adding the subgroups.
        defrule_bitarray_of_positives_after_adding = sl.default_rule_bitarray_of_positives
        defrule_bitarray_of_negatives_after_adding = sl.default_rule_bitarray_of_negatives
        defrule_bitarray_of_positives_after_adding_copy = sl.default_rule_bitarray_of_positives.copy()
        defrule_bitarray_of_negatives_after_adding_copy = sl.default_rule_bitarray_of_negatives.copy()
        # First and second subgroups after adding the subgroups.
        s1_subgroup = sl.get_subgroup(0)
        s1_bitarray_of_positives = sl.get_subgroup_bitarray_of_positives(0)
        s1_bitarray_of_negatives = sl.get_subgroup_bitarray_of_negatives(0)
        s2_subgroup = sl.get_subgroup(1)
        s2_bitarray_of_positives = sl.get_subgroup_bitarray_of_positives(1)
        s2_bitarray_of_negatives = sl.get_subgroup_bitarray_of_negatives(1)
        s1_subgroup_copy = sl.get_subgroup(0).copy()
        s1_bitarray_of_positives_copy = sl.get_subgroup_bitarray_of_positives(0).copy()
        s1_bitarray_of_negatives_copy = sl.get_subgroup_bitarray_of_negatives(0).copy()
        s2_subgroup_copy = sl.get_subgroup(1).copy()
        s2_bitarray_of_positives_copy = sl.get_subgroup_bitarray_of_positives(1).copy()
        s2_bitarray_of_negatives_copy = sl.get_subgroup_bitarray_of_negatives(1).copy()
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 1)
        #expected_result = (-1*log2(1/3)-0*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-1*log2(1/1)-0*log2(0/1)+log2_multinomial_with_recurrence(2,1))
        expected_result = (-1*log2(1/3)-0*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        self.assertEqual(result, expected_result)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(2) - universal_code_for_integer(3) - universal_code_for_integer(1) - log2(comb(3, 1)) - log2(2)
        self.assertEqual(result, expected_result)
        # Check aliasing and subgroup list state.
        self.assertEqual(len(sl), 2)
        self.assertNotEqual(id(sl.default_rule_bitarray_of_positives), id(bitarray_of_positives))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_negatives), id(bitarray_of_negatives))
        self.assertEqual(sl.default_rule_bitarray_of_positives, defrule_bitarray_of_positives_after_adding)
        self.assertEqual(sl.default_rule_bitarray_of_positives, defrule_bitarray_of_positives_after_adding_copy)
        self.assertEqual(sl.default_rule_bitarray_of_negatives, defrule_bitarray_of_negatives_after_adding)
        self.assertEqual(sl.default_rule_bitarray_of_negatives, defrule_bitarray_of_negatives_after_adding_copy)
        self.assertEqual(id(sl.default_rule_bitarray_of_positives), id(defrule_bitarray_of_positives_after_adding))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_positives), id(defrule_bitarray_of_positives_after_adding_copy))
        self.assertEqual(id(sl.default_rule_bitarray_of_negatives), id(defrule_bitarray_of_negatives_after_adding))
        self.assertNotEqual(id(sl.default_rule_bitarray_of_negatives), id(defrule_bitarray_of_negatives_after_adding_copy))
        self.assertEqual(sl.get_subgroup(0), s1_subgroup)
        self.assertEqual(id(sl.get_subgroup(0)), id(s1_subgroup))
        self.assertEqual(s1_bitarray_of_positives, sl.get_subgroup_bitarray_of_positives(0))
        self.assertEqual(s1_bitarray_of_negatives, sl.get_subgroup_bitarray_of_negatives(0))
        self.assertEqual(id(s1_bitarray_of_positives), id(sl.get_subgroup_bitarray_of_positives(0)))
        self.assertEqual(id(s1_bitarray_of_negatives), id(sl.get_subgroup_bitarray_of_negatives(0)))
        self.assertEqual(sl.get_subgroup(1), s2_subgroup)
        self.assertEqual(id(sl.get_subgroup(1)), id(s2_subgroup))
        self.assertEqual(s2_bitarray_of_positives, sl.get_subgroup_bitarray_of_positives(1))
        self.assertEqual(s2_bitarray_of_negatives, sl.get_subgroup_bitarray_of_negatives(1))
        self.assertEqual(id(s2_bitarray_of_positives), id(sl.get_subgroup_bitarray_of_positives(1)))
        self.assertEqual(id(s2_bitarray_of_negatives), id(sl.get_subgroup_bitarray_of_negatives(1)))
        self.assertEqual(sl.get_subgroup(0), s1_subgroup_copy)
        self.assertNotEqual(id(sl.get_subgroup(0)), id(s1_subgroup_copy))
        self.assertEqual(s1_bitarray_of_positives_copy, sl.get_subgroup_bitarray_of_positives(0))
        self.assertEqual(s1_bitarray_of_negatives_copy, sl.get_subgroup_bitarray_of_negatives(0))
        self.assertNotEqual(id(s1_bitarray_of_positives_copy), id(sl.get_subgroup_bitarray_of_positives(0)))
        self.assertNotEqual(id(s1_bitarray_of_negatives_copy), id(sl.get_subgroup_bitarray_of_negatives(0)))
        self.assertEqual(sl.get_subgroup(1), s2_subgroup_copy)
        self.assertNotEqual(id(sl.get_subgroup(1)), id(s2_subgroup_copy))
        self.assertEqual(s2_bitarray_of_positives_copy, sl.get_subgroup_bitarray_of_positives(1))
        self.assertEqual(s2_bitarray_of_negatives_copy, sl.get_subgroup_bitarray_of_negatives(1))
        self.assertNotEqual(id(s2_bitarray_of_positives_copy), id(sl.get_subgroup_bitarray_of_positives(1)))
        self.assertNotEqual(id(s2_bitarray_of_negatives_copy), id(sl.get_subgroup_bitarray_of_negatives(1)))
        ###############
        ## EXAMPLE 5 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        sl.add_subgroup( Subgroup(Pattern([Selector("at2", Operator.EQUAL, "d")]), Selector(target[0], Operator.EQUAL, target[1])), bitarray("010", endian="big"), bitarray("000", endian="big") )
        sl.add_subgroup( Subgroup(Pattern([Selector("at3", Operator.EQUAL, "j")]), Selector(target[0], Operator.EQUAL, target[1])), bitarray("001", endian="big"), bitarray("000", endian="big") )
        candidate = Subgroup(Pattern([Selector("at2", Operator.EQUAL, "c")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("001", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("100", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 1)
        #expected_result = (-1*log2(1/3)-0*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-1*log2(1/1)-0*log2(0/1)+log2_multinomial_with_recurrence(2,1))
        expected_result = (-1*log2(1/3)-0*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        self.assertEqual(result, expected_result)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(2) - universal_code_for_integer(3) - universal_code_for_integer(1) - log2(comb(3, 1)) - log2(2)
        self.assertEqual(result, expected_result)
        ###############
        ## EXAMPLE 6 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        candidate = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a"), Selector("at2", Operator.EQUAL, "c")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("000", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("100", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 1)
        #expected_result = (-1*log2(1/3)-2*log2(2/3)) - (-0*log2(1/3)-2*log2(2/3)) - (-1*log2(1/1)-0*log2(0/1)+log2_multinomial_with_recurrence(2,1))
        expected_result = (-1*log2(1/3)-2*log2(2/3)) - (-0*log2(1/3)-2*log2(2/3)) - (-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        self.assertEqual(result, expected_result)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(0) - universal_code_for_integer(1) - universal_code_for_integer(2) - log2(comb(3, 2)) - log2(2) - log2(2)
        self.assertEqual(result, expected_result)
        ###############
        ## EXAMPLE 7 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        candidate = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "b"), Selector("at2", Operator.EQUAL, "c")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("001", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("000", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 1)
        #expected_result = (-1*log2(1/3)-2*log2(2/3)) - (-1*log2(1/3)-1*log2(2/3)) - (-0*log2(0/1)-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        expected_result = (-1*log2(1/3)-2*log2(2/3)) - (-1*log2(1/3)-1*log2(2/3)) - (-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        self.assertEqual(result, expected_result)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(0) - universal_code_for_integer(1) - universal_code_for_integer(2) - log2(comb(3, 2)) - log2(2) - log2(2)
        self.assertEqual(result, expected_result)
        ###############
        ## EXAMPLE 8 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        sl.add_subgroup( Subgroup(Pattern([Selector("at3", Operator.EQUAL, "e")]), Selector(target[0], Operator.EQUAL, target[1])), bitarray("010", endian="big"), bitarray("100", endian="big") )
        candidate = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "b"), Selector("at2", Operator.EQUAL, "c")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("001", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("000", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 1)
        #expected_result = (-0*log2(1/3)-1*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-0*log2(0/1)-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        expected_result = (-0*log2(1/3)-1*log2(2/3)) - (-0*log2(1/3)-0*log2(2/3)) - (-1*log2(1/1)+log2_multinomial_with_recurrence(2,1))
        self.assertEqual(result, expected_result)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(1) - universal_code_for_integer(2) - universal_code_for_integer(2) - log2(comb(3, 2)) - log2(2) - log2(2)
        self.assertEqual(result, expected_result)
    
    def test_GMSL_mdl_functions_2(self) -> None:
        df = DataFrame({"at1" : ["a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a",\
                                 "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a",\
                                 "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b", "b"],\
                        "at2" : ["c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c",\
                                 "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d", "d",\
                                 "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c"],\
                        "at3" : ["e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e",\
                                 "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e",\
                                 "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j", "j"],\
                        "target" : ["n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n", "n",\
                                    "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y",\
                                    "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y", "y"]})
        target = ("target", "y")
        dataset_target_positives = (df[target[0]] == target[1])
        dataset_target_negatives = ~dataset_target_positives
        bitarray_of_positives = bitarray(dataset_target_positives.to_list(), endian="big")
        bitarray_of_negatives = bitarray(dataset_target_negatives.to_list(), endian="big")
        self.assertEqual(bitarray_of_positives, bitarray("000000000000000000000000000000000011111111111111111111111111111111111111111111111111111111111111111111", endian="big"))
        self.assertEqual(bitarray_of_negatives, bitarray("111111111111111111111111111111111100000000000000000000000000000000000000000000000000000000000000000000", endian="big"))
        ###############
        ## EXAMPLE 1 ##
        ###############
        sl = SubgroupList(bitarray_of_positives, bitarray_of_negatives, len(df))
        candidate = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector(target[0], Operator.EQUAL, target[1]))
        candidate_bitarray_of_positives = bitarray("000000000000000000000000000000000011111111111111111111111111111111110000000000000000000000000000000000", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        candidate_bitarray_of_negatives = bitarray("111111111111111111111111111111111100000000000000000000000000000000000000000000000000000000000000000000", endian="big") # IMPORTANT: this bitarray must consider THE COMPLETE dataset.
        # Data, model, candidate.
        result, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(df, sl, candidate, candidate_bitarray_of_positives, candidate_bitarray_of_negatives)
        self.assertEqual(candidate_number_of_rows, 68)
        expected_result = (-34*log2(34/102)-68*log2(68/102)) - (-0*log2(34/102)-34*log2(68/102)) - (-34*log2(34/68)-34*log2(34/68)+log2_multinomial_with_recurrence(2,68))
        self.assertEqual(result, expected_result)
        self.assertGreater(result, 0)
        # Model, candidate.
        result = GMSL._compute_delta_model_candidate(df, sl, candidate)
        expected_result = universal_code_for_integer(0) - universal_code_for_integer(1) - universal_code_for_integer(1) - log2(comb(3, 1)) - log2(2)
        self.assertEqual(result, expected_result)
        self.assertLess(result, 0)
    
    def test_GMSL_mdl_functions_3(self) -> None:
        # Dataset.
        dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data"
        df = read_csv(dataset_url, names=["buying", "maint", "doors", "persons", "lug_boot", "safety"])
        df.reset_index(drop=True, inplace=True)
        target = ("safety", "unacc")
        # Subgroup list.
        mask = (df[target[0]] == target[1])
        sl = SubgroupList(bitarray(mask.tolist(), endian = "big"), bitarray((~mask).tolist(), endian = "big"), len(df))
        # Add s1 to the empty subgroup list.
        s1 = Subgroup(Pattern([Selector("doors", Operator.EQUAL, "2")]), Selector("safety", Operator.EQUAL, "unacc"))
        bitarray_of_positives = bitarray("111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000111111111000000000000000000", endian = "big")
        bitarray_of_negatives = bitarray("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", endian = "big")
        first_value, instances = GMSL._compute_delta_data_model_candidate(df, sl, s1, bitarray_of_positives, bitarray_of_negatives)
        second_value = GMSL._compute_delta_model_candidate(df, sl, s1)
        self.assertEqual(first_value, 291.1768556462128)
        self.assertEqual(second_value, -6.944025328338215)
        self.assertEqual(instances, 576)
        sl.add_subgroup(s1, bitarray_of_positives, bitarray_of_negatives)
        # Candidate s2 with only s1 in the list.
        s2 = Subgroup(Pattern([Selector("lug_boot", Operator.EQUAL, "high")]), Selector("safety", Operator.EQUAL, "unacc"))
        bitarray_of_positives = bitarray("001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000", endian = "big")
        bitarray_of_negatives = bitarray("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001", endian = "big")
        first_value, instances = GMSL._compute_delta_data_model_candidate(df, sl, s2, bitarray_of_positives, bitarray_of_negatives)
        second_value = GMSL._compute_delta_model_candidate(df, sl, s2)
        self.assertEqual(first_value, 265.8758204686112)
        self.assertEqual(second_value, -6.4254579619733665)
        self.assertEqual(instances, 384)
        # Candidate s3 with only s1 in the list.
        s3 = Subgroup(Pattern([Selector("lug_boot", Operator.EQUAL, "low")]), Selector("safety", Operator.EQUAL, "unacc"))
        bitarray_of_positives = bitarray("100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100", endian = "big")
        bitarray_of_negatives = bitarray("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", endian = "big")
        first_value, instances = GMSL._compute_delta_data_model_candidate(df, sl, s3, bitarray_of_positives, bitarray_of_negatives)
        second_value = GMSL._compute_delta_model_candidate(df, sl, s3)
        self.assertEqual(first_value, 192.75576029045158)
        self.assertEqual(second_value, -6.4254579619733665)
        self.assertEqual(instances, 384)
        # Add s2 to the list with s1.
        s2 = Subgroup(Pattern([Selector("lug_boot", Operator.EQUAL, "high")]), Selector("safety", Operator.EQUAL, "unacc"))
        bitarray_of_positives = bitarray("001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000001001001000000000001000000001001001000000000000000000001001001000000000000000000001001001000000000000000000", endian = "big")
        bitarray_of_negatives = bitarray("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001000000000001001001000001001000000000001001001001001001000000000001001001001001001000000000001001001001001001", endian = "big")
        first_value, instances = GMSL._compute_delta_data_model_candidate(df, sl, s2, bitarray_of_positives, bitarray_of_negatives)
        second_value = GMSL._compute_delta_model_candidate(df, sl, s2)
        self.assertEqual(first_value, 265.8758204686112)
        self.assertEqual(second_value, -6.4254579619733665)
        self.assertEqual(instances, 384)
        sl.add_subgroup(s2, bitarray_of_positives, bitarray_of_negatives)
        # Add s3 to the list with s1 and s2.
        s3 = Subgroup(Pattern([Selector("lug_boot", Operator.EQUAL, "low")]), Selector("safety", Operator.EQUAL, "unacc"))
        bitarray_of_positives = bitarray("100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100", endian = "big")
        bitarray_of_negatives = bitarray("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", endian = "big")
        first_value, instances = GMSL._compute_delta_data_model_candidate(df, sl, s3, bitarray_of_positives, bitarray_of_negatives)
        second_value = GMSL._compute_delta_model_candidate(df, sl, s3)
        self.assertEqual(first_value, 192.7557602904514)
        self.assertEqual(second_value, -6.674869170148412)
        self.assertEqual(instances, 384)
        sl.add_subgroup(s3, bitarray_of_positives, bitarray_of_negatives)
        # len(sl) equal to 3.
        self.assertEqual(len(sl), 3)
    
    def test_GMSL_load_candidates_method_1(self) -> None:
        number_of_dataset_instances = 5 # Number of instances of the original dataset (i.e., from which the subgroups were extracted).
        number_of_subgroups = 11 # Number of subgroups from the input file.
        input_file_path = "./tmp_input.txt"
        input_file_content = "Description: [a = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [a = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [a = 'r'], Target: target = 'y' ; 00010 ; 00000\nDescription: [a = 'w'], Target: target = 'y' ; 00000 ; 01000\nDescription: [b = 'g'], Target: target = 'y' ; 00010 ; 00000\nDescription: [b = 'q'], Target: target = 'y' ; 00000 ; 11001\nDescription: [b = 'v'], Target: target = 'y' ; 00100 ; 00000\nDescription: [c = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [c = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [c = 'r'], Target: target = 'y' ; 00010 ; 00000\nDescription: [c = 'w'], Target: target = 'y' ; 00000 ; 01000"
        input_file = open(input_file_path, "w")
        input_file.write(input_file_content)
        input_file.close()
        output_file_path = "./tmp_output.txt"
        gmsl_alg = GMSL(input_file_path, 5, 0.0, output_file_path)
        gmsl_alg._output_file = open(output_file_path, "w")
        subgroups, bitarrays_of_positives, bitarrays_of_negatives = gmsl_alg._load_candidates(number_of_dataset_instances)
        self.assertEqual(len(subgroups), number_of_subgroups)
        self.assertEqual(len(bitarrays_of_positives), number_of_subgroups)
        self.assertEqual(len(bitarrays_of_negatives), number_of_subgroups)
        gmsl_alg._output_file.close()
        remove(input_file_path)
        remove(output_file_path)
    
    def test_GMSL_load_candidates_method_2(self) -> None:
        number_of_dataset_instances = 5 # Number of instances of the original dataset (i.e., from which the subgroups were extracted).
        number_of_subgroups = 11 # Number of subgroups from the input file.
        input_file_path = "./tmp_input.txt"
        input_file_content = "Description: [a = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [a = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [a = 'r'], Target: target = 'y' ; 00010 ; 00000\nDescription: [a = 'w'], Target: target = 'y' ; 00000 ; 01000\nDescription: [b = 21], Target: target = 'y' ; 00010 ; 00000\nDescription: [b = 22], Target: target = 'y' ; 00000 ; 11001\nDescription: [b = 23], Target: target = 'y' ; 00100 ; 00000\nDescription: [c = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [c = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [c = 'r'], Target: target = 'y' ; 00010 ; 00000\nDescription: [c = 'w'], Target: target = 'y' ; 00000 ; 01000"
        input_file = open(input_file_path, "w")
        input_file.write(input_file_content)
        input_file.close()
        output_file_path = "./tmp_output.txt"
        gmsl_alg = GMSL(input_file_path, 5, 0.0, output_file_path)
        gmsl_alg._output_file = open(output_file_path, "w")
        subgroups, bitarrays_of_positives, bitarrays_of_negatives = gmsl_alg._load_candidates(number_of_dataset_instances)
        self.assertEqual(len(subgroups), number_of_subgroups)
        self.assertEqual(len(bitarrays_of_positives), number_of_subgroups)
        self.assertEqual(len(bitarrays_of_negatives), number_of_subgroups)
        gmsl_alg._output_file.close()
        remove(input_file_path)
        remove(output_file_path)
    
    def test_GMSL_load_candidates_method_3(self) -> None:
        number_of_dataset_instances = 5 # Number of instances of the original dataset (i.e., from which the subgroups were extracted).
        number_of_subgroups = 11 # Number of subgroups from the input file.
        input_file_path = "./tmp_input.txt"
        input_file_content = "Description: [a = g], Target: target = 'y' ; 00000 ; 00001\nDescription: [a = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [a = 'r'], Target: target = 'y' ; 00010 ; 00000\nDescription: [a = 'w'], Target: target = 'y' ; 00000 ; 01000\nDescription: [b = 'g'], Target: target = 'y' ; 00010 ; 00000\nDescription: [b = 'q'], Target: target = 'y' ; 00000 ; 11001\nDescription: [b = 'v'], Target: target = 'y' ; 00100 ; 00000\nDescription: [c = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [c = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [c = r], Target: target = 'y' ; 00010 ; 00000\nDescription: [c = 'w'], Target: target = 'y' ; 00000 ; 01000"
        input_file = open(input_file_path, "w")
        input_file.write(input_file_content)
        input_file.close()
        output_file_path = "./tmp_output.txt"
        gmsl_alg = GMSL(input_file_path, 5, 0.0, output_file_path)
        gmsl_alg._output_file = open(output_file_path, "w")
        subgroups, bitarrays_of_positives, bitarrays_of_negatives = gmsl_alg._load_candidates(number_of_dataset_instances)
        self.assertEqual(len(subgroups), number_of_subgroups)
        self.assertEqual(len(bitarrays_of_positives), number_of_subgroups)
        self.assertEqual(len(bitarrays_of_negatives), number_of_subgroups)
        gmsl_alg._output_file.close()
        remove(input_file_path)
        remove(output_file_path)
    
    def test_GMSL_load_candidates_method_4(self) -> None:
        number_of_dataset_instances = 5 # Number of instances of the original dataset (i.e., from which the subgroups were extracted).
        number_of_subgroups = 11 # Number of subgroups from the input file.
        input_file_path = "./tmp_input.txt"
        input_file_content = "Description: [a = g, Target: target = 'y' ; 00000 ; 00001\ndescription: [a = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [a = 'r'], Target: target = 'y' ; 0001 ; 00000\nDescription: [a = 'w'], Target: target = 'y'; 00000 ; 01000\nDescription: [b = 'g'], Target: target = 'y' ; 00010 ; 00000\nDescription: [b = 'q'], Target: target = 'y' ; 00000 ; 11001\nDescription: [b = 'v'], Target: target = 'y' ; 00100 ; 00000\nDescription: [c = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [c = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [c = r], Target: target = 'y' ; 00010 ; 00000\nDescription: [c = 'w'], Target: target = 'y' ; 00000 ; 01000"
        input_file = open(input_file_path, "w")
        input_file.write(input_file_content)
        input_file.close()
        output_file_path = "./tmp_output.txt"
        gmsl_alg = GMSL(input_file_path, 5, 0.0, output_file_path)
        gmsl_alg._output_file = open(output_file_path, "w")
        subgroups, bitarrays_of_positives, bitarrays_of_negatives = gmsl_alg._load_candidates(number_of_dataset_instances)
        self.assertEqual(len(subgroups), 7)
        self.assertEqual(len(bitarrays_of_positives), 7)
        self.assertEqual(len(bitarrays_of_negatives), 7)
        gmsl_alg._output_file.close()
        remove(input_file_path)
        remove(output_file_path)
    
    def test_GMSL_load_candidates_method_5(self) -> None:
        number_of_dataset_instances = 5 # Number of instances of the original dataset (i.e., from which the subgroups were extracted).
        number_of_subgroups = 11 # Number of subgroups from the input file.
        input_file_path = "./tmp_input.txt"
        input_file_content = "Description: [a = g], Target: target == 'y' ; 00000 ; 00001\nDescription: [a != 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [a < 'r'], Target: target = 'y' ; 00010 ; 00000\nDescription: [a = 'w'], Target: target = 'y' ; 00000 ; 01000\nDescription: [b = 'g'], Target: target = 'y' ; 00010 ; 00000\nDescription: [b = 'q'], Target: target = 'y' ; 00000 ; 11001\nDescription: [b = 'v'], Target: target = 'y' ; 00100 ; 00000\nDescription: [c = 'g'], Target: target = 'y' ; 00000 ; 00001\nDescription: [c = 'q'], Target: target = 'y' ; 00100 ; 10000\nDescription: [c = r], Target: target = 'y' ; 00010 ; 00000\nDescription: [c = 'w'], Target: target = 'y' ; 00000 ; 01000"
        input_file = open(input_file_path, "w")
        input_file.write(input_file_content)
        input_file.close()
        output_file_path = "./tmp_output.txt"
        gmsl_alg = GMSL(input_file_path, 5, 0.0, output_file_path)
        gmsl_alg._output_file = open(output_file_path, "w")
        subgroups, bitarrays_of_positives, bitarrays_of_negatives = gmsl_alg._load_candidates(number_of_dataset_instances)
        self.assertEqual(len(subgroups), 8)
        self.assertEqual(len(bitarrays_of_positives), 8)
        self.assertEqual(len(bitarrays_of_negatives), 8)
        gmsl_alg._output_file.close()
        remove(input_file_path)
        remove(output_file_path)
    
    def test_GMSL_fit_method_1(self) -> None:
        gmsl_alg = GMSL("", 3, 0.0, "")
        self.assertRaises(TypeError, gmsl_alg.fit, 23, ("a", "a"))
        self.assertRaises(TypeError, gmsl_alg.fit, DataFrame({"a" : ["1", "2", "3", "4"], "target" : ["4", "5", "6", "7"]}), "aaa")
        self.assertRaises(ValueError, gmsl_alg.fit, DataFrame({}), ("a", "a"))
        self.assertRaises(DatasetAttributeTypeError, gmsl_alg.fit, DataFrame({"a" : [1, 2, 3, 4], "target" : ["4", "5", "6", "7"]}), ("a", "a"))
    
    def test_GMSL_fit_method_2(self) -> None:
        # Dataset.
        dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/car/car.data"
        df = read_csv(dataset_url, names=["buying", "maint", "doors", "persons", "lug_boot", "safety"])
        df.reset_index(drop=True, inplace=True)
        target = ("safety", "unacc")
        self.assertEqual(len(df), 1728)
        self.assertEqual(len(df.columns), 6)
        # VLSD algorithm.
        vlsd_results_tmp_file_path = "./vlsd_results_tmp.txt"
        vlsd_alg = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, \
                        vertical_lists_implementation = VLSD.VERTICAL_LISTS_WITH_BITSETS, \
                        write_results_in_file = True, file_path = vlsd_results_tmp_file_path)
        vlsd_alg.fit(df, target)
        expected_subgroups = 1599
        self.assertEqual(vlsd_alg.selected_subgroups, expected_subgroups)
        self.assertEqual(vlsd_alg.unselected_subgroups, 0)
        self.assertEqual(vlsd_alg.visited_nodes, expected_subgroups)
        # Regular expression to read the results.
        selector_regex_pattern = "[A-Za-z0-9_-]+ = ([A-Za-z0-9_-]+|'[A-Za-z0-9_-]+')"
        pattern_regex_pattern = "\\[" + selector_regex_pattern + "(, " + selector_regex_pattern + ")*\\]"
        input_line_regex_pattern = "^(?P<subgroup>Description: " + pattern_regex_pattern + ", Target: " + selector_regex_pattern + ")" +\
                                   " ; Sequence of instances tp = bitarray\\('(?P<positive_bitarray>[01]+)'\\)" +\
                                   " ; Sequence of instances fp = bitarray\\('(?P<negative_bitarray>[01]+)'\\) ; .+$"
        input_line_regex_object = compile(input_line_regex_pattern)
        # Generate the correct input file for the GMSL algorithm.
        vlsd_results_file_path = "./vlsd_results.txt"
        vlsd_results_file = open(vlsd_results_file_path, "w")
        with open(vlsd_results_tmp_file_path, "r") as vlsd_results_tmp_file:
            for line in vlsd_results_tmp_file: # Read line by line.
                match_object = input_line_regex_object.fullmatch(line.rstrip("\n"))
                self.assertIsNotNone(match_object)
                subgroup = match_object.group("subgroup")
                positive_bitarray = match_object.group("positive_bitarray")
                negative_bitarray = match_object.group("negative_bitarray")
                useful_line = subgroup + " ; " + positive_bitarray + " ; " + negative_bitarray + "\n"
                vlsd_results_file.write(useful_line)
        vlsd_results_file.close()
        # GMSL algorithm.
        # beta = 0.0
        gmsl_results_file_path = "./gmsl_results.txt"
        gmsl_alg = GMSL(vlsd_results_file_path, 3, 0.0, gmsl_results_file_path)
        gmsl_alg.fit(df, target)
        # beta = 0.5
        gmsl_results_file_path = "./gmsl_results.txt"
        gmsl_alg = GMSL(vlsd_results_file_path, 3, 0.5, gmsl_results_file_path)
        gmsl_alg.fit(df, target)
        # beta = 1.0
        gmsl_results_file_path = "./gmsl_results.txt"
        gmsl_alg = GMSL(vlsd_results_file_path, 3, 1.0, gmsl_results_file_path)
        gmsl_alg.fit(df, target)
        # Remove files.
        remove(vlsd_results_tmp_file_path)
        remove(vlsd_results_file_path)
        remove(gmsl_results_file_path)
