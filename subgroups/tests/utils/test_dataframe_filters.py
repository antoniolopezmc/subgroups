# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'utils/dataframe_filters.py'.
"""

from subgroups.utils.dataframe_filters import filter_by_list_of_selectors
from pandas import DataFrame
from subgroups.core.selector import Selector
import unittest

class TestDataFrameFilter(unittest.TestCase):

    def test_dataframe_filters_general(self):
        df1 = DataFrame({"a" : [1,2,3], "b" : [7,8,9], "c" : ["a", "b", "c"]})
        df2 = DataFrame({"a" : [1,2,3], "b" : [7,8,9], "c" : ["a", "b", "c"]})
        df3 = DataFrame({"a" : [1,2,3], "b" : [7,125,9], "c" : ["a", "b", "c"]})
        df4 = DataFrame({"a" : [1,2,3], "b" : [71,125,25], "c" : ["b", "b", "b"]})
        list_of_selectors_2 = [Selector.generate_from_str("b < 8")]
        list_of_selectors_3 = [Selector.generate_from_str("a >= 1"), Selector.generate_from_str("b >= 10")]
        list_of_selectors_4 = [Selector.generate_from_str("a >= 2"), Selector.generate_from_str("b >= 8"), Selector.generate_from_str("c = 'b'")]
        df2_filtered = DataFrame({"a" : [1], "b" : [7], "c" : ["a"]}, index=[0])
        df3_filtered = DataFrame({"a" : [2], "b" : [125], "c" : ["b"]}, index=[1])
        df4_filtered = DataFrame({"a" : [2,3], "b" : [125,25], "c" : ["b", "b"]}, index=[1,2])
        self.assertTrue((filter_by_list_of_selectors(df1, []) == df1).all().all())
        self.assertTrue((filter_by_list_of_selectors(df2, list_of_selectors_2) == df2_filtered).all().all())
        self.assertTrue((filter_by_list_of_selectors(df3, list_of_selectors_3) == df3_filtered).all().all())
        self.assertTrue((filter_by_list_of_selectors(df4, list_of_selectors_4) == df4_filtered).all().all())
        self.assertRaises(KeyError, filter_by_list_of_selectors, df1, [Selector.generate_from_str("att1 < 8")])
