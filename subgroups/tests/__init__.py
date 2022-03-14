# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""We use the __init__.py file to create a function with which to run all tests.
"""

from subgroups import __file__ as subgroups_package_init_file
from subgroups.tests import __file__ as subgroups_tests_package_init_file
from os.path import dirname
import unittest

def run_all_tests():
    test_loader = unittest.TestLoader()
    subgroups_package_dir = dirname(subgroups_package_init_file)
    subgroups_tests_package_dir = dirname(subgroups_tests_package_init_file)
    test_suite_core_package = test_loader.discover(start_dir = subgroups_tests_package_dir+"/core", pattern = "test_*.py", top_level_dir = subgroups_package_dir)
    test_suite_quality_measures_package = test_loader.discover(start_dir = subgroups_tests_package_dir+"/quality_measures", pattern = "test_*.py", top_level_dir = subgroups_package_dir)
    test_suite_data_structures_package = test_loader.discover(start_dir = subgroups_tests_package_dir+"/data_structures", pattern = "test_*.py", top_level_dir = subgroups_package_dir)
    test_suite_algorithms_package = test_loader.discover(start_dir = subgroups_tests_package_dir+"/algorithms", pattern = "test_*.py", top_level_dir = subgroups_package_dir)
    test_suite_utils_package = test_loader.discover(start_dir = subgroups_tests_package_dir+"/utils", pattern = "test_*.py", top_level_dir = subgroups_package_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    print("\n")
    print("##################################")
    print("########## CORE PACKAGE ##########")
    print("##################################")
    runner.run(test_suite_core_package)
    print("\n")
    print("##############################################")
    print("########## QUALITY MEASURES PACKAGE ##########")
    print("##############################################")
    runner.run(test_suite_quality_measures_package)
    print("\n")
    print("#############################################")
    print("########## DATA STRUCTURES PACKAGE ##########")
    print("#############################################")
    runner.run(test_suite_data_structures_package)
    print("\n")
    print("########################################")
    print("########## ALGORITHMS PACKAGE ##########")
    print("########################################")
    runner.run(test_suite_algorithms_package)
    print("\n")
    print("###################################")
    print("########## UTILS PACKAGE ##########")
    print("###################################")
    runner.run(test_suite_utils_package)
