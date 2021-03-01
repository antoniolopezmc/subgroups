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
    assert (fp_tree_for_sdmap.is_empty())
    assert (fp_tree_for_sdmap.there_is_a_single_path())
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
                        "a3" : ["v2", "v4", "v1", "v4", "v3", "v2"], "target" : ["Y", "Y", "N", "Y", "N", "N"]})
    fp_tree_for_sdmap = FPTreeForSDMap()
    assert (fp_tree_for_sdmap.is_empty())
    assert (fp_tree_for_sdmap.there_is_a_single_path())
    target = ("target", "Y")
    set_of_frequent_selectors = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, 0, 0)
    assert (set_of_frequent_selectors["a2'v2'"][1] == [1, 0])
    assert (set_of_frequent_selectors["a3'v1'"][1] == [0, 1])
    assert (set_of_frequent_selectors["a1'v3'"][1] == [1, 0])
    assert (set_of_frequent_selectors["a3'v3'"][1] == [0, 1])
    assert (set_of_frequent_selectors["a1'v4'"][1] == [0, 1])
    assert (set_of_frequent_selectors["a2'v1'"][1] == [0, 1])
    assert (set_of_frequent_selectors["a1'v1'"][1] == [2, 0])
    assert (set_of_frequent_selectors["a3'v2'"][1] == [1, 1])
    assert (set_of_frequent_selectors["a2'v3'"][1] == [1, 1])
    assert (set_of_frequent_selectors["a3'v4'"][1] == [2, 0])
    assert (set_of_frequent_selectors["a1'v2'"][1] == [0, 2])
    assert (set_of_frequent_selectors["a2'v4'"][1] == [1, 1])
    fp_tree_for_sdmap.build_tree(df, set_of_frequent_selectors, target)
    assert not (fp_tree_for_sdmap.is_empty())
    assert not (fp_tree_for_sdmap.there_is_a_single_path())
    # Test the header table.
    assert (len(fp_tree_for_sdmap.header_table) == 12)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v2")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v2")][0][1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v1")][0][0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v1")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v3")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v3")][0][1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v3")][0][0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v3")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v4")][0][0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v4")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v1")][0][0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v1")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][0][0] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][0][1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][0][0] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][0][1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v2")][0][0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v2")][0][1] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v2")][1]._selector == Selector.generate_from_str("a2 = v2"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v2")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v2")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v2")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v1")][1]._selector == Selector.generate_from_str("a3 = v1"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v1")][1]._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v1")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v1")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v3")][1]._selector == Selector.generate_from_str("a1 = v3"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v3")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v3")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v3")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v3")][1]._selector == Selector.generate_from_str("a3 = v3"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v3")][1]._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v3")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v3")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v4")][1]._selector == Selector.generate_from_str("a1 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v4")][1]._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v4")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v4")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v1")][1]._selector == Selector.generate_from_str("a2 = v1"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v1")][1]._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v1")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v1")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._selector == Selector.generate_from_str("a1 = v1"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._counters[0] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._selector == Selector.generate_from_str("a3 = v2"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._node_link != None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._node_link._selector == Selector.generate_from_str("a3 = v2"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._node_link._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._node_link._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._node_link._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._selector == Selector.generate_from_str("a2 = v3"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._node_link != None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._node_link._selector == Selector.generate_from_str("a2 = v3"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._node_link._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._node_link._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._node_link._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._selector == Selector.generate_from_str("a3 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link != None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._selector == Selector.generate_from_str("a3 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v2")][1]._selector == Selector.generate_from_str("a1 = v2"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v2")][1]._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v2")][1]._counters[1] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v2")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._selector == Selector.generate_from_str("a2 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._counters[0] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._node_link != None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._node_link._selector == Selector.generate_from_str("a2 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._node_link._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._node_link._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._node_link._node_link == None)
    # Test the sorted header table.
    ## ==> Ascending orden and, in case of tie, we maintain the insertion order (the order of appearance in the dataset).
    assert (fp_tree_for_sdmap._sorted_header_table == [Selector.generate_from_str("a2 = v2"), Selector.generate_from_str("a3 = v1"), Selector.generate_from_str("a1 = v3"), \
                                                Selector.generate_from_str("a3 = v3"), Selector.generate_from_str("a1 = v4"), Selector.generate_from_str("a2 = v1"), 
                                                Selector.generate_from_str("a1 = v1"), Selector.generate_from_str("a3 = v2"), Selector.generate_from_str("a2 = v3"), 
                                                Selector.generate_from_str("a3 = v4"), Selector.generate_from_str("a1 = v2"), Selector.generate_from_str("a2 = v4")])
    # Test the complete tree.
    assert (fp_tree_for_sdmap.root_node.number_of_children == 4)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")].number_of_children == 2)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a3 = v2")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v2")].number_of_children == 2)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")]._childs[Selector.generate_from_str("a3 = v4")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")]._childs[Selector.generate_from_str("a3 = v4")]._childs[Selector.generate_from_str("a1 = v3")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")]._childs[Selector.generate_from_str("a3 = v2")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")]._childs[Selector.generate_from_str("a3 = v2")]._childs[Selector.generate_from_str("a2 = v2")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")]._childs[Selector.generate_from_str("a2 = v3")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")]._childs[Selector.generate_from_str("a2 = v3")]._childs[Selector.generate_from_str("a3 = v4")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a3 = v2")]._childs[Selector.generate_from_str("a1 = v4")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a3 = v2")]._childs[Selector.generate_from_str("a1 = v4")]._childs[Selector.generate_from_str("a2 = v1")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v2")]._childs[Selector.generate_from_str("a2 = v4")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v2")]._childs[Selector.generate_from_str("a2 = v4")]._childs[Selector.generate_from_str("a3 = v1")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v2")]._childs[Selector.generate_from_str("a2 = v3")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v2")]._childs[Selector.generate_from_str("a2 = v3")]._childs[Selector.generate_from_str("a3 = v3")].number_of_children == 0)
    assert (id(fp_tree_for_sdmap.root_node) == id(fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")].parent))
    assert (id(fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")]._childs[Selector.generate_from_str("a3 = v4")]) == id(fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")]._childs[Selector.generate_from_str("a3 = v4")]._childs[Selector.generate_from_str("a1 = v3")].parent))

def test_FPTreeForSDMap_build_tree_3():
    df = pd.DataFrame({"a1" : ["v1", "v1", "v2", "v3", "v2", "v4"], "a2" : ["v2", "v3", "v4", "v4", "v3", "v1"],\
                        "a3" : ["v2", "v4", "v1", "v4", "v3", "v2"], "target" : ["Y", "Y", "N", "Y", "N", "N"]})
    fp_tree_for_sdmap = FPTreeForSDMap()
    target = ("target", "Y")
    set_of_frequent_selectors = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, 2, 0)
    fp_tree_for_sdmap.build_tree(df, set_of_frequent_selectors, target)
    # Test the header table.
    assert (len(fp_tree_for_sdmap.header_table) == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][0][0] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][0][1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][0][0] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][0][1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._selector == Selector.generate_from_str("a1 = v1"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._counters[0] == 2)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a1 = v1")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._selector == Selector.generate_from_str("a3 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link != None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._selector == Selector.generate_from_str("a3 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._counters[1] == 0)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v4")][1]._node_link._node_link == None)
    # Test the sorted header table.
    assert (fp_tree_for_sdmap._sorted_header_table == [Selector.generate_from_str("a1 = v1"), Selector.generate_from_str("a3 = v4")])
    # Test the complete tree.
    assert (fp_tree_for_sdmap.root_node.number_of_children == 2)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")].number_of_children == 1)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a3 = v4")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a1 = v1")]._childs[Selector.generate_from_str("a3 = v4")].number_of_children == 0)

