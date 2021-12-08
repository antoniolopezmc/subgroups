# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Run all tests.
"""

from subgroups.tests.core.test_operator import *
from subgroups.tests.core.test_selector import *
from subgroups.tests.core.test_pattern import *
from subgroups.tests.core.test_subgroup import *
from subgroups.tests.quality_measures.test_quality_measures import *
from subgroups.tests.utils.test_dataframe_filters import *
from subgroups.tests.data_structures.test_fp_tree_node import *
from subgroups.tests.data_structures.test_fp_tree_for_sdmap import *
from subgroups.tests.algorithms.individual_subgroups.nominal_target.test_sdmap import *
from subgroups.tests.data_structures.test_vertical_list import *
from subgroups.tests.algorithms.individual_subgroups.nominal_target.test_vlsd import *

if __name__ == "__main__":
    # core/test_operator file.
    test_Operator_evaluate_method()
    test_Operator_evaluate_method_with_pandasSeries()
    test_Operator_generate_from_str_method()
    test_Operator_string_representation()
    # core/test_selector file.
    test_Selector_creation_process()
    test_Selector_deletion_process()
    test_Selector_same_value_different_type()
    test_Selector_attributes()
    test_Selector_match_method()
    test_Selector_generate_from_str_method()
    test_Selector_comparisons()
    # core/test_pattern file.
    test_Pattern()
    test_Pattern_is_contained_method()
    # core/test_subgroup file.
    test_Subgroup()
    test_Subgroup_filter()
    # quality_measures/test_all file.
    test_quality_measures()
    test_quality_measures_compute()
    # utils/test_dataframe_filters file.
    test_dataframe_filters()
    # data_structures/test_fp_tree_node file.
    test_FPTreeNode()
    # data_structures/test_fp_tree_for_sdmap file.
    test_FPTreeForSDMap_generate_set_of_frequent_selectors_1()
    test_FPTreeForSDMap_generate_set_of_frequent_selectors_2()
    test_FPTreeForSDMap_generate_set_of_frequent_selectors_3()
    test_FPTreeForSDMap_build_tree_1()
    test_FPTreeForSDMap_build_tree_2()
    test_FPTreeForSDMap_build_tree_3()
    test_FPTreeForSDMap_build_tree_4()
    test_FPTreeForSDMap_generate_conditional_fp_tree_1()
    test_FPTreeForSDMap_generate_conditional_fp_tree_2()
    # algorithms/test_sdmap file.
    test_SDMap_init_method_1()
    test_SDMap_init_method_2()
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
    # data_structures/test_vertical_list file.
    test_vertical_list_1()
    test_vertical_list_2()
    test_vertical_list_3()
    test_vertical_list_str_method()
    # algorithms/test_vlsd file.
    test_VLSD_init_method_1()
    test_VLSD_init_method_2()
    test_VLSD_fit_method_1()
    test_VLSD_fit_method_2()
    test_VLSD_fit_method_3()
    test_VLSD_fit_method_4()
    test_VLSD_fit_method_5()
    test_VLSD_fit_method_6()
    test_VLSD_fit_method_7()
