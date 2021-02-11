# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Run all tests.
"""

from subgroups.tests.core.operator_test import *
from subgroups.tests.core.selector_test import *
from subgroups.tests.core.pattern_test import *
from subgroups.tests.core.subgroup_test import *
from subgroups.tests.quality_measures.all_test import *
from subgroups.tests.utils.dataframe_filters_test import *
from subgroups.tests.data_structures.fp_tree_node_test import *

if __name__ == "__main__":
    # core/operator file.
    test_Operator_evaluate_method()
    test_Operator_evaluate_method_with_pandasSeries()
    test_Operator_generate_from_str_method()
    test_Operator_string_representation()
    # core/selector file.
    test_Selector_creation_process()
    test_Selector_deletion_process()
    test_Selector_attributes()
    test_Selector_match_method()
    test_Selector_generate_from_str_method()
    test_Selector_comparisons()
    # core/pattern file.
    test_Pattern()
    test_Pattern_is_contained_method()
    # core/subgroup file.
    test_Subgroup()
    test_Subgroup_filter()
    # quality_measures folter.
    test_quality_measures()
    test_quality_measures_compute()
    # utils/dataframe_filters file.
    test_dataframe_filters()
    # data_structures/fp_tree_node file.
    test_FPTreeNode()