def test_FPTreeForSDMap_build_tree_4():
    df = pd.DataFrame({"a1" : ["v1", "v1", "v2", "v3", "v2", "v4"], "a2" : ["v2", "v3", "v4", "v4", "v3", "v1"],\
                        "a3" : ["v2", "v4", "v1", "v4", "v3", "v2"], "target" : ["Y", "Y", "N", "Y", "N", "N"]})
    fp_tree_for_sdmap = FPTreeForSDMap()
    target = ("target", "Y")
    set_of_frequent_selectors = fp_tree_for_sdmap.generate_set_of_frequent_selectors(df, target, 1, 1)
    fp_tree_for_sdmap.build_tree(df, set_of_frequent_selectors, target)
    # Test the header table.
    assert (len(fp_tree_for_sdmap.header_table) == 3)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][0][0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][0][1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._selector == Selector.generate_from_str("a3 = v2"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a3 = v2")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._selector == Selector.generate_from_str("a2 = v3"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v3")][1]._node_link == None)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._selector == Selector.generate_from_str("a2 = v4"))
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._counters[0] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._counters[1] == 1)
    assert (fp_tree_for_sdmap.header_table[Selector.generate_from_str("a2 = v4")][1]._node_link == None)
    # Test the sorted header table.
    assert (fp_tree_for_sdmap._sorted_header_table == [Selector.generate_from_str("a3 = v2"), Selector.generate_from_str("a2 = v3"), Selector.generate_from_str("a2 = v4")])
    # Test the complete tree.
    assert (fp_tree_for_sdmap.root_node.number_of_children == 3)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a3 = v2")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v3")].number_of_children == 0)
    assert (fp_tree_for_sdmap.root_node._childs[Selector.generate_from_str("a2 = v4")].number_of_children == 0)

