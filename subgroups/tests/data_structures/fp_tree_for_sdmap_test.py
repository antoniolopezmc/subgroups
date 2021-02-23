# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'data_structures/fp_tree_for_sdmap.py'.
"""

import pandas as pd
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
import string
import random
from numpy import concatenate, quantile

def test_FPTreeForSDMap_generate_set_of_frequent_selectors():
    random.seed(123)
    n_rows = 500
    attribute_names = ["att1", "att2", "att3", "att4", "att5"]
    values = ["value1", "value2", "value3", "value4", "value5", "value6"]
    df = pd.DataFrame()
    for att_name in attribute_names:
        df[att_name] = [random.choice(values) for _ in range(n_rows)]
    df["target"] = [random.choice(["Y","N"]) for _ in range(n_rows)]
    fp_tree_for_sdmap = FPTreeForSDMap()
    assert (fp_tree_for_sdmap.is_empty())
    assert (fp_tree_for_sdmap.there_is_a_single_path())
    assert (fp_tree_for_sdmap.root_node.selector == Selector("None", Operator.EQUAL, "None"))
    assert (fp_tree_for_sdmap.root_node.number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node.counters[0] == -1)
    assert (fp_tree_for_sdmap.root_node.counters[1] == -1)
    assert (fp_tree_for_sdmap.root_node.parent is None)
    assert (fp_tree_for_sdmap.root_node.node_link is None)
    assert (fp_tree_for_sdmap.header_table == dict())
    assert (fp_tree_for_sdmap.sorted_header_table == [])
    target = ("target", "Y")
    # Set of frequent selectors without thresholds.
    minimum_tp = 0
    minimum_fp = 0
    set_of_frequent_selectors_1 = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, minimum_tp, minimum_fp)
    test_set_of_frequent_selectors_1 = dict() # We generate the dict by hand in order to compare it with 'set_of_frequent_selectors_1'.
    for row in df.itertuples(index=False):
        if row.target == target[1]:
            column_index = 0
            for att_name in attribute_names:
                try:
                    test_set_of_frequent_selectors_1[att_name+repr(row[column_index])][1][0] = \
                        test_set_of_frequent_selectors_1[att_name+repr(row[column_index])][1][0] + 1
                except KeyError:
                    test_set_of_frequent_selectors_1[att_name+repr(row[column_index])] = [Selector(att_name, Operator.EQUAL, row[column_index]), [1, 0]]
                column_index = column_index + 1
        else:
            column_index = 0
            for att_name in attribute_names:
                try:
                    test_set_of_frequent_selectors_1[att_name+repr(row[column_index])][1][1] = \
                        test_set_of_frequent_selectors_1[att_name+repr(row[column_index])][1][1] + 1
                except KeyError:
                    test_set_of_frequent_selectors_1[att_name+repr(row[column_index])] = [Selector(att_name, Operator.EQUAL, row[column_index]), [0, 1]]
                column_index = column_index + 1
    assert (len(set_of_frequent_selectors_1) == len(test_set_of_frequent_selectors_1))
    for key in set_of_frequent_selectors_1:
        assert (set_of_frequent_selectors_1[key][0] == test_set_of_frequent_selectors_1[key][0])
        assert (set_of_frequent_selectors_1[key][1][0] == test_set_of_frequent_selectors_1[key][1][0])
        assert (set_of_frequent_selectors_1[key][1][1] == test_set_of_frequent_selectors_1[key][1][1])
    # Set of frequent selectors with thresholds.
    minimum_tp = int( quantile(concatenate([df[column].value_counts().values for column in df]), 0.5) / 2 )
    minimum_fp = int( quantile(concatenate([df[column].value_counts().values for column in df]), 0.7) / 2 )
    set_of_frequent_selectors_2 = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, minimum_tp, minimum_fp)
    test_set_of_frequent_selectors_2 = dict() # We generate the dict by hand in order to compare it with 'set_of_frequent_selectors_2'.
    for row in df.itertuples(index=False):
        if row.target == target[1]:
            column_index = 0
            for att_name in attribute_names:
                try:
                    test_set_of_frequent_selectors_2[att_name+repr(row[column_index])][1][0] = \
                        test_set_of_frequent_selectors_2[att_name+repr(row[column_index])][1][0] + 1
                except KeyError:
                    test_set_of_frequent_selectors_2[att_name+repr(row[column_index])] = [Selector(att_name, Operator.EQUAL, row[column_index]), [1, 0]]
                column_index = column_index + 1
        else:
            column_index = 0
            for att_name in attribute_names:
                try:
                    test_set_of_frequent_selectors_2[att_name+repr(row[column_index])][1][1] = \
                        test_set_of_frequent_selectors_2[att_name+repr(row[column_index])][1][1] + 1
                except KeyError:
                    test_set_of_frequent_selectors_2[att_name+repr(row[column_index])] = [Selector(att_name, Operator.EQUAL, row[column_index]), [0, 1]]
                column_index = column_index + 1
    final_result = dict()
    for key in test_set_of_frequent_selectors_2:
        if (test_set_of_frequent_selectors_2[key][1][0] >= minimum_tp) and (test_set_of_frequent_selectors_2[key][1][1] >= minimum_fp):
            final_result[key] = test_set_of_frequent_selectors_2[key]
    assert (len(set_of_frequent_selectors_2) == len(final_result))
    for key in set_of_frequent_selectors_2:
        assert (set_of_frequent_selectors_2[key][0] == final_result[key][0])
        assert (set_of_frequent_selectors_2[key][1][0] == final_result[key][1][0])
        assert (set_of_frequent_selectors_2[key][1][1] == final_result[key][1][1])

def test_FPTreeForSDMap_build_tree_1():
    random.seed(789)
    n_rows = 500
    attribute_names = ["att1", "att2", "att3", "att4", "att5"]
    values = ["value1", "value2", "value3", "value4", "value5", "value6"]
    df = pd.DataFrame()
    for att_name in attribute_names:
        df[att_name] = [random.choice(values) for _ in range(n_rows)]
    df["target"] = [random.choice(["Y","N"]) for _ in range(n_rows)]
    fp_tree_for_sdmap = FPTreeForSDMap()
    target = ("target", "N")
    minimum_tp = int( quantile(concatenate([df[column].value_counts().values for column in df]), 0.5) / 2 )
    minimum_fp = int( quantile(concatenate([df[column].value_counts().values for column in df]), 0.7) / 2 )
    set_of_frequent_selectors = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, minimum_tp, minimum_fp)
    fp_tree_for_sdmap.build_tree(df, set_of_frequent_selectors, target)
    # Test the header table and the sorted header table.
    header_table = fp_tree_for_sdmap.header_table
    assert (len(header_table) == len(set_of_frequent_selectors))
    for sel in header_table:
        assert ((sel.attribute_name+repr(sel.value)) in set_of_frequent_selectors)
        value_of_header_table = header_table[sel] # Tuple.
        assert (value_of_header_table[0][0] == set_of_frequent_selectors[sel.attribute_name+repr(sel.value)][1][0])
        assert (value_of_header_table[0][1] == set_of_frequent_selectors[sel.attribute_name+repr(sel.value)][1][1])
    sorted_header_table = fp_tree_for_sdmap.sorted_header_table # Must be in ascending order.
    header_table_as_list = [x for x in header_table] 
    header_table_as_list.sort(reverse=False, key=lambda x : (set_of_frequent_selectors[x.attribute_name+repr(x.value)][1][0]+set_of_frequent_selectors[x.attribute_name+repr(x.value)][1][1]))
    assert (sorted_header_table == header_table_as_list)
    set_of_frequent_selectors_as_list = [x[0] for x in set_of_frequent_selectors.values()]
    set_of_frequent_selectors_as_list.sort(reverse=False, key=lambda x : (set_of_frequent_selectors[x.attribute_name+repr(x.value)][1][0]+set_of_frequent_selectors[x.attribute_name+repr(x.value)][1][1]))
    assert (sorted_header_table == set_of_frequent_selectors_as_list)
    header_table_as_list = [x for x in header_table]
    header_table_as_list.sort(reverse=False, key=lambda x : (header_table[x][0][0]+header_table[x][0][1]))
    assert (sorted_header_table == header_table_as_list)

def test_FPTreeForSDMap_build_tree_2():
    df = pd.DataFrame({"a1" : ["v1", "v1", "v2", "v3", "v2", "v4"], "a2" : ["v2", "v3", "v4", "v4", "v3", "v1"],\
                        "a3" : ["v2", "v4", "v1", "v4", "v3", "v2"], "target" : ["y", "y", "n", "y", "n", "n"]})
    fp_tree_for_sdmap = FPTreeForSDMap()
    target = ("target", "y")
    set_of_frequent_selectors = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, 0, 0)
    fp_tree_for_sdmap.build_tree(df, set_of_frequent_selectors, target)
    print(fp_tree_for_sdmap.tree_as_str())
    print(fp_tree_for_sdmap.header_table_as_str())
    # Test the header table.
    # Test the sorted header table.
    #print(fp_tree_for_sdmap._sorted_header_table)
    assert(fp_tree_for_sdmap._sorted_header_table == [Selector.generate_from_str("a1 = v3"), Selector.generate_from_str("a1 = v4"), Selector.generate_from_str("a2 = v1"), \
                                                Selector.generate_from_str("a2 = v2"), Selector.generate_from_str("a3 = v1"), Selector.generate_from_str("a3 = v3"), 
                                                Selector.generate_from_str("a1 = v1"), Selector.generate_from_str("a1 = v2"), Selector.generate_from_str("a2 = v3"), 
                                                Selector.generate_from_str("a2 = v4"), Selector.generate_from_str("a3 = v2"), Selector.generate_from_str("a3 = v4")])
    # Test the complete tree.

