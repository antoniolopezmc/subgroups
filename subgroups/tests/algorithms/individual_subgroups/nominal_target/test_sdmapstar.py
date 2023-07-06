# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/sdmapstar.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.individual_subgroups.nominal_target.sdmapstar import SDMapStar
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
from subgroups.quality_measures.qg import Qg
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError, ParameterNotFoundError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.core.subgroup import Subgroup
from os import remove
import unittest

class TestSDMapStar(unittest.TestCase):

    def test_SDMapStar_init_method_1(self) -> None:
        self.assertRaises(TypeError, SDMapStar, "hello", 0.85)
        self.assertRaises(TypeError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),"hello")
        self.assertRaises(InconsistentMethodParametersError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),0.85)
        self.assertRaises(InconsistentMethodParametersError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_tp=0)
        self.assertRaises(InconsistentMethodParametersError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_fp=0)
        self.assertRaises(InconsistentMethodParametersError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_tp=0, minimum_n=0)
        self.assertRaises(InconsistentMethodParametersError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_fp=0, minimum_n=0)
        self.assertRaises(InconsistentMethodParametersError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_tp=0, minimum_fp=0, minimum_n=0)
        dictionary = dict()
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, additional_parameters_for_the_quality_measure=dictionary)
        self.assertEqual(len(sdmap.additional_parameters_for_the_quality_measure), 0)
        self.assertEqual(sdmap.additional_parameters_for_the_quality_measure, dictionary)
        self.assertNotEqual(id(sdmap.additional_parameters_for_the_quality_measure), id(dictionary))
        self.assertIsNot(sdmap.additional_parameters_for_the_quality_measure, dictionary)
        dictionary = dict({"g" : 0.5})
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, additional_parameters_for_the_quality_measure=dictionary)
        self.assertEqual(len(sdmap.additional_parameters_for_the_quality_measure), 1)
        self.assertEqual(sdmap.additional_parameters_for_the_quality_measure, dictionary)
        self.assertNotEqual(id(sdmap.additional_parameters_for_the_quality_measure), id(dictionary))
        self.assertIsNot(sdmap.additional_parameters_for_the_quality_measure, dictionary)
        self.assertEqual(sdmap.additional_parameters_for_the_quality_measure["g"], 0.5)

    def test_SDMapStar_init_method_2(self) -> None:
        SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=False)
        SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=False, file_path="./sdfsdfs/adrwfxc") # Path does not exist, but it does not matter because the flag is False.
        self.assertRaises(TypeError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=True, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(TypeError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=False, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(ValueError, SDMapStar, WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=True, file_path=None) # If 'write_results_in_file' is True, 'file_path' must not be None.

    def test_SDMapStar_fpgrowth_method_1(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        TP = 2
        FP = 2
        minimum_n = 0
        fp_tree = FPTreeForSDMap()
        frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_n=minimum_n)
        fp_tree.build_tree(df, frequent_selectors_dict, target)
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=minimum_n)
        sdmap._fpgrowth(fp_tree, None, target, TP, FP)
        # Minimum WRAcc = -1 and minimum n = 0. For this reason, all possible nodes of the tree are built and all subgroups are generated.
        self.assertEqual(sdmap.selected_subgroups, 25)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 25)

    def test_SDMapStar_fpgrowth_method_2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        TP = 2
        FP = 2
        minimum_n = 2
        fp_tree = FPTreeForSDMap()
        frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_n=minimum_n)
        fp_tree.build_tree(df, frequent_selectors_dict, target)
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=minimum_n)
        sdmap._fpgrowth(fp_tree, None, target, TP, FP)
        # Minimum WRAcc = -1 and minimum n = 2. For this reason, not all possible nodes of the tree are built (although all explored subgroups are generated). 
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)

    def test_SDMapStar_fpgrowth_method_3(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        TP = 2
        FP = 2
        minimum_tp = 1
        minimum_fp = 1
        fp_tree = FPTreeForSDMap()
        frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_tp=minimum_tp, minimum_fp=minimum_fp)
        fp_tree.build_tree(df, frequent_selectors_dict, target)
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=minimum_tp, minimum_fp=minimum_fp)
        sdmap._fpgrowth(fp_tree, None, target, TP, FP)
        # Minimum WRAcc = -1 and minimum n = 2 (1 + 1). For this reason, not all possible nodes of the tree are built (although all explored subgroups are generated). 
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)

    def test_SDMapStar_fpgrowth_method_4(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        TP = 2
        FP = 2
        minimum_tp = 1
        minimum_fp = 0
        fp_tree = FPTreeForSDMap()
        frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_tp=minimum_tp, minimum_fp=minimum_fp)
        fp_tree.build_tree(df, frequent_selectors_dict, target)
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=minimum_tp, minimum_fp=minimum_fp)
        sdmap._fpgrowth(fp_tree, None, target, TP, FP)
        # Minimum WRAcc = -1 and minimum n = 1 (1 + 0). For this reason, not all possible nodes of the tree are built (although all explored subgroups are generated). 
        self.assertEqual(sdmap.selected_subgroups, 13)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 13)

    def test_SDMapStar_fit_method_1(self) -> None:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_tp=0, minimum_fp=0)
        self.assertRaises(DatasetAttributeTypeError, sdmap.fit, df, ("class", 0))
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_tp=0, minimum_fp=0)
        self.assertRaises(DatasetAttributeTypeError, sdmap.fit, df, ("class", "0"))
        df = DataFrame({"att1" : [4,5,2,6], "class" : ["0","1","2","2"]}) # All the attributes must be nominal (type 'str').
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.85, minimum_tp=0, minimum_fp=0)
        self.assertRaises(DatasetAttributeTypeError, sdmap.fit, df, ("class", "0"))

    def test_SDMapStar_fit_method_2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 25)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 25)
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

    def test_SDMapStar_fit_method_3(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=2, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_SDMapStar_fit_method_4(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=1, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_SDMapStar_fit_method_5(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=0, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 13)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 13)
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

    def test_SDMapStar_fit_method_6(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0, minimum_tp=1, minimum_fp=0, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 13)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 13)
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

    def test_SDMapStar_fit_method_7(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.1, minimum_tp=1, minimum_fp=0, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 12)
        self.assertEqual(sdmap.unselected_subgroups, 1)
        self.assertEqual(sdmap.visited_nodes, 13)
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

    def test_SDMapStar_fit_method_8(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.1, minimum_n=0, write_results_in_file=True, file_path="./results.txt")
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 12)
        self.assertEqual(sdmap.unselected_subgroups, 13)
        self.assertEqual(sdmap.visited_nodes, 25)
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

    def test_SDMapStar_fit_method_9(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: the subgroup parameter TP will be deleted in the __init__ method.
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"TP" : 100000, "g" : 0.5}, write_results_in_file=True, file_path="./results.txt")
        self.assertEqual(len(sdmap.additional_parameters_for_the_quality_measure), 1)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")
            
    def test_SDMapStar_fit_method_10(self) -> None:
        df = DataFrame({'att1': ['v3', 'v2', 'v1', 'v3', 'v4', 'v4'], 'att2': ['1', '2', '3', '3', '5', '6'], 'att3': ['B', 'A', 'A', 'B', 'A', 'B'], 'class': ['0', '1', '0', '0', '1', '1']})
        algSDMap = SDMapStar(WRAcc(),WRAccOptimisticEstimate1(), -1000, num_subgroups=5, minimum_n = 0,  write_results_in_file=True, file_path="./results.txt")
        algSDMap.fit(df, ("class", "1"))
        list_of_written_results = []
        file_to_read = open("./results.txt", "r")
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]        
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4', att3 = 'B'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4', att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att2 = '6'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4', att2 = '6'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att2 = '6', att3 = 'B'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4', att2 = '6', att3 = 'B'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att2 = '5'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4', att2 = '5'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att2 = '5', att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v4', att2 = '5', att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att2 = '2'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v2', att2 = '2'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att2 = '2', att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v2', att2 = '2', att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v2'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att1 = 'v2', att3 = 'A'], Target: class = '1'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [att3 = 'B'], Target: class = '1'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")

    def test_SDMapStar_additional_parameters_in_fit_method(self) -> None:
        sdmap_1 = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"tp" : 10, "fp" : 20, "TP" : 100, "FP" : 200})
        self.assertEqual(len(sdmap_1._additional_parameters_for_the_quality_measure), 0)
        sdmap_2 = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"tp" : 10, "fp" : 20, "TP" : 1000})
        self.assertEqual(len(sdmap_2._additional_parameters_for_the_quality_measure), 0)
        sdmap_3 = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"tp" : 10, "fp" : 20, "TP" : 100, "FP" : 200, "g" : 0.1})
        self.assertEqual(len(sdmap_3._additional_parameters_for_the_quality_measure), 1)

    def test_SDMapStar_unselected_and_selected_subgroups_1(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 25)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 25)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=2) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=1) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 2)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 2)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 13)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 13)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 13)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 13)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.1, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 12)
        self.assertEqual(sdmap.unselected_subgroups, 1)
        self.assertEqual(sdmap.visited_nodes, 13)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.1, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 12)
        self.assertEqual(sdmap.unselected_subgroups, 13)
        self.assertEqual(sdmap.visited_nodes, 25)
        # ---------------------------------------
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.2, minimum_n=2) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 2)
        self.assertEqual(sdmap.visited_nodes, 2)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),0.2, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 0)
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 0)
        self.assertEqual(sdmap.unselected_subgroups, 25)
        self.assertEqual(sdmap.visited_nodes, 25)

    def test_SDMapStar_unselected_and_selected_subgroups_2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0,num_subgroups=15)  # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 25)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 25)
        self.assertEqual(sdmap.conditional_pruned_branches, 0)
        # ---------------------------------------
        sdmap = SDMapStar(WRAcc(), WRAccOptimisticEstimate1(),-1, minimum_n=0,num_subgroups=10)  # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        sdmap.fit(df, target)
        self.assertEqual(sdmap.selected_subgroups, 13)
        self.assertEqual(sdmap.unselected_subgroups, 0)
        self.assertEqual(sdmap.visited_nodes, 13)
        self.assertEqual(sdmap.conditional_pruned_branches, 1)
       