def test_FPTreeForSDMap_generate_conditional_fp_tree():
    fp_tree_for_sd_map = FPTreeForSDMap()
    ## The tree will be built by hand in order to test this functionality. It is a custom tree and has not been generated from any dataset.
    # A branch from the root.
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("a = a"), Selector.generate_from_str("b = b"), Selector.generate_from_str("c = c"), Selector.generate_from_str("w = w")], fp_tree_for_sd_map.root_node, 0)
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("a = a"), Selector.generate_from_str("b = b")], fp_tree_for_sd_map.root_node, 1)
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("a = a")], fp_tree_for_sd_map.root_node, 1)
    # A branch from the root.
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("z = z"), Selector.generate_from_str("j = j"), Selector.generate_from_str("c = c")], fp_tree_for_sd_map.root_node, 0)
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("z = z"), Selector.generate_from_str("j = j"), Selector.generate_from_str("c = c")], fp_tree_for_sd_map.root_node, 1)
    for _ in range(3):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("z = z")], fp_tree_for_sd_map.root_node, 1)
    for _ in range(2):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("z = z")], fp_tree_for_sd_map.root_node, 0)
    # A branch from the root.
    for _ in range(3):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("j = j"), Selector.generate_from_str("c = c")], fp_tree_for_sd_map.root_node, 1)
    for _ in range(2):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("j = j"), Selector.generate_from_str("c = c")], fp_tree_for_sd_map.root_node, 0)
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("j = j")], fp_tree_for_sd_map.root_node, 1)
    for _ in range(2):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("j = j")], fp_tree_for_sd_map.root_node, 0)
    # A branch from the root.
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i"), Selector.generate_from_str("c = c"), Selector.generate_from_str("w = w")], fp_tree_for_sd_map.root_node, 0)
    for _ in range(3):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i"), Selector.generate_from_str("c = c")], fp_tree_for_sd_map.root_node, 1)
    for _ in range(2):
        fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i"), Selector.generate_from_str("c = c")], fp_tree_for_sd_map.root_node, 0)
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i")], fp_tree_for_sd_map.root_node, 1)
    fp_tree_for_sd_map._insert_tree([Selector.generate_from_str("d = d"), Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i")], fp_tree_for_sd_map.root_node, 0)
    # Finally, we create the sorted header table.
    assert (fp_tree_for_sd_map._sorted_header_table == [])
    for key in fp_tree_for_sd_map._header_table:
        fp_tree_for_sd_map._sorted_header_table.append( key )
    # IMPORTANT: THIS CRITERION HAS BEEN EXTRACTED FROM THE ORIGINAL IMPLEMENTATION OF THE SDMAP ALGORITHM (IN VIKAMINE).
    # We have to sort the selectors according to the summation of 'n' (i.e., summation of tp + summation of fp).
    # - In case of tie, we maintain the insertion order (the order of appearance in the dataset).
    fp_tree_for_sd_map._sorted_header_table.sort(reverse=False, \
        key=lambda x : (fp_tree_for_sd_map._header_table[x][0][0] + fp_tree_for_sd_map._header_table[x][0][1])) # Ascending order.
    #print(fp_tree_for_sd_map.header_table_as_str())
    #print(fp_tree_for_sd_map.tree_as_str())
    #print(fp_tree_for_sd_map.sorted_header_table)
    assert (fp_tree_for_sd_map.sorted_header_table == [Selector.generate_from_str("b = b"), Selector.generate_from_str("w = w"), Selector.generate_from_str("a = a"), \
                                                        Selector.generate_from_str("z = z"), Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i"), \
                                                        Selector.generate_from_str("j = j"), Selector.generate_from_str("c = c"), Selector.generate_from_str("d = d")])
    ## Test the conditional FPTree with the selector "c = 'c'" and without thresholds.
    conditional_fp_tree_c_eq_c = fp_tree_for_sd_map.generate_conditional_fp_tree([Selector.generate_from_str("c = c")], 0, 0)
    # Test the header table.
    assert (len(conditional_fp_tree_c_eq_c.header_table) == 7)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("a = a")][0][0] == 0)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("a = a")][0][1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("b = b")][0][0] == 0)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("b = b")][0][1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("d = d")][0][0] == 6)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("d = d")][0][1] == 5)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][0][0] == 4)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][0][1] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("k = k")][0][0] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("k = k")][0][1] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("i = i")][0][0] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("i = i")][0][1] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("z = z")][0][0] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("z = z")][0][1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("a = a")][1]._selector == Selector.generate_from_str("a = a"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("a = a")][1]._counters[0] == 0)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("a = a")][1]._counters[1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("a = a")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("b = b")][1]._selector == Selector.generate_from_str("b = b"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("b = b")][1]._counters[0] == 0)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("b = b")][1]._counters[1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("b = b")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("d = d")][1]._selector == Selector.generate_from_str("d = d"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("d = d")][1]._counters[0] == 6)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("d = d")][1]._counters[1] == 5)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("d = d")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("z = z")][1]._selector == Selector.generate_from_str("z = z"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("z = z")][1]._counters[0] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("z = z")][1]._counters[1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("z = z")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("k = k")][1]._selector == Selector.generate_from_str("k = k"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("k = k")][1]._counters[0] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("k = k")][1]._counters[1] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("k = k")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("i = i")][1]._selector == Selector.generate_from_str("i = i"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("i = i")][1]._counters[0] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("i = i")][1]._counters[1] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("i = i")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._selector == Selector.generate_from_str("j = j"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._counters[0] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._counters[1] == 1)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._node_link != None)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._node_link._selector == Selector.generate_from_str("j = j"))
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._node_link._counters[0] == 3)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._node_link._counters[1] == 2)
    assert (conditional_fp_tree_c_eq_c.header_table[Selector.generate_from_str("j = j")][1]._node_link._node_link == None)
    # Test the sorted header table.
    assert (conditional_fp_tree_c_eq_c._sorted_header_table == [Selector.generate_from_str("a = a"), Selector.generate_from_str("b = b"), \
                                                                Selector.generate_from_str("z = z"), Selector.generate_from_str("k = k"), \
                                                                Selector.generate_from_str("i = i"), Selector.generate_from_str("j = j"), \
                                                                Selector.generate_from_str("d = d")])
    # Test the complete tree.
    assert (conditional_fp_tree_c_eq_c.root_node.number_of_children == 3)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("a = a")].number_of_children == 1)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("j = j")].number_of_children == 1)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("d = d")].number_of_children == 2)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("a = a")]._childs[Selector.generate_from_str("b = b")].number_of_children == 0)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("j = j")]._childs[Selector.generate_from_str("z = z")].number_of_children == 0)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("d = d")]._childs[Selector.generate_from_str("j = j")].number_of_children == 0)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("d = d")]._childs[Selector.generate_from_str("k = k")].number_of_children == 1)
    assert (conditional_fp_tree_c_eq_c.root_node._childs[Selector.generate_from_str("d = d")]._childs[Selector.generate_from_str("k = k")]._childs[Selector.generate_from_str("i = i")].number_of_children == 0)
    ## Test the conditional FPTree with the selector "c = 'c'" and with thresholds.
    conditional_fp_tree_c_eq_c_3_2 = fp_tree_for_sd_map.generate_conditional_fp_tree([Selector.generate_from_str("c = c")], 3, 2)
    # Test the header table.
    assert (len(conditional_fp_tree_c_eq_c_3_2.header_table) == 4)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("d = d")][0][0] == 6)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("d = d")][0][1] == 5)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][0][0] == 4)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][0][1] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("k = k")][0][0] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("k = k")][0][1] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("i = i")][0][0] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("i = i")][0][1] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("d = d")][1]._selector == Selector.generate_from_str("d = d"))
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("d = d")][1]._counters[0] == 6)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("d = d")][1]._counters[1] == 5)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("d = d")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("k = k")][1]._selector == Selector.generate_from_str("k = k"))
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("k = k")][1]._counters[0] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("k = k")][1]._counters[1] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("k = k")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("i = i")][1]._selector == Selector.generate_from_str("i = i"))
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("i = i")][1]._counters[0] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("i = i")][1]._counters[1] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("i = i")][1]._node_link == None)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._selector == Selector.generate_from_str("j = j"))
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._counters[0] == 1)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._counters[1] == 1)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._node_link != None)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._node_link._selector == Selector.generate_from_str("j = j"))
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._node_link._counters[0] == 3)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._node_link._counters[1] == 2)
    assert (conditional_fp_tree_c_eq_c_3_2.header_table[Selector.generate_from_str("j = j")][1]._node_link._node_link == None)
    # Test the sorted header table.
    assert (conditional_fp_tree_c_eq_c_3_2._sorted_header_table == [Selector.generate_from_str("k = k"), Selector.generate_from_str("i = i"), \
                                                                    Selector.generate_from_str("j = j"), Selector.generate_from_str("d = d")])                                
    # Test the complete tree.
    assert (conditional_fp_tree_c_eq_c_3_2.root_node.number_of_children == 2)
    assert (conditional_fp_tree_c_eq_c_3_2.root_node._childs[Selector.generate_from_str("j = j")].number_of_children == 0)
    assert (conditional_fp_tree_c_eq_c_3_2.root_node._childs[Selector.generate_from_str("d = d")].number_of_children == 2)
    assert (conditional_fp_tree_c_eq_c_3_2.root_node._childs[Selector.generate_from_str("d = d")]._childs[Selector.generate_from_str("j = j")].number_of_children == 0)
    assert (conditional_fp_tree_c_eq_c_3_2.root_node._childs[Selector.generate_from_str("d = d")]._childs[Selector.generate_from_str("k = k")].number_of_children == 1)
    assert (conditional_fp_tree_c_eq_c_3_2.root_node._childs[Selector.generate_from_str("d = d")]._childs[Selector.generate_from_str("k = k")]._childs[Selector.generate_from_str("i = i")].number_of_children == 0)
