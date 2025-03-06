# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles <fmora@um.es>

"""Tests of the functionality contained in the file 'algorithms/bsd.py'.
"""

from os import remove
from bitarray import bitarray
from pandas import DataFrame
from subgroups.algorithms.subgroup_sets.bsd import BSD
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
import unittest


class TestBSD(unittest.TestCase):

    def test_BSD_init_method(self) -> None:
        self.assertRaises(TypeError, BSD, 0, "hello")
        self.assertRaises(TypeError, BSD, 0, WRAcc(),"hello")
        self.assertRaises(TypeError, BSD, 0, WRAcc(),WRAccOptimisticEstimate1(),"hello")
        self.assertRaises(TypeError, BSD, 0, WRAcc(),WRAccOptimisticEstimate1(),1,"hello")
        BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False,file_path="./asdasfha/fsdvm") # Path does not exist, but it is not checked
        self.assertRaises(TypeError, BSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=True, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(TypeError, BSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=False, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(ValueError, BSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=True, file_path=None) # If 'write_results_in_file' is True, 'file_path' must not be None.

    def test_BSD_checkRel(self) -> None:
        bsd = BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110000"))]
        self.assertFalse(bsd._checkRel(res,bitarray("100"),bitarray("000"),0.,Pattern([])))
        self.assertFalse(bsd._checkRel(res,bitarray("100"),bitarray("010"),0.,Pattern([])))
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110010"))]
        self.assertTrue(bsd._checkRel(res,bitarray("100"),bitarray("000"),0.,Pattern([])))
        self.assertFalse(bsd._checkRel(res,bitarray("100"),bitarray("010"),0.,Pattern([])))
        
    def test_BSD_checkRelevancies(self) -> None:
        bsd = BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110000")),(0,Pattern([Selector("att1",Operator.EQUAL,"B")]),bitarray("100000"))]
        bsd._k_subgroups = res
        bsd._checkRelevancies(bitarray("100"),bitarray("000"),Pattern([Selector("att1",Operator.EQUAL,"B")]))
        self.assertEqual(bsd._k_subgroups,res) # The subgroup att1=B is irrelevant, but is not checked
        bsd._checkRelevancies(bitarray("110"),bitarray("000"),Pattern([Selector("att1",Operator.EQUAL,"A")]))
        self.assertNotEqual(bsd._k_subgroups,res) # The subgroup att1=B is irrelevant, and is checked

    def test_BSD_cardinality(self) -> None:
        bsd = BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        ba = bitarray("110000")
        self.assertEqual(bsd._cardinality(ba),2)
        ba = bitarray("110010")
        self.assertEqual(bsd._cardinality(ba),3)
        ba = bitarray("000000")
        self.assertEqual(bsd._cardinality(ba),0)
    
    def test_BSD_logicalAnd(self) -> None:
        bsd = BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        ba1 = bitarray("110000")
        ba2 = bitarray("100000")
        self.assertEqual(bsd._logicalAnd(ba1,ba2),bitarray("100000"))
        ba1 = bitarray("110010")
        ba2 = bitarray("000001")
        self.assertEqual(bsd._logicalAnd(ba1,ba2),bitarray("000000"))
    
    def test_BSD_fit1(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = BSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 3)
        self.assertEqual(bsd.unselected_subgroups, 58)
        self.assertEqual(bsd.visited_subgroups, 21)
        
    def test_BSD_fit2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = BSD(0, WRAcc(),WRAccOptimisticEstimate1(),2,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 2)
        self.assertEqual(bsd.unselected_subgroups, 23)
        self.assertEqual(bsd.visited_subgroups, 17)
        
    def test_BSD_fit3(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = BSD(200, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 0)
        self.assertEqual(bsd.unselected_subgroups, 0)
        self.assertEqual(bsd.visited_subgroups, 0)
    
    def test_BSD_fit4(self) -> None:
        df = DataFrame({'bread': {0: 'yes', 1: 'yes', 2: 'no', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'milk': {0: 'yes', 1: 'no', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}, 'beer': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'no', 5: 'yes', 6: 'no'}, 'coke': {0: 'no', 1: 'no', 2: 'yes', 3: 'no', 4: 'yes', 5: 'no', 6: 'yes'}, 'diaper': {0: 'no', 1: 'yes', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes', 6: 'yes'}})
        target = ("diaper", "yes")
        bsd = BSD(min_support=0,quality_measure=WRAcc(),optimistic_estimate = WRAccOptimisticEstimate1(), num_subgroups=8,max_depth=100 , write_results_in_file = True, file_path = "./results.txt" )
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 4)
        file_to_read = open("./results.txt", "r")
        list_of_written_results = []
        for line in file_to_read:
            list_of_written_results.append(line)
        list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
        self.assertIn(Subgroup.generate_from_str("Description: [bread = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [milk = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [coke = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        self.assertIn(Subgroup.generate_from_str("Description: [beer = 'yes'], Target: diaper = 'yes'"), list_of_subgroups)
        file_to_read.close()
        remove("./results.txt")