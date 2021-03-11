# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'algorithms/sdmap.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.sdmap import SDMap
from subgroups.quality_measures.wracc import WRAcc
from subgroups.exceptions import ParametersError, AttributeTypeError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.core.subgroup import Pattern, Subgroup

def test_SDMap_init_method():
    try:
        SDMap("hello", 0.85)
        assert (False)
    except TypeError:
        assert (True)
    try:
        SDMap(WRAcc(), "hello")
        assert (False)
    except TypeError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_tp=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_fp=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_n=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_fp=0, minimum_n=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0, minimum_n=0)
        assert (False)
    except ParametersError:
        assert (True)

def test_SDMap_fpgrowth_method_1():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    minimum_n = 0
    fp_tree = FPTreeForSDMap()
    frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_n=minimum_n)
    fp_tree.build_tree(df, frequent_selectors_dict, target)
    sdmap = SDMap(WRAcc(), 9999, minimum_n=minimum_n) # In this test, 'quality_measure' and 'minimum_quality_measure_value' are not used.
    patterns = sdmap._fpgrowth(fp_tree, None)
    assert (len(patterns) == 25)
    assert ( (Pattern.generate_from_str("[a1 = a]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = a, a2 = q]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = a, a3 = f]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = a, a3 = f, a2 = q]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b, a3 = g]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b, a3 = g, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = c]"), [1,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = c, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = q]"), [2,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = s]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = s, a1 = c]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = s, a3 = h]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = s, a3 = h, a1 = c]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = f]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = f, a2 = q]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = g]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = g, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = h]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = h, a1 = c]"), [0,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k, a1 = c]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k, a1 = c, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k, a2 = q]"), [1,0]) in patterns )

def test_SDMap_fpgrowth_method_2():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    minimum_n = 2
    fp_tree = FPTreeForSDMap()
    frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_n=minimum_n)
    fp_tree.build_tree(df, frequent_selectors_dict, target)
    sdmap = SDMap(WRAcc(), 9999, minimum_n=minimum_n) # In this test, 'quality_measure' and 'minimum_quality_measure_value' are not used.
    patterns = sdmap._fpgrowth(fp_tree, None)
    assert (len(patterns) == 2)
    assert ( (Pattern.generate_from_str("[a1 = c]"), [1,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = q]"), [2,1]) in patterns )

def test_SDMap_fpgrowth_method_3():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    minimum_tp = 1
    minimum_fp = 1
    fp_tree = FPTreeForSDMap()
    frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_tp=minimum_tp, minimum_fp=minimum_fp)
    fp_tree.build_tree(df, frequent_selectors_dict, target)
    sdmap = SDMap(WRAcc(), 9999, minimum_tp=minimum_tp, minimum_fp=minimum_fp) # In this test, 'quality_measure' and 'minimum_quality_measure_value' are not used.
    patterns = sdmap._fpgrowth(fp_tree, None)
    assert (len(patterns) == 2)
    assert ( (Pattern.generate_from_str("[a1 = c]"), [1,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = q]"), [2,1]) in patterns )

def test_SDMap_fpgrowth_method_4():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    minimum_tp = 1
    minimum_fp = 0
    fp_tree = FPTreeForSDMap()
    frequent_selectors_dict = fp_tree.generate_set_of_frequent_selectors(df, target, minimum_tp=minimum_tp, minimum_fp=minimum_fp)
    fp_tree.build_tree(df, frequent_selectors_dict, target)
    sdmap = SDMap(WRAcc(), 9999, minimum_tp=minimum_tp, minimum_fp=minimum_fp) # In this test, 'quality_measure' and 'minimum_quality_measure_value' are not used.
    patterns = sdmap._fpgrowth(fp_tree, None)
    assert (len(patterns) == 13)
    assert ( (Pattern.generate_from_str("[a1 = b]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b, a3 = g]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = b, a3 = g, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = c]"), [1,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a1 = c, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a2 = q]"), [2,1]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = g]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = g, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k, a1 = c]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k, a1 = c, a2 = q]"), [1,0]) in patterns )
    assert ( (Pattern.generate_from_str("[a3 = k, a2 = q]"), [1,0]) in patterns )

def test_SDMap_fit_method_1():
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", 0))
        assert (False)
    except AttributeTypeError:
        assert (True)
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", "0"))
        assert (False)
    except AttributeTypeError:
        assert (True)
    try:
        df = DataFrame({"att1" : [4,5,2,6], "class" : ["0","1","2","2"]}) # All the attributes must be nominal (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", "0"))
        assert (False)
    except AttributeTypeError:
        assert (True)

def test_SDMap_fit_method_2():
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

def test_SDMap_fit_method_3():
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

def test_SDMap_fit_method_4():
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

def test_SDMap_fit_method_5():
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

def test_SDMap_fit_method_6():
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

def test_SDMap_fit_method_7():
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

def test_SDMap_fit_method_8():
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