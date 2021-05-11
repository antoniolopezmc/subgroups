# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Run all tests.
"""

from subgroups.tests.core.operator_test import *
from subgroups.tests.core.selector_test import *
from subgroups.tests.core.pattern_test import *
from subgroups.tests.core.subgroup_test import *
from subgroups.tests.quality_measures.all_tests import *
from subgroups.tests.utils.dataframe_filters_test import *
from subgroups.tests.data_structures.fp_tree_node_test import *
from subgroups.tests.data_structures.fp_tree_for_sdmap_test import *
from subgroups.tests.algorithms.sdmap_test import *
from subgroups.tests.data_structures.vertical_list_test import *
from subgroups.tests.algorithms.vlsd_test import *

if __name__ == "__main__":
    # core/operator_test file.
    test_Operator_evaluate_method()
    test_Operator_evaluate_method_with_pandasSeries()
    test_Operator_generate_from_str_method()
    test_Operator_string_representation()
    # core/selector_test file.
    test_Selector_creation_process()
    test_Selector_deletion_process()
    test_Selector_same_value_different_type()
    test_Selector_attributes()
    test_Selector_match_method()
    test_Selector_generate_from_str_method()
    test_Selector_comparisons()
    # core/pattern_test file.
    test_Pattern()
    test_Pattern_is_contained_method()
    # core/subgroup_test file.
    test_Subgroup()
    test_Subgroup_filter()
    # quality_measures/all_tests file.
    test_quality_measures()
    test_quality_measures_compute()
    # utils/dataframe_filters_test file.
    test_dataframe_filters()
    # data_structures/fp_tree_node_test file.
    test_FPTreeNode()
    # data_structures/fp_tree_for_sdmap_test file.
    test_FPTreeForSDMap_generate_set_of_frequent_selectors_1()
    test_FPTreeForSDMap_generate_set_of_frequent_selectors_2()
    test_FPTreeForSDMap_generate_set_of_frequent_selectors_3()
    test_FPTreeForSDMap_build_tree_1()
    test_FPTreeForSDMap_build_tree_2()
    test_FPTreeForSDMap_build_tree_3()
    test_FPTreeForSDMap_build_tree_4()
    test_FPTreeForSDMap_generate_conditional_fp_tree_1()
    test_FPTreeForSDMap_generate_conditional_fp_tree_2()
    # algorithms/sdmap_test file.
    test_SDMap_init_method()
    test_SDMap_fpgrowth_method_1()
    test_SDMap_fpgrowth_method_2()
    test_SDMap_fpgrowth_method_3()
    test_SDMap_fpgrowth_method_4()
    test_SDMap_fit_method_1()
    test_SDMap_fit_method_2()
    test_SDMap_fit_method_3()
    test_SDMap_fit_method_4()
    test_SDMap_fit_method_5()
    test_SDMap_fit_method_6()
    test_SDMap_fit_method_7()
    test_SDMap_fit_method_8()
    test_SDMap_fit_method_9()
    test_SDMap_fit_method_10()
    test_SDMap_fit_method_11()
    test_SDMap_visited_and_pruned_nodes()
    # data_structures/vertical_list_test file.
    test_vertical_list_1()
    test_vertical_list_2()
    test_vertical_list_3()
    test_vertical_list_str_method()
    # algorithms/vlsd file.
    #test_VLSD_init_method_1()
    #test_VLSD_init_method_2()
    #test_VLSD_fit_method_1()
    #test_VLSD_fit_method_2()
    #test_VLSD_fit_method_3()
    #test_VLSD_fit_method_4()
    #test_VLSD_fit_method_5()
