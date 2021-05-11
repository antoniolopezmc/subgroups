# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'data_structures/vertical_list.py'.
"""

from subgroups.data_structures.vertical_list import VerticalList
from bitarray import bitarray
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from pandas import DataFrame
from subgroups.quality_measures.support import Support
from subgroups.quality_measures.coverage import Coverage

def test_vertical_list_1():
    df = DataFrame({"at1" : ["a", "b", "c"], "at2" : ["b", "b", "z"], "at3" : ["a", "c", "c"], "target" : ["yes", "no", "no"]})
    target = ("target", "yes")
    TP = 1
    FP = 2
    vl_1 = VerticalList([Selector("at1", Operator.EQUAL, "a")], [0], [], 3, -45)
    vl_2 = VerticalList([Selector("at2", Operator.EQUAL, "b")], [0], [1], 3, -45)
    vl_3 = VerticalList([Selector("at2", Operator.EQUAL, "z")], [], [2], 3, -45)
    vl_4 = VerticalList([Selector("at3", Operator.EQUAL, "c")], [], [1,2], 3, -45)
    assert (vl_1.list_of_selectors == [Selector.generate_from_str("at1 = 'a'")])
    assert (vl_2.list_of_selectors == [Selector.generate_from_str("at2 = b")])
    assert (vl_3.list_of_selectors == [Selector.generate_from_str("at2 = 'z'")])
    assert (vl_4.list_of_selectors == [Selector.generate_from_str("at3 = 'c'")])
    assert ( vl_1.sequence_of_instances_tp == bitarray("100", endian="big") )
    assert ( vl_2.sequence_of_instances_tp == bitarray("100", endian="big") )
    assert ( vl_3.sequence_of_instances_tp == bitarray("000", endian="big") )
    assert ( vl_4.sequence_of_instances_tp == bitarray("000", endian="big") )
    assert ( vl_1.sequence_of_instances_fp == bitarray("000", endian="big") )
    assert ( vl_2.sequence_of_instances_fp == bitarray("010", endian="big") )
    assert ( vl_3.sequence_of_instances_fp == bitarray("001", endian="big") )
    assert ( vl_4.sequence_of_instances_fp == bitarray("011", endian="big") )
    assert (vl_1.tp == 1)
    assert (vl_2.tp == 1)
    assert (vl_3.tp == 0)
    assert (vl_4.tp == 0)
    assert (vl_1.fp == 0)
    assert (vl_2.fp == 1)
    assert (vl_3.fp == 1)
    assert (vl_4.fp == 2)
    assert (vl_1.n == 1)
    assert (vl_2.n == 2)
    assert (vl_3.n == 1)
    assert (vl_4.n == 2)
    assert (vl_1.quality_value == -45)
    assert (vl_2.quality_value == -45)
    assert (vl_3.quality_value == -45)
    assert (vl_4.quality_value == -45)
    assert (vl_1.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}) == 1/3) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (vl_2.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}) == 1/3) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (vl_3.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}) == 0) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (vl_4.compute_quality_value(Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}) == 0) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    union_1 = vl_3.union(vl_4, Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (union_1.list_of_selectors == [Selector("at2", Operator.EQUAL, "z"), Selector("at3", Operator.EQUAL, "c")])
    assert ( union_1.sequence_of_instances_tp == bitarray("000", endian="big") )
    assert ( union_1.sequence_of_instances_fp == bitarray("001", endian="big") )
    assert (union_1.tp == 0)
    assert (union_1.fp == 1)
    assert (union_1.n == 1)
    assert (union_1.quality_value == 0)
    union_2 = vl_1.union(union_1, Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (union_2.list_of_selectors == [Selector("at1", Operator.EQUAL, "a"), Selector("at3", Operator.EQUAL, "c")])
    assert ( union_2.sequence_of_instances_tp == bitarray("000", endian="big") )
    assert ( union_2.sequence_of_instances_fp == bitarray("000", endian="big") )
    assert (union_2.tp == 0)
    assert (union_2.fp == 0)
    assert (union_2.n == 0)
    assert (union_2.quality_value == 0)
    union_3 = union_1.union(union_2, Support(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (union_3.list_of_selectors == [Selector("at2", Operator.EQUAL, "z"), Selector("at3", Operator.EQUAL, "c"), Selector("at3", Operator.EQUAL, "c")])
    assert ( union_3.sequence_of_instances_tp == bitarray("000", endian="big") )
    assert ( union_3.sequence_of_instances_fp == bitarray("000", endian="big") )
    assert (union_3.tp == 0)
    assert (union_3.fp == 0)
    assert (union_3.n == 0)
    assert (union_3.quality_value == 0)
    union_4 = vl_3.union(vl_4, Coverage(), {"tp" : 1000, "fp" : 1000, "TP" : TP, "FP" : FP}, return_None_if_n_is_0 = False) # The parameters "tp" and "fp" of the dictionary of parameters should not be considered in the method.
    assert (union_4.list_of_selectors == [Selector("at2", Operator.EQUAL, "z"), Selector("at3", Operator.EQUAL, "c")])
    assert ( union_4.sequence_of_instances_tp == bitarray("000", endian="big") )
    assert ( union_4.sequence_of_instances_fp == bitarray("001", endian="big") )
    assert (union_4.tp == 0)
    assert (union_4.fp == 1)
    assert (union_4.n == 1)
    assert (union_4.quality_value == (1/3))

def test_vertical_list_2():
    TP = 24
    FP = 26
    vl_1 = VerticalList([Selector("at1", Operator.EQUAL, "a")], [0], [], 50, -45)
    vl_2 = VerticalList([Selector("at2", Operator.EQUAL, "b")], [0], [1], 50, -45)
    vl_3 = VerticalList([Selector("at2", Operator.EQUAL, "z")], [], [2], 50, -45)
    vl_4 = VerticalList([Selector("at3", Operator.EQUAL, "c")], [], [1,2], 50, -45)
    vl_5 = VerticalList([Selector("at4", Operator.EQUAL, "c")], [0,1], [2,3], 50, -45)
    vl_6 = VerticalList([Selector("at5", Operator.EQUAL, "c")], [10,11], [12,33], 50, -45)
    assert (vl_1.union(vl_2, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True) is not None)
    assert (vl_1.union(vl_3, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True) is None)
    assert (vl_2.union(vl_4, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True) is not None)
    assert (vl_3.union(vl_4, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True) is not None)
    assert (vl_5.union(vl_6, Coverage(), {"TP" : TP, "FP" : FP}, return_None_if_n_is_0 = True) is None)

def test_vertical_list_3():
    vl_1 = VerticalList([Selector("at1", Operator.EQUAL, "a")], [0], [], 3, -45) # dataset_size = 3
    vl_2 = VerticalList([Selector("at2", Operator.EQUAL, "b")], [0], [1], 5, -45) # dataset_size = 5
    try:
        # The sequence of instances of the vertical lists do not have the same sizes.
        union_1 = vl_1.union(vl_2, Coverage(), {"TP" : 5, "FP" : 5})
        assert(False)
    except ValueError:
        assert(True)

def test_vertical_list_str_method():
    vl_1 = VerticalList([Selector("at1", Operator.EQUAL, "a")], [], [], 4, 20)
    vl_2 = VerticalList([Selector("at2", Operator.EQUAL, "b"), Selector("at3", Operator.NOT_EQUAL, "c")], [0,1], [], 4, -45)
    vl_3 = VerticalList([Selector("at2", Operator.EQUAL, "b")], [1], [], 4, 100)
    vl_4 = VerticalList([Selector("at2", Operator.EQUAL, "z")], [], [2], 4, 0)
    vl_5 = VerticalList([], [], [1,2], 4, 1)
    vl_6 = VerticalList([Selector("at1", Operator.EQUAL, "a"), Selector("at2", Operator.EQUAL, "b"), Selector("at3", Operator.NOT_EQUAL, "c")], [1], [0,3], 4, 5)
    assert (str(vl_1) == "List of selectors: [at1 = 'a'], Sequence of instances (tp): [], Sequence of instances (fp): [], Quality value: 20")
    assert (str(vl_2) == "List of selectors: [" + str(Selector("at2", Operator.EQUAL, "b")) + ", " + str(Selector("at3", Operator.NOT_EQUAL, "c")) + "], Sequence of instances (tp): [0, 1], Sequence of instances (fp): [], Quality value: -45")
    assert (str(vl_3) == "List of selectors: [" + str(Selector("at2", Operator.EQUAL, "b")) + "], Sequence of instances (tp): [1], Sequence of instances (fp): [], Quality value: 100")
    assert (str(vl_4) == "List of selectors: [" + str(Selector("at2", Operator.EQUAL, "z")) + "], Sequence of instances (tp): [], Sequence of instances (fp): [2], Quality value: 0")
    assert (str(vl_5) == "List of selectors: [], Sequence of instances (tp): [], Sequence of instances (fp): [1, 2], Quality value: 1")
    assert (str(vl_6) == "List of selectors: [" + str(Selector("at1", Operator.EQUAL, "a")) + ", " + str(Selector("at2", Operator.EQUAL, "b")) + ", " + str(Selector("at3", Operator.NOT_EQUAL, "c")) + "], Sequence of instances (tp): [1], Sequence of instances (fp): [0, 3], Quality value: 5")
