# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/cbsd.py'.
"""

from bitarray import bitarray
from pandas import DataFrame
from subgroups.algorithms.individual_subgroups.nominal_target.cbsd import CBSD
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
import unittest


class TestCBSD(unittest.TestCase):

    def test_CBSD_init_method(self) -> None:
        self.assertRaises(TypeError, CBSD, 0, "hello")
        self.assertRaises(TypeError, CBSD, 0, WRAcc(),"hello")
        self.assertRaises(TypeError, CBSD, 0, WRAcc(),WRAccOptimisticEstimate1(),"hello")
        self.assertRaises(TypeError, CBSD, 0, WRAcc(),WRAccOptimisticEstimate1(),1,"hello")
        CBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        CBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False,file_path="./asdasfha/fsdvm") # Path does not exist, but it is not checked
        self.assertRaises(TypeError, CBSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=True, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(TypeError, CBSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=False, file_path=24) # If 'file_path' is present, it must be of type str, no matter the flag.
        self.assertRaises(ValueError, CBSD, 0 , WRAcc(), WRAccOptimisticEstimate1(), 5,10, write_results_in_file=True, file_path=None) # If 'write_results_in_file' is True, 'file_path' must not be None.

    def test_CBSD_checkRel(self) -> None:
        bsd = CBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110000"))]
        self.assertFalse(bsd._checkRel(res,bitarray("110"),bitarray("000"),0.,Pattern([])))
        self.assertTrue(bsd._checkRel(res,bitarray("110"),bitarray("010"),0.,Pattern([])))
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110010"))]
        self.assertFalse(bsd._checkRel(res,bitarray("110"),bitarray("010"),0.,Pattern([])))
        self.assertFalse(bsd._checkRel(res,bitarray("100"),bitarray("010"),0.,Pattern([])))
        self.assertTrue(bsd._checkRel(res,bitarray("100"),bitarray("011"),0.,Pattern([])))
        
    def test_CBSD_checkRelevancies(self) -> None:
        bsd = CBSD(0, WRAcc(),WRAccOptimisticEstimate1(),5,10,write_results_in_file=False)
        res = [(0,Pattern([Selector("att1",Operator.EQUAL,"A")]),bitarray("110000")),(0,Pattern([Selector("att1",Operator.EQUAL,"B")]),bitarray("110000"))]
        bsd._k_subgroups = res
        bsd._checkRelevancies(bitarray("110000"),Pattern([Selector("att1",Operator.EQUAL,"A")]),0.1)
        self.assertEqual(bsd._k_subgroups,res) # The subgroup att1=B has the same bitarray, but it has a different quality
        bsd._checkRelevancies(bitarray("110000"),Pattern([Selector("att1",Operator.EQUAL,"A")]),0.)
        self.assertNotEqual(bsd._k_subgroups,res) # The subgroup att1=B is irrelevant

    
        