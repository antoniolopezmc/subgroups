# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/bsd.py'.
"""

from bitarray import bitarray
from pandas import DataFrame
from subgroups.algorithms.individual_subgroups.nominal_target.bsd import BSD
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
from subgroups.quality_measures.qg import Qg
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError, ParameterNotFoundError
from subgroups.data_structures.bitset_bsd import BitsetDictionary, BitsetBSD
from subgroups.core.subgroup import Subgroup
from os import remove
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
        self.assertEqual(bsd.unselected_subgroups, 50)
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
        
    def test_BSD_fit2(self) -> None:
        df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
        target = ("class", "y")
        # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
        bsd = BSD(200, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        bsd.fit(df, target)
        self.assertEqual(bsd.selected_subgroups, 0)
        self.assertEqual(bsd.unselected_subgroups, 0)
        self.assertEqual(bsd.visited_subgroups, 0)
        
unittest.main()