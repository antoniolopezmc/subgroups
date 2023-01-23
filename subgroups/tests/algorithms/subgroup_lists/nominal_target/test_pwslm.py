# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/pwslm.py'.
"""

from subgroups.algorithms.subgroup_lists.nominal_target.pwslm import PWSLM
from subgroups.core import Subgroup, Pattern, Selector, Operator
from bitarray import bitarray
import unittest

class TestPWSLM(unittest.TestCase):
    
    def test_PWSLM_counter_of_subgroups_1(self) -> None:
        # We suppose a data with 41 instances.
        dataset_number_of_instances = 41
        ## Counters.
        positive_counter_of_subgroups = [0] * dataset_number_of_instances
        negative_counter_of_subgrouos = [0] * dataset_number_of_instances
        ## Add s1 to the empty subgroup list.
        # - Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("11001100110011001100110011001100110011000", endian = "big")
        bitarray_of_negatives = bitarray("00000000000000000000000000000000000000000", endian = "big")
        self.assertEqual(positive_counter_of_subgroups, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        self.assertEqual(negative_counter_of_subgrouos, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        for index in range(dataset_number_of_instances):
            if bitarray_of_positives[index]:
                positive_counter_of_subgroups[index] = positive_counter_of_subgroups[index] + 1
            if bitarray_of_negatives[index]:
                negative_counter_of_subgrouos[index] = negative_counter_of_subgrouos[index] + 1
        self.assertEqual(positive_counter_of_subgroups, [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0])
        self.assertEqual(negative_counter_of_subgrouos, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        ## Add s2 to the subgroup list.
        # - Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("00000000000000000000000000000000000000000", endian = "big")
        bitarray_of_negatives = bitarray("11001100110011001100110011001100110011000", endian = "big")
        self.assertEqual(positive_counter_of_subgroups, [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0])
        self.assertEqual(negative_counter_of_subgrouos, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        for index in range(dataset_number_of_instances):
            if bitarray_of_positives[index]:
                positive_counter_of_subgroups[index] = positive_counter_of_subgroups[index] + 1
            if bitarray_of_negatives[index]:
                negative_counter_of_subgrouos[index] = negative_counter_of_subgrouos[index] + 1
        self.assertEqual(positive_counter_of_subgroups, [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0])
        self.assertEqual(negative_counter_of_subgrouos, [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0])
    
    def test_PWSLM_counter_of_subgroups_2(self) -> None:
        # We suppose a data with 40 instances.
        dataset_number_of_instances = 40
        ## Counters.
        positive_counter_of_subgroups = [0] * dataset_number_of_instances
        negative_counter_of_subgrouos = [0] * dataset_number_of_instances
        ## Add s1 to the empty subgroup list.
        # - Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("1100000011000000110000001100000011000000", endian = "big")
        bitarray_of_negatives = bitarray("0000110000001100000011000000110000001100", endian = "big")
        self.assertEqual(positive_counter_of_subgroups, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        self.assertEqual(negative_counter_of_subgrouos, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        for index in range(dataset_number_of_instances):
            if bitarray_of_positives[index]:
                positive_counter_of_subgroups[index] = positive_counter_of_subgroups[index] + 1
            if bitarray_of_negatives[index]:
                negative_counter_of_subgrouos[index] = negative_counter_of_subgrouos[index] + 1
        self.assertEqual(positive_counter_of_subgroups, [1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0])
        self.assertEqual(negative_counter_of_subgrouos, [0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0])
    
    def test_PWSLM_compute_overlap_factor_function_1(self) -> None:
        ###################
        #### EXAMPLE 1 ####
        ###################
        subgroup = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector("target", Operator.EQUAL, "value1"))
        # Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("1100000011000000110000001100000011000000", endian = "big")
        bitarray_of_negatives = bitarray("0000110000001100000011000000110000001100", endian = "big")
        positive_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        negative_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        positive_overlap_factor = PWSLM._compute_positive_overlap_factor(subgroup, bitarray_of_positives, positive_counter_of_subgroups)
        negative_overlap_factor = PWSLM._compute_negative_overlap_factor(subgroup, bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_overlap_factor, 0.0)
        self.assertEqual(negative_overlap_factor, 0.0)
        ###################
        #### EXAMPLE 2 ####
        ###################
        subgroup = Subgroup(Pattern([Selector("at2", Operator.EQUAL, "b")]), Selector("target", Operator.EQUAL, "value1"))
        # Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("1100000011000000110000001100000011000000", endian = "big")
        bitarray_of_negatives = bitarray("0000110000001100000011000000110000001100", endian = "big")
        positive_counter_of_subgroups = [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        negative_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,0,0]
        positive_overlap_factor = PWSLM._compute_positive_overlap_factor(subgroup, bitarray_of_positives, positive_counter_of_subgroups)
        negative_overlap_factor = PWSLM._compute_negative_overlap_factor(subgroup, bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_overlap_factor, 2/3)
        self.assertEqual(positive_overlap_factor, 2/sum(positive_counter_of_subgroups))
        self.assertEqual(negative_overlap_factor, 4/6)
        self.assertEqual(negative_overlap_factor, 4/sum(negative_counter_of_subgroups))
        ###################
        #### EXAMPLE 3 ####
        ###################
        subgroup = Subgroup(Pattern([Selector("at3", Operator.EQUAL, "c")]), Selector("target", Operator.EQUAL, "value1"))
        # Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("1100000011000000110000001100000011000000", endian = "big")
        bitarray_of_negatives = bitarray("0000110000001100000011000000110000011100", endian = "big")
        positive_counter_of_subgroups = [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        negative_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,0,0]
        positive_overlap_factor = PWSLM._compute_positive_overlap_factor(subgroup, bitarray_of_positives, positive_counter_of_subgroups)
        negative_overlap_factor = PWSLM._compute_negative_overlap_factor(subgroup, bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_overlap_factor, 2/3)
        self.assertEqual(positive_overlap_factor, 2/sum(positive_counter_of_subgroups))
        self.assertEqual(negative_overlap_factor, 6/6)
        self.assertEqual(negative_overlap_factor, 6/sum(negative_counter_of_subgroups))
        ###################
        #### EXAMPLE 4 ####
        ###################
        subgroup = Subgroup(Pattern([Selector("at4", Operator.EQUAL, "d")]), Selector("target", Operator.EQUAL, "value1"))
        # Bitarrays considering the complemente dataset.
        bitarray_of_positives = bitarray("0000000000000000000000000000000000000000", endian = "big")
        bitarray_of_negatives = bitarray("0000000000000000000000000000000000000000", endian = "big")
        positive_counter_of_subgroups = [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        negative_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,0,0]
        positive_overlap_factor = PWSLM._compute_positive_overlap_factor(subgroup, bitarray_of_positives, positive_counter_of_subgroups)
        negative_overlap_factor = PWSLM._compute_negative_overlap_factor(subgroup, bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_overlap_factor, 1.0)
        self.assertEqual(negative_overlap_factor, 0.0)
    
    def test_PWSLM_compute_overlap_factor_function_2(self) -> None:
        # s1 -> This is the only subgroup in the list.
        s1 = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector("target", Operator.EQUAL, "value1"))
        s1_bitarray_of_positives = bitarray("1111111111111111111100000000000000000000", endian = "big")
        s1_bitarray_of_negatives = bitarray("0000000000000000000011111111111111111111", endian = "big")
        positive_counter_of_subgroups = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        negative_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        # s2 -> candidate.
        s2 = Subgroup(Pattern([Selector("at2", Operator.EQUAL, "b")]), Selector("target", Operator.EQUAL, "value1"))
        s2_bitarray_of_positives = bitarray("1100000000000000000000000000000000000001", endian = "big")
        s2_bitarray_of_negatives = bitarray("0000000000000000000000000000000000000011", endian = "big")
        # Overlap factors between s2 and the previous subgroups (i.e., s1).
        positive_of_s2 = PWSLM._compute_positive_overlap_factor(s2, s2_bitarray_of_positives, positive_counter_of_subgroups)
        negative_of_s2 = PWSLM._compute_negative_overlap_factor(s2, s2_bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_of_s2, 2/20)
        self.assertEqual(positive_of_s2, 2/sum(positive_counter_of_subgroups))
        self.assertEqual(negative_of_s2, 2/20)
        self.assertEqual(negative_of_s2, 2/sum(negative_counter_of_subgroups))
        # s3 -> candidate.
        s3 = Subgroup(Pattern([Selector("at3", Operator.EQUAL, "c")]), Selector("target", Operator.EQUAL, "value1"))
        s3_bitarray_of_positives = bitarray("1000000000000000000000000000000000000011", endian = "big")
        s3_bitarray_of_negatives = bitarray("1100000000000000000000000000000000000111", endian = "big")
        # Overlap factors between s3 and the previous subgroups (i.e., s1).
        positive_of_s3 = PWSLM._compute_positive_overlap_factor(s3, s3_bitarray_of_positives, positive_counter_of_subgroups)
        negative_of_s3 = PWSLM._compute_negative_overlap_factor(s3, s3_bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_of_s3, 1/20)
        self.assertEqual(positive_of_s3, 1/sum(positive_counter_of_subgroups))
        self.assertEqual(negative_of_s3, 3/20)
        self.assertEqual(negative_of_s3, 3/sum(negative_counter_of_subgroups))
        # In the positive instances, there is more overlap between s2 and s1 than between s3 and s1.
        self.assertGreater(positive_of_s2, positive_of_s3)
        # In the negative instances, there is more overlap between s3 ans s1 than between s2 and s1.
        self.assertGreater(negative_of_s3, negative_of_s2)

    def test_PWSLM_compute_overlap_factor_function_3(self) -> None:
        # s1 -> This is the only subgroup in the list.
        s1 = Subgroup(Pattern([Selector("at1", Operator.EQUAL, "a")]), Selector("target", Operator.EQUAL, "value1"))
        s1_bitarray_of_positives = bitarray("1111111111111111111100000000000000000000", endian = "big")
        s1_bitarray_of_negatives = bitarray("0000000000000000000011111111111111111111", endian = "big")
        positive_counter_of_subgroups = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        negative_counter_of_subgroups = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        # s2 -> candidate.
        s2 = Subgroup(Pattern([Selector("at2", Operator.EQUAL, "b")]), Selector("target", Operator.EQUAL, "value1"))
        s2_bitarray_of_positives = bitarray("1111111111111111111100000000000000000000", endian = "big")
        s2_bitarray_of_negatives = bitarray("0000000000000000000000000000000000000000", endian = "big")
        positive_of_s2 = PWSLM._compute_positive_overlap_factor(s2, s2_bitarray_of_positives, positive_counter_of_subgroups)
        negative_of_s2 = PWSLM._compute_negative_overlap_factor(s2, s2_bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_of_s2, 20/20)
        self.assertEqual(negative_of_s2, 0.0)
        # s3 -> candidate.
        s3 = Subgroup(Pattern([Selector("at3", Operator.EQUAL, "c")]), Selector("target", Operator.EQUAL, "value1"))
        s3_bitarray_of_positives = bitarray("0000000000000000000000000000000000000000", endian = "big")
        s3_bitarray_of_negatives = bitarray("0000000000000000000011111111111111111111", endian = "big")
        positive_of_s3 = PWSLM._compute_positive_overlap_factor(s3, s3_bitarray_of_positives, positive_counter_of_subgroups)
        negative_of_s3 = PWSLM._compute_negative_overlap_factor(s3, s3_bitarray_of_negatives, negative_counter_of_subgroups)
        self.assertEqual(positive_of_s3, 1.0)
        self.assertEqual(negative_of_s3, 20/20)