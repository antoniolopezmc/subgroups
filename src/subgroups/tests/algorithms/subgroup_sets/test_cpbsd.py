# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles <franciscojose.morac@um.es>

"""Tests of the functionality contained in the file 'algorithms/cpbsd.py'.
"""

from os import remove
from bitarray import bitarray
from pandas import DataFrame
from subgroups.algorithms.subgroup_sets.cpbsd import CPBSD
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
import unittest


class TestCPBSD(unittest.TestCase):

    def test_CPBSD_init_method(self) -> None:
        self.assertRaises(TypeError, CPBSD, 0, "hello")
        self.assertRaises(TypeError, CPBSD, 0, WRAcc(),"hello")
        self.assertRaises(TypeError, CPBSD, 0, WRAcc(),WRAccOptimisticEstimate1(),"hello")
        self.assertRaises(TypeError, CPBSD, 0, WRAcc(),WRAccOptimisticEstimate1(),1,"hello")
        CPBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        CPBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False,file_path="./asdasfha/fsdvm") # Path does not exist, but it is not checked
        self.assertRaises(TypeError, CPBSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=True, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(TypeError, CPBSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=False, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(ValueError, CPBSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=True, file_path=None) # If 'write_results_in_file' is True, 'file_path' must not be None.

    def test_CPBSD_checkRel(self) -> None:
        bsd = CPBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110000"))]
        self.assertFalse(bsd._checkRel(res,bitarray("110"),0.,Pattern([])))
        self.assertTrue(bsd._checkRel(res,bitarray("100"),0.1,Pattern([])))
        self.assertTrue(bsd._checkRel(res,bitarray("101"),0.,Pattern([])))
        
    def test_CPBSD_checkRelevancies(self) -> None:
        bsd = CPBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110000")),(0,Pattern([Selector("att1",Operator.EQUAL,"B")]),bitarray("110000"))]
        bsd._k_subgroups = res
        bsd._checkRelevancies(bitarray("100001"),Pattern([Selector("att1",Operator.EQUAL,"A")]),0.1)
        self.assertEqual(bsd._k_subgroups,res)
        bsd._checkRelevancies(bitarray("100001"),Pattern([Selector("att1",Operator.EQUAL,"A")]),0.)
        self.assertEqual(bsd._k_subgroups,res)
        bsd._checkRelevancies(bitarray("110000"),Pattern([Selector("att1",Operator.EQUAL,"A")]),0.)
        self.assertNotEqual(bsd._k_subgroups,res)

    def test_CPBSD_fit1(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = CPBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 5)
        self.assertEqual(bsd.unselected_subgroups, 56)
        self.assertEqual(bsd.visited_subgroups, 25)
        
    def test_CPBSD_fit2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = CPBSD(0, WRAcc(),WRAccOptimisticEstimate1(),2,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 2)
        self.assertEqual(bsd.unselected_subgroups, 23)
        self.assertEqual(bsd.visited_subgroups, 17)
        
    def test_CPBSD_fit3(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = CPBSD(200, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 0)
        self.assertEqual(bsd.unselected_subgroups, 0)
        self.assertEqual(bsd.visited_subgroups, 0)
    
    def test_CPBSD_fit4(self) -> None:
        df = DataFrame({'bread': {0: 'yes', 1: 'yes', 2: 'no', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'milk': {0: 'yes', 1: 'no', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'beer': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'no', 5: 'yes', 6: 'no'}, 'coke': {0: 'no', 1: 'no', 2: 'yes', 3: 'no', 4: 'yes', 5: 'no', 6: 'yes'}, 'diaper': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}})
        target = ("diaper", "yes")
        bsd = CPBSD(min_support=0,quality_measure=WRAcc(),optimistic_estimate = WRAccOptimisticEstimate1(), num_subgroups=8,max_depth=100 , write_results_in_file = True, file_path = "./results.txt" )
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 8)
        file_to_read = open("./results.txt", "r")
        list_of_written_results = []
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [bread = 'yes', beer = 'yes', coke = 'no', milk = 'no'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes', bread = 'no', coke = 'yes', milk = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'no', bread = 'yes', coke = 'yes', milk = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes', bread = 'yes', coke = 'no', milk = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes', milk = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [coke = 'yes', milk = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes', bread = 'yes', coke = 'no'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")
    