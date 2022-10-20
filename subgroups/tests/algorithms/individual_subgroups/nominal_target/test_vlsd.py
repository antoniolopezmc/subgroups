# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/vlsd.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.individual_subgroups.nominal_target.vlsd import VLSD
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
from subgroups.quality_measures.qg import Qg
from subgroups.exceptions import DatasetAttributeTypeError
from subgroups.core.subgroup import Subgroup
from os import remove
import unittest

class TestVLSD(unittest.TestCase):

    def test_VLSD_init_method_1(self) -> None:
        dictionary = dict()
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, additional_parameters_for_the_quality_measure=dictionary, additional_parameters_for_the_optimistic_estimate=dictionary)
        self.assertEqual(len(vlsd.additional_parameters_for_the_quality_measure), 0)
        self.assertEqual(len(vlsd.additional_parameters_for_the_optimistic_estimate), 0)
        self.assertEqual(vlsd.additional_parameters_for_the_quality_measure, dictionary)
        self.assertEqual(vlsd.additional_parameters_for_the_optimistic_estimate, dictionary)
        self.assertEqual(vlsd.additional_parameters_for_the_quality_measure, vlsd.additional_parameters_for_the_optimistic_estimate)
        self.assertNotEqual(id(vlsd.additional_parameters_for_the_quality_measure), id(dictionary))
        self.assertNotEqual(id(vlsd.additional_parameters_for_the_optimistic_estimate), id(dictionary))
        self.assertNotEqual(id(vlsd.additional_parameters_for_the_quality_measure), id(vlsd.additional_parameters_for_the_optimistic_estimate))
        dictionary = dict({"g" : 0.5})
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, additional_parameters_for_the_quality_measure=dictionary, additional_parameters_for_the_optimistic_estimate=dictionary)
        self.assertEqual(len(vlsd.additional_parameters_for_the_quality_measure), 1)
        self.assertEqual(len(vlsd.additional_parameters_for_the_optimistic_estimate), 1)
        self.assertEqual(vlsd.additional_parameters_for_the_quality_measure, dictionary)
        self.assertEqual(vlsd.additional_parameters_for_the_optimistic_estimate, dictionary)
        self.assertEqual(vlsd.additional_parameters_for_the_quality_measure, vlsd.additional_parameters_for_the_optimistic_estimate)
        self.assertNotEqual(id(vlsd.additional_parameters_for_the_quality_measure), id(dictionary))
        self.assertNotEqual(id(vlsd.additional_parameters_for_the_optimistic_estimate), id(dictionary))
        self.assertNotEqual(id(vlsd.additional_parameters_for_the_quality_measure), id(vlsd.additional_parameters_for_the_optimistic_estimate))
        self.assertIsNot(vlsd.additional_parameters_for_the_quality_measure, dictionary)
        self.assertIsNot(vlsd.additional_parameters_for_the_optimistic_estimate, dictionary)
        self.assertIsNot(vlsd.additional_parameters_for_the_quality_measure, vlsd.additional_parameters_for_the_optimistic_estimate)
        self.assertEqual(vlsd.additional_parameters_for_the_quality_measure["g"], 0.5)
        self.assertEqual(vlsd.additional_parameters_for_the_optimistic_estimate["g"], 0.5)
        vlsd.additional_parameters_for_the_optimistic_estimate["g"] = 0.1
        self.assertNotEqual(vlsd.additional_parameters_for_the_quality_measure, vlsd.additional_parameters_for_the_optimistic_estimate)
        self.assertEqual(vlsd.additional_parameters_for_the_quality_measure["g"], 0.5)
        self.assertEqual(vlsd.additional_parameters_for_the_optimistic_estimate["g"], 0.1)

    def test_VLSD_init_method_2(self) -> None:
        VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -0.85)
        # WRAccOptimisticEstimate1 quality measure is not an optimistic stimate of the Qg quality measure.
        self.assertRaises(ValueError, VLSD, Qg(), -1, WRAccOptimisticEstimate1(), -0.85, additional_parameters_for_the_quality_measure={"Qg" : 0.2})

    def test_VLSD_fit_method_1(self) -> None:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -0.85)
        self.assertRaises(DatasetAttributeTypeError, vlsd.fit, df, ("class", 0))
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), 0.85)
        self.assertRaises(DatasetAttributeTypeError, vlsd.fit, df, ("class", "0"))
        df = DataFrame({"att1" : [4,5,2,6], "class" : ["0","1","2","2"]}) # All the attributes must be nominal (type 'str').
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), 0.85)
        self.assertRaises(DatasetAttributeTypeError, vlsd.fit, df, ("class", "0"))

    def test_VLSD_fit_method_2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        ### VERTICAL LISTS IMPLEMENTED WITH SETS ###
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, vertical_lists_implementation = VLSD.VERTICAL_LISTS_WITH_SETS, write_results_in_file=True, file_path="./results.txt")
        self.assertEqual(vlsd._vertical_lists_implementation, VLSD.VERTICAL_LISTS_WITH_SETS)
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 25)
        self.assertEqual(vlsd.unselected_subgroups, 0)
        self.assertEqual(vlsd.visited_nodes, 25)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")
        ### VERTICAL LISTS IMPLEMENTED WITH BITSETS ###
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, vertical_lists_implementation = VLSD.VERTICAL_LISTS_WITH_BITSETS, write_results_in_file=True, file_path="./results.txt")
        self.assertEqual(vlsd._vertical_lists_implementation, VLSD.VERTICAL_LISTS_WITH_BITSETS)
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 25)
        self.assertEqual(vlsd.unselected_subgroups, 0)
        self.assertEqual(vlsd.visited_nodes, 25)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_VLSD_fit_method_3(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        vlsd = VLSD(WRAcc(), 0, WRAccOptimisticEstimate1(), 0, write_results_in_file=True, file_path="./results.txt")
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 13)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_VLSD_fit_method_4(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        vlsd = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, write_results_in_file=True, file_path="./results.txt")
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 12)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_VLSD_fit_method_5(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: the subgroup parameters TP and FP (inserted as additional parameters) must be deleted in the __init__ method.
        vlsd = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, additional_parameters_for_the_quality_measure={"TP" : 100000, "g" : 0.5}, additional_parameters_for_the_optimistic_estimate={"FP" : 100000, "g" : 0.4}, write_results_in_file=True, file_path="./results.txt")
        self.assertEqual(len(vlsd.additional_parameters_for_the_quality_measure), 1)
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 12)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_VLSD_fit_method_6(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, sort_criterion_in_s1 = "quality-ascending", sort_criterion_in_other_sizes = "no-order", write_results_in_file=True, file_path="./results.txt")
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 25)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_VLSD_fit_method_7(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, sort_criterion_in_s1 = "no-order", sort_criterion_in_other_sizes = "quality-descending", write_results_in_file=True, file_path="./results.txt")
        vlsd.fit(df, target)
        self.assertEqual(vlsd.selected_subgroups, 25)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_VLSD_additional_parameters_in_fit_method(self) -> None:
        vlsd_1 = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, additional_parameters_for_the_quality_measure={"tp" : 10, "fp" : 20, "TP" : 100, "FP" : 200}, additional_parameters_for_the_optimistic_estimate={"tp" : 10, "fp" : 20, "TP" : 100, "FP" : 200})
        self.assertEqual(len(vlsd_1._additional_parameters_for_the_quality_measure), 0)
        self.assertEqual(len(vlsd_1._additional_parameters_for_the_optimistic_estimate), 0)
        vlsd_2 = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, additional_parameters_for_the_quality_measure={"tp" : 10, "fp" : 20, "TP" : 1000}, additional_parameters_for_the_optimistic_estimate={"tp" : 10, "fp" : 20, "TP" : 1000})
        self.assertEqual(len(vlsd_2._additional_parameters_for_the_quality_measure), 0)
        self.assertEqual(len(vlsd_2._additional_parameters_for_the_optimistic_estimate), 0)
        vlsd_3 = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, additional_parameters_for_the_quality_measure={"tp" : 10, "fp" : 20, "TP" : 100, "FP" : 200, "a" : 0.1}, additional_parameters_for_the_optimistic_estimate={"tp" : 10, "fp" : 20, "TP" : 100, "FP" : 200, "b" : 0.1})
        self.assertEqual(len(vlsd_3._additional_parameters_for_the_quality_measure), 1)
        self.assertEqual(len(vlsd_3._additional_parameters_for_the_optimistic_estimate), 1)
