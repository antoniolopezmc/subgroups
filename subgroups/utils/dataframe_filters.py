# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of some additional functions used for filtering a pandas DataFrame according to certain criteria.
"""

from pandas import DataFrame, Series

def filter_by_list_of_selectors(pandas_dataframe, list_of_selectors):
    """Method to filter a pandas DataFrame, retrieving only the rows covered by all selectors included in the parameter 'list_of_selectors'.
    
    :type pandas_dataframe: pandas.DataFrame
    :param pandas_dataframe: the DataFrame which is filtered.
    :type list_of_selectors: list[Selector]
    :param list_of_selectors: the list of selectors used in the filtering process. IMPORTANT: we assume that the parameter 'list_of_selectors' only contains selectors.
    :rtype: pandas.DataFrame
    :return: the pandas DataFrame obtained after the filtering process.
    """
    if type(pandas_dataframe) is not DataFrame:
        raise TypeError("The type of the parameter 'pandas_dataframe' must be 'pandas.DataFrame'.")
    if type(list_of_selectors) is not list:
        raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
    final_result = Series([True] * len(pandas_dataframe)) # The empty list of selectors is contained in all the rows of a pandas DataFrame.
    for selector in list_of_selectors:
        current_attribute_name = selector.attribute_name
        corresponding_Series = pandas_dataframe[current_attribute_name]
        final_result = final_result & selector.match(current_attribute_name, corresponding_Series)
    return pandas_dataframe[final_result]
