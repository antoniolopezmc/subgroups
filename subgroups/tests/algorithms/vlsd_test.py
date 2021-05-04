# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'algorithms/vlsd.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.vlsd import VLSD
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_upper_bound_1 import WRAccUpperBound1
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError, ParameterNotFoundError, SubgroupParameterNotFoundError
from subgroups.data_structures.vertical_list import VerticalList
from subgroups.core.pattern import Pattern
from subgroups.core.subgroup import Subgroup

def test_VLSD_init_method():
    dictionary = dict()
    vlsd = VLSD(WRAcc(), WRAccUpperBound1(), -1, additional_parameters_for_the_quality_measure=dictionary, additional_parameters_for_the_upper_bound=dictionary)
    assert (len(vlsd.additional_parameters_for_the_quality_measure) == 0)
    assert (len(vlsd.additional_parameters_for_the_upper_bound) == 0)
    assert (vlsd.additional_parameters_for_the_quality_measure == dictionary)
    assert (vlsd.additional_parameters_for_the_upper_bound == dictionary)
    assert (vlsd.additional_parameters_for_the_quality_measure == vlsd.additional_parameters_for_the_upper_bound)
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_upper_bound) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(vlsd.additional_parameters_for_the_upper_bound))
    dictionary = dict({"g" : 0.5})
    vlsd = VLSD(WRAcc(), WRAccUpperBound1(), -1, additional_parameters_for_the_quality_measure=dictionary, additional_parameters_for_the_upper_bound=dictionary)
    assert (len(vlsd.additional_parameters_for_the_quality_measure) == 1)
    assert (len(vlsd.additional_parameters_for_the_upper_bound) == 1)
    assert (vlsd.additional_parameters_for_the_quality_measure == dictionary)
    assert (vlsd.additional_parameters_for_the_upper_bound == dictionary)
    assert (vlsd.additional_parameters_for_the_quality_measure == vlsd.additional_parameters_for_the_upper_bound)
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_upper_bound) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(vlsd.additional_parameters_for_the_upper_bound))
    assert (vlsd.additional_parameters_for_the_quality_measure["g"] == 0.5)
    assert (vlsd.additional_parameters_for_the_upper_bound["g"] == 0.5)
    vlsd.additional_parameters_for_the_upper_bound["g"] = 0.1
    assert (vlsd.additional_parameters_for_the_quality_measure != vlsd.additional_parameters_for_the_upper_bound)
    assert (vlsd.additional_parameters_for_the_quality_measure["g"] == 0.5)
    assert (vlsd.additional_parameters_for_the_upper_bound["g"] == 0.1)















def test_VLSD_fit_method_1():
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", 0))
        assert (False)
    except DatasetAttributeTypeError:
        assert (True)
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", "0"))
        assert (False)
    except DatasetAttributeTypeError:
        assert (True)
    try:
        df = DataFrame({"att1" : [4,5,2,6], "class" : ["0","1","2","2"]}) # All the attributes must be nominal (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", "0"))
        assert (False)
    except DatasetAttributeTypeError:
        assert (True)

def test_VLSD_fit_method_2():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), -1, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 25)
    assert ( (Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), 0.0) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'"), -0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_3():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), -1, minimum_n=2) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 2)
    assert ( (Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), 0.0) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_4():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), -1, minimum_tp=1, minimum_fp=1) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 2)
    assert ( (Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), 0.0) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_5():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), -1, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 13)
    assert ( (Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), 0.0) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_6():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), 0, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 13)
    assert ( (Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), 0.0) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_7():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), 0.1, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 12)
    assert ( (Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_8():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), 0.1, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 12)
    assert ( (Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_9():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), -1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"TP" : 100000, "g" : 0.5}) # IMPORTANT: the subgroup parameter TP must be deleted in the __init__ method.
    assert (len(sdmap.additional_parameters_for_the_quality_measure) == 1)
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 2)
    assert ( (Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'"), 0.0) in subgroups_qmvalue_round3 )
    assert ( (Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'"), 0.125) in subgroups_qmvalue_round3 )

def test_VLSD_fit_method_10():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(Qg(), -1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"TP" : 100000}) # IMPORTANT: the subgroup parameter TP must be deleted in the __init__ method.
    try:
        subgroups = sdmap.fit(df, target)
        assert (False)
    except ParameterNotFoundError:
        assert (True)

def test_VLSD_fit_method_11():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(Qg(), -1, minimum_tp=1, minimum_fp=1, additional_parameters_for_the_quality_measure={"TP" : 100000, "g" : 0.5}) # IMPORTANT: the subgroup parameter TP must be deleted in the __init__ method.
    subgroups = sdmap.fit(df, target)
    subgroups_qmvalue_round3 = []
    for elem in subgroups:
        subgroups_qmvalue_round3.append( (elem[0],round(elem[1], 3)) )
    assert (len(subgroups) == 2)

def test_VLSD_visited_and_pruned_nodes():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), -1, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 25)
    assert (sdmap.pruned_nodes == 0)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), -1, minimum_n=2) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 2)
    assert (sdmap.pruned_nodes == 0)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), -1, minimum_tp=1, minimum_fp=1) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 2)
    assert (sdmap.pruned_nodes == 0)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), -1, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 13)
    assert (sdmap.pruned_nodes == 0)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), 0, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 13)
    assert (sdmap.pruned_nodes == 0)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), 0.1, minimum_tp=1, minimum_fp=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 12)
    assert (sdmap.pruned_nodes == 1)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), 0.1, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 12)
    assert (sdmap.pruned_nodes == 13)
    # ---------------------------------------
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), 0.2, minimum_n=2) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 2)
    # ---------------------------------------
    sdmap = SDMap(WRAcc(), 0.2, minimum_n=0) # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 0)
    subgroups = sdmap.fit(df, target)
    assert (sdmap.visited_nodes == 0)
    assert (sdmap.pruned_nodes == 25)
