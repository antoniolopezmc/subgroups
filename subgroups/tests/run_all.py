# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Run all tests.
"""

from subgroups.tests.core.operator_test import *
from subgroups.tests.core.selector_test import *
from subgroups.tests.core.pattern_test import *

if __name__ == "__main__":
    test_Operator_evaluate_method()
    test_Operator_generate_from_str_method()
    test_Operator_string_representation()
    test_Selector_creation_process()
    test_Selector_deletion_process()
    test_Selector_attributes()
    test_Selector_match_method()
    test_Selector_generate_from_str_method()
    test_Selector_comparisons()
    test_Pattern()
