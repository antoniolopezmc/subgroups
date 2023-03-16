# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the FPTree data structure used in the BSD algorithm and its variants.
"""

from pandas import DataFrame

# Python annotations.
from typing import Union
from subgroups.core.operator import Operator

from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern
from bitarray import bitarray

class BitsetDictionary(dict):
    """ Internal class to implement the dicttionaries used in the bitset. This dictionary only allows to insert a Pattern or a Selector as key.
    If a Selector is inserted, it is converted to a Pattern. Each entry must store a bitarray.
    """

    def __iter__(self):
        for key in super().__iter__():
            yield Pattern.generate_from_str(key)

    def __setitem__(self, key, value) -> None:
        if (type(value) != bitarray):
            raise TypeError("The value must be a bitarray.")
        if (type(key)==Selector):
            super().__setitem__(str(Pattern([key])),value)
        elif (type(key)==Pattern):
            super().__setitem__(str(key), value)
        else:
            raise TypeError("The key must be a Selector or a Pattern.")
    
    def __getitem__(self, key) -> bitarray:
        if (type(key)==Selector):
            return super().__getitem__(str(Pattern([key])))
        elif (type(key)==Pattern):
            return super().__getitem__(str(key))
        else:
            raise TypeError("The key must be a Selector or a Pattern.")
    
    def __contains__(self, __o: object) -> bool:
        if (type(__o)==Selector):
            return super().__contains__(str(Pattern([__o])))
        elif (type(__o)==Pattern):
            return super().__contains__(str(__o))
        else:
            raise TypeError("The key must be a Selector or a Pattern.")


class BitsetBSD(object):
    """This class represents a bitset used in the BSD algorithm and its variants.

    """

    def __init__(self):
        """Method to initialize an object of type 'BitsetBSD'.
        """
        # For each dictionary, the key is a string representation of a pattern and the value is a bitarray that stores for each row whether it follows the pattern.
        # As we are using the BitsetDictionary class, we can use Patterns or Selectors as keys.
        self._bitset_pos = BitsetDictionary()
        self._bitset_neg = BitsetDictionary()

    def _get_bitset_pos(self) -> dict:
        """Private Method to get the bitset_pos dictionary.

        :return: the bitset_pos dictionary.
        """
        return self._bitset_pos
    
    def _get_bitset_neg(self) -> dict:
        """Private Method to get the bitset_neg dictionary.

        :return: the bitset_neg dictionary.
        """
        return self._bitset_neg
    
    def _set_bitset_pos(self, bitset_pos : dict) -> None:
        """Private Method to set the bitset_pos dictionary.

        :param bitset_pos: the bitset_pos dictionary.
        """
        self._bitset_pos = bitset_pos
    
    def _set_bitset_neg(self, bitset_neg : dict) -> None:
        """Private Method to set the bitset_neg dictionary.

        :param bitset_neg: the bitset_neg dictionary.
        """
        self._bitset_neg = bitset_neg
    
    bitset_pos = property(_get_bitset_pos, _set_bitset_pos, None, "The bitset dictionary for rows that match the target value.")
    bitset_neg = property(_get_bitset_neg, _set_bitset_neg, None, "The bitset dictionary for rows that do not match the target value.")


    def build_bitset(self, pandas_dataframe :DataFrame,set_of_frequent_selectors:list, tuple_target_attribute_value : tuple) -> None:
        """Method to build the complete tree from the root node using a set of frequent selectors.

        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :param set_of_frequent_selectors: The set of frequent selectors (L) to use in the building of the tree.
        :param tuple_target_attribute_value: Tuple with the name of the target attribute (first element) and with the value of this attribute (second element). EXAMPLE1: ("age", 25). EXAMPLE2: ("class", "Setosa"). It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset,
          (3) it is VERY IMPORTANT to respect the types of the attributes: the value in the tuple (second element) MUST BE comparable with the values of the corresponding attribute in the dataset,
          (4) the value of the target attribute MUST exist in the dataset.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if type(set_of_frequent_selectors) is not list:
            raise TypeError("Parameter 'set_of_frequent_selectors' must be a list.")
        if (type(tuple_target_attribute_value) is not tuple):
            raise TypeError("Parameter 'tuple_target_attribute_value' must be a tuple.")
        if (len(tuple_target_attribute_value) != 2):
            raise ValueError("Parameter 'tuple_target_attribute_value' must be of length 2.")
        if type(tuple_target_attribute_value[0]) is not str:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') must be a string.")

        # Initialize an empty list for selectors
        selectors = []
        # Get the columns of the dataset without the target column
        columns_without_target = pandas_dataframe.columns[pandas_dataframe.columns != tuple_target_attribute_value[0]]
        # Check that each column contains only string values
        for column in columns_without_target:
            # If the column contains only string values
            if pandas_dataframe[column].apply(lambda x: isinstance(x, str)).all():
                # Add to the list of selectors that column along with its values
                selectors += [(column, value) for value in pandas_dataframe[column].unique()]
        # Filter the list of selectors to keep only those that are in the set of frequent selectors
        selectors = list(filter(lambda x: Selector(x[0], Operator.EQUAL, x[1]) in set_of_frequent_selectors, selectors))
        # Get the subset of the dataset where the target column has the target value (positive examples)
        df_pos = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]]
        # Get the subset of the dataset where the target column does not have the target value (negative examples)
        df_neg = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1]]
        # For each selector in the list of selectors
        for selector in selectors:
            # Create a bitarray from the boolean array that indicates whether the positive examples match the selector
            ba_pos = bitarray((df_pos[selector[0]] == selector[1]).tolist())
            # Create a bitarray from the boolean array that indicates whether the negative examples match the selector
            ba_neg = bitarray((df_neg[selector[0]] == selector[1]).tolist())
            # Add the bitarrays to the corresponding bitset dictionaries with the selector as key
            self._bitset_pos[Selector(selector[0],Operator.EQUAL, selector[1])] = ba_pos
            self._bitset_neg[Selector(selector[0],Operator.EQUAL, selector[1])] = ba_neg

    def _update_empty_bitsets(self,positive_counts : int, negative_counts : int):
        """Internal method to set the length of the bit sets to be equal to bitsetCount
        :param positive_counts: Length of bitset_pos values
        :param positive_counts: Length of bitset_neg values
        """
        if type(positive_counts) is not int:
            raise TypeError("Parameter 'positive_counts' must be a int.")
        if type(negative_counts) is not int:
            raise TypeError("Parameter 'negative_counts' must be a int.")
        for pat in self._bitset_neg:
            if (len(pat) > 1):
                #If the pattern is not equivalent to a single selector
                continue
            selector = pat.get_selector(0)
            if selector not in self._bitset_pos:
                self._bitset_pos[selector] = bitarray([0]) * positive_counts

        for pat in self._bitset_pos:
            if (len(pat) > 1):
                #If the pattern is not equivalent to a single selector
                continue
            selector = pat.get_selector(0)
            if selector not in self._bitset_neg:
                self._bitset_neg[selector] = bitarray([0]) * negative_counts




    def _update_bitset(self,selectorsUsed : list,bitset):
        """Internal method to update the not added selectors in the bitset
       :type selectorsUsed: List
       :param selectorsUsed: List of selectors
       :type bitset: dict
       :param bitset: dict that represents a bitset
       """
        if type(selectorsUsed) is not list:
            raise TypeError("Parameter 'selectorsUsed' must be a list.")
        if type(bitset) is not BitsetDictionary:
            raise TypeError("Parameter 'bitset' must be a dict.")

        for pat in bitset:
            if (len(pat) > 1):
                #If the pattern is not equivalent to a selector
                continue
            selector = pat.get_selector(0)
            # If the selector is not in the list of selectors used in the current row, we have to add
            # the information of the current row of the dataset.
            if (selector not in selectorsUsed):
                bitset[selector] = bitset[selector] + [False]
        return bitset

    def generate_set_of_frequent_selectors(self, pandas_dataframe, tuple_target_attribute_value, min_support):
        """Method to scan the dataset (ONLY DISCRETE/NOMINAL ATTRIBUTES) and collect the sorted set of frequent selectors (L).

        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :type tuple_target_attribute_value: tuple
        :param tuple_target_attribute_value: Tuple with the name of the target attribute (first element) and with the value of this attribute (second element). EXAMPLE1: ("age", 25). EXAMPLE2: ("class", "Setosa"). It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset,
          (3) it is VERY IMPORTANT to respect the types of the attributes: the value in the tuple (second element) MUST BE comparable with the values of the corresponding attribute in the dataset,
          (4) the value of the target attribute MUST exist in the dataset.
        :type min_support: int
        :param min_support: Minimum support threshold (NUMBER OF TIMES, NOT A PROPORTION).
        :rtype: list
        :return: the sorted set of frequent selectors (L) as a list.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if (type(tuple_target_attribute_value) is not tuple):
            raise TypeError("Parameter 'tuple_target_attribute_value' must be a tuple.")
        if (len(tuple_target_attribute_value) != 2):
            raise ValueError("Parameter 'tuple_target_attribute_value' must be of length 2.")
        if type(tuple_target_attribute_value[0]) is not str:
            raise ValueError(
                "The name of the target attribute (first element in parameter 'tuple_target_attribute_value') must be a string.")
        if tuple_target_attribute_value[0] not in pandas_dataframe.columns:
            raise ValueError(
                "The name of the target attribute (first element in parameter 'tuple_target_attribute_value') is not an attribute of the input dataset.")
        if (type(min_support) is not int) and (type(min_support) is not float):
            raise TypeError("Parameter 'min_support' must be a number.")
        # key: Selector (ONLY OF THE FORM "ATTRIBUTE = VALUE"), value: int: true positives ('tp').
        final_set_of_frequent_selectors = dict()
        # We generate the set of frequent selectors.
        columns_without_target = pandas_dataframe.columns[pandas_dataframe.columns != tuple_target_attribute_value[0]]
        for column in columns_without_target:  # Iterate over dataframe column names, except target column name.
            if (type(pandas_dataframe[column].loc[
                         0]) is str):  # Only check the first element, because all elements of the column are of the same type.
                # EXTREMELY IMPORTANT: DOCUMENTATION OF PANDAS: ITERROWS.
                #   - Because iterrows returns a Series for each row, it does NOT preserve dtypes across the rows (dtypes are preserved across columns for DataFrames).
                #   - This is important because types in Selector are primitive types of python (and not pandas or numpy types).
                for index, row in pandas_dataframe.iterrows():
                    new_selector = Selector(column, Operator.EQUAL, row[column])
                    new_selector = str(new_selector)
                    # IF the selector does not exist in the dict AND the target match.
                    if (new_selector not in final_set_of_frequent_selectors) and (row[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]):
                        final_set_of_frequent_selectors[new_selector] = 1
                    # IF the selector does not exist in the dict AND the target does not match.
                    elif (new_selector not in final_set_of_frequent_selectors) and (row[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1]):
                        final_set_of_frequent_selectors[new_selector] = 0
                    # IF the selector exists in the dict AND the target match.
                    elif (new_selector in final_set_of_frequent_selectors) and (row[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]):
                        final_set_of_frequent_selectors[new_selector] = final_set_of_frequent_selectors[new_selector] + 1
        # Make a list with the selectors that have a value of 'tp' greater or equal than the minimum support.
        final_list_of_frequent_selectors = []
        for key in final_set_of_frequent_selectors:
            if final_set_of_frequent_selectors[key] >= min_support:
                final_list_of_frequent_selectors.append((key, final_set_of_frequent_selectors[key]))  # Add the selector and its 'tp' as a tuple.
        # Sort descending/reverse by value of 'tp'.
        final_list_of_frequent_selectors.sort(key=lambda x: x[1], reverse=True)
        # LIST OF FREQUENT SELECTORS L.
        return [Selector.generate_from_str(x[0]) for x in final_list_of_frequent_selectors]  # RETURN ONLY THE SELECTORS IN A LIST.
