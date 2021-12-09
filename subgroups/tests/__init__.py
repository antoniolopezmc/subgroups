# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""We use the __init__.py file to create a function with which to run all tests.
"""

from subgroups import __file__ as subgroups_package_init_file
from subgroups.tests import __file__ as tests_package_init_file
from os.path import dirname
import unittest

def run_all():
    test_loader = unittest.TestLoader()
    subgroups_package_dir = dirname(subgroups_package_init_file)
    tests_package_dir = dirname(tests_package_init_file)
    test_suite = test_loader.discover(start_dir = tests_package_dir, pattern = "test_*.py", top_level_dir = subgroups_package_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

