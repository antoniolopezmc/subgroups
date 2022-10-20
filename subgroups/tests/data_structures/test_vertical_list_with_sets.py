# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'data_structures/vertical_list.py'.
"""

from subgroups.data_structures.vertical_list_with_sets import VerticalListWithSets
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from pandas import DataFrame
from subgroups.quality_measures.support import Support
from subgroups.quality_measures.coverage import Coverage
from subgroups.exceptions import VerticalListSizeError
import unittest

class TestVerticalListWithSets(unittest.TestCase):

    def test_vertical_list_1(self) -> None:
        df = DataFrame({"at1" : ["a", "b", "c"], "at2" : ["b", "b", "z"], "at3" : ["a", "c", "c"], "target" : ["yes", "no", "no"]})
        target = ("target", "yes")
        TP = 1
        FP = 2
        vl_1 = VerticalListWithSets([Selector("at1", Operator.EQUAL, "a")], [0], [], 3, -45)
        vl_2 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "b")], [0], [1], 3, -45)
        vl_3 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "z")], [], [2], 3, -45)
        vl_4 = VerticalListWithSets([Selector("at3", Operator.EQUAL, "c")], [], [1,2], 3, -45)
        self.assertEqual(vl_1.list_of_selectors, [Selector.generate_from_str("at1 = 'a'")])
        self.assertEqual(vl_2.list_of_selectors, [Selector.generate_from_str("at2 = b")])
        self.assertEqual(vl_3.list_of_selectors, [Selector.generate_from_str("at2 = 'z'")])
        self.assertEqual(vl_4.list_of_selectors, [Selector.generate_from_str("at3 = 'c'")])
        self.assertEqual( vl_1.sequence_of_instances_tp, set([0]) )
        self.assertEqual( vl_2.sequence_of_instances_tp, set([0]) )
        self.assertEqual( vl_3.sequence_of_instances_tp, set([]) )
        self.assertEqual( vl_4.sequence_of_instances_tp, set([]) )
        self.assertEqual( vl_1.sequence_of_instances_fp, set([]) )
        self.assertEqual( vl_2.sequence_of_instances_fp, set([1]) )
        self.assertEqual( vl_3.sequence_of_instances_fp, set([2]) )
        self.assertEqual( vl_4.sequence_of_instances_fp, set([2,1]) )
        self.assertEqual( vl_4.sequence_of_instances_fp, set([1,2]) )
        self.assertEqual(vl_1.tp, 1)
        self.assertEqual(vl_2.tp, 1)
        self.assertEqual(vl_3.tp, 0)
        self.assertEqual(vl_4.tp, 0)
        self.assertEqual(vl_1.fp, 0)
        self.assertEqual(vl_2.fp, 1)
        self.assertEqual(vl_3.fp, 1)
        self.assertEqual(vl_4.fp, 2)
        self.assertEqual(vl_1.n, 1)
        self.assertEqual(vl_2.n, 2)
        self.assertEqual(vl_3.n, 1)
        self.assertEqual(vl_4.n, 2)
        self.assertEqual(vl_1.quality_value, -45)
        self.assertEqual(vl_2.quality_value, -45)
        self.assertEqual(vl_3.quality_value, -45)
        self.assertEqual(vl_4.quality_value, -45)
        self.assertEqual(vl_1.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}), 1/3) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(vl_2.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}), 1/3) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(vl_3.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}), 0) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(vl_4.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}), 0) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        join_1 = vl_3.join(vl_4, Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(join_1.list_of_selectors, [Selector("at2", Operator.EQUAL, "z"), Selector("at3", Operator.EQUAL, "c")])
        self.assertEqual( join_1.sequence_of_instances_tp, set([]) )
        self.assertEqual( join_1.sequence_of_instances_fp, set([2]) )
        self.assertEqual(join_1.tp, 0)
        self.assertEqual(join_1.fp, 1)
        self.assertEqual(join_1.n, 1)
        self.assertEqual(join_1.quality_value, 0)
        join_2 = vl_1.join(join_1, Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(join_2.list_of_selectors, [Selector("at1", Operator.EQUAL, "a"), Selector("at3", Operator.EQUAL, "c")])
        self.assertEqual( join_2.sequence_of_instances_tp, set([]) )
        self.assertEqual( join_2.sequence_of_instances_fp, set([]) )
        self.assertEqual(join_2.tp, 0)
        self.assertEqual(join_2.fp, 0)
        self.assertEqual(join_2.n, 0)
        self.assertEqual(join_2.quality_value, 0)
        join_3 = join_1.join(join_2, Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(join_3.list_of_selectors, [Selector("at2", Operator.EQUAL, "z"), Selector("at3", Operator.EQUAL, "c"), Selector("at3", Operator.EQUAL, "c")])
        self.assertEqual( join_3.sequence_of_instances_tp, set([]) )
        self.assertEqual( join_3.sequence_of_instances_fp, set([]) )
        self.assertEqual(join_3.tp, 0)
        self.assertEqual(join_3.fp, 0)
        self.assertEqual(join_3.n, 0)
        self.assertEqual(join_3.quality_value, 0)
        join_4 = vl_3.join(vl_4, Coverage(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
        self.assertEqual(join_4.list_of_selectors, [Selector("at2", Operator.EQUAL, "z"), Selector("at3", Operator.EQUAL, "c")])
        self.assertEqual( join_4.sequence_of_instances_tp, set([]) )
        self.assertEqual( join_4.sequence_of_instances_fp, set([2]) )
        self.assertEqual(join_4.tp, 0)
        self.assertEqual(join_4.fp, 1)
        self.assertEqual(join_4.n, 1)
        self.assertEqual(join_4.quality_value, (1/3))

    def test_vertical_list_2(self) -> None:
        TP = 24
        FP = 26
        vl_1 = VerticalListWithSets([Selector("at1", Operator.EQUAL, "a")], [0], [], 50, -45)
        vl_2 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "b")], [0], [1], 50, -45)
        vl_3 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "z")], [], [2], 50, -45)
        vl_4 = VerticalListWithSets([Selector("at3", Operator.EQUAL, "c")], [], [1,2], 50, -45)
        vl_5 = VerticalListWithSets([Selector("at4", Operator.EQUAL, "c")], [0,1], [2,3], 50, -45)
        vl_6 = VerticalListWithSets([Selector("at5", Operator.EQUAL, "c")], [10,11], [12,33], 50, -45)
        self.assertIsNotNone(vl_1.join(vl_2, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True))
        self.assertIsNone(vl_1.join(vl_3, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True))
        self.assertIsNotNone(vl_2.join(vl_4, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True))
        self.assertIsNotNone(vl_3.join(vl_4, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True))
        self.assertIsNone(vl_5.join(vl_6, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True))

    def test_vertical_list_3(self) -> None:
        vl_1 = VerticalListWithSets([Selector("at1", Operator.EQUAL, "a")], [0], [], 3, -45) # number_of_dataset_instances = 3
        vl_2 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "b")], [0], [1], 5, -45) # number_of_dataset_instances = 5
        self.assertRaises(VerticalListSizeError, vl_1.join, vl_2, Coverage(), {"TP" : 5, "FP" : 5})

    def test_vertical_list_str_method(self) -> None:
        vl_1 = VerticalListWithSets([Selector("at1", Operator.EQUAL, "a")], [], [], 4, 20)
        vl_2 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "b"), Selector("at3", Operator.NOT_EQUAL, "c")], [0,1], [], 4, -45)
        vl_3 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "b")], [1], [], 4, 100)
        vl_4 = VerticalListWithSets([Selector("at2", Operator.EQUAL, "z")], [], [2], 4, 0)
        vl_5 = VerticalListWithSets([], [], [1,2], 4, 1)
        vl_6 = VerticalListWithSets([Selector("at1", Operator.EQUAL, "a"), Selector("at2", Operator.EQUAL, "b"), Selector("at3", Operator.NOT_EQUAL, "c")], [1], [0,3], 4, 5)
        self.assertEqual(str(vl_1), "List of selectors: [at1 = 'a'], Sequence of instances (tp): [], Sequence of instances (fp): [], Quality value: 20")
        self.assertEqual(str(vl_2), "List of selectors: [" + str(Selector("at2", Operator.EQUAL, "b")) + ", " + str(Selector("at3", Operator.NOT_EQUAL, "c")) + "], Sequence of instances (tp): [0, 1], Sequence of instances (fp): [], Quality value: -45")
        self.assertEqual(str(vl_3), "List of selectors: [" + str(Selector("at2", Operator.EQUAL, "b")) + "], Sequence of instances (tp): [1], Sequence of instances (fp): [], Quality value: 100")
        self.assertEqual(str(vl_4), "List of selectors: [" + str(Selector("at2", Operator.EQUAL, "z")) + "], Sequence of instances (tp): [], Sequence of instances (fp): [2], Quality value: 0")
        self.assertEqual(str(vl_5), "List of selectors: [], Sequence of instances (tp): [], Sequence of instances (fp): [1, 2], Quality value: 1")
        self.assertEqual(str(vl_6), "List of selectors: [" + str(Selector("at1", Operator.EQUAL, "a")) + ", " + str(Selector("at2", Operator.EQUAL, "b")) + ", " + str(Selector("at3", Operator.NOT_EQUAL, "c")) + "], Sequence of instances (tp): [1], Sequence of instances (fp): [0, 3], Quality value: 5")
