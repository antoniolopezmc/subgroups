# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of some additional functions used for filtering a pandas DataFrame according to certain criteria.
"""

from pandas import DataFrame, Series
from subgroups.core.selector import Selector

def filter_by_list_of_selectors(pandas_dataframe : DataFrame, list_of_selectors : list[Selector]) -> DataFrame:
    """Method to filter a pandas DataFrame, retrieving only the rows covered by all selectors included in the parameter 'list_of_selectors'. IMPORTANT: If an attribute name of a selector of the pattern is not in the pandas.DataFrame passed by parameter, a KeyError exception is raised.
    
    :param pandas_dataframe: the DataFrame which is filtered.
    :param list_of_selectors: the list of selectors used in the filtering process. IMPORTANT: we assume that the parameter 'list_of_selectors' only contains selectors.
    :return: the pandas DataFrame obtained after the filtering process.
    """
    if type(pandas_dataframe) is not DataFrame:
        raise TypeError("The type of the parameter 'pandas_dataframe' must be 'pandas.DataFrame'.")
    if type(list_of_selectors) is not list:
        raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
    final_result = Series([True] * len(pandas_dataframe)) # The empty list of selectors is contained in all the rows of a pandas DataFrame.
    # For each selector, we process the whole corresponding attribute (i.e., the complete Series).
    # If all the boolean values of 'final_result' are False, we can stop the process.
    current_index = 0
    while (final_result.sum() > 0) and (current_index < len(list_of_selectors)):
        current_selector = list_of_selectors[current_index]
        current_attribute_name = current_selector.attribute_name
        corresponding_Series = pandas_dataframe[current_attribute_name]
        final_result = final_result & current_selector.match(current_attribute_name, corresponding_Series) # type: ignore
        current_index = current_index + 1
    return pandas_dataframe[final_result]
