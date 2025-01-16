# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles <franciscojose.morac@um.es>

"""This file contains the implementation of the Bitset data structure used in the BSD algorithm and its variants.
"""

from pandas import DataFrame
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern
from bitarray import bitarray

class BitsetDictionary(dict):
    """ Internal class to implement the dicttionaries used in the bitset. This dictionary only allows to insert a Pattern or a Selector as key. If a Selector is inserted, it is converted to a Pattern. Each entry must store a bitarray.
    """

    __slots__ = ()

    def __iter__(self):
        for key in super().__iter__():
            yield Pattern.generate_from_str(key)

    def __setitem__(self, key, value) -> None:
        if (type(value) != bitarray):
            raise TypeError("The value must be a bitarray.")
        if (type(key) is Selector):
            super().__setitem__(str(Pattern([key])),value)
        elif (type(key) is Pattern):
            super().__setitem__(str(key), value)
        else:
            raise TypeError("The key must be a Selector or a Pattern.")
    
    def __getitem__(self, key) -> bitarray:
        if (type(key) is Selector):
            return super().__getitem__(str(Pattern([key])))
        elif (type(key) is Pattern):
            return super().__getitem__(str(key))
        else:
            raise TypeError("The key must be a Selector or a Pattern.")
    
    def __contains__(self, __o: object) -> bool:
        if (type(__o) is Selector):
            return super().__contains__(str(Pattern([__o])))
        elif (type(__o) is Pattern):
            return super().__contains__(str(__o))
        else:
            raise TypeError("The key must be a Selector or a Pattern.")

class BitsetBSD(object):
    """This class represents a bitset used in the BSD algorithm and its variants.
    """

    __slots__ = ("_bitset_pos", "_bitset_neg")

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
        # Initialize the set of frequent selectors
        set_of_frequent_selectors = dict()
        # Get the columns of the dataset without the target column
        columns_without_target = pandas_dataframe.columns[pandas_dataframe.columns != tuple_target_attribute_value[0]]
        selectors = []
        for column in columns_without_target:
            # If the column contains only string values
            if pandas_dataframe[column].apply(lambda x: isinstance(x, str)).all():
                # Add to the list of selectors that column along with its values
                selectors += [(column, value) for value in pandas_dataframe[column].unique()]
        # Get the rows that match the target value
        df_pos = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]]
        for selector in selectors:
            # Get the number of rows that match the selector and the target value
            num_pos = len(df_pos[df_pos[selector[0]] == selector[1]])
            # Save the selector and its support in the dictionary if it is above the minimum support
            if num_pos >= min_support:
                set_of_frequent_selectors[Selector(selector[0], Operator.EQUAL, selector[1])] = num_pos
        list_of_frequent_selectors = [(key, set_of_frequent_selectors[key]) for key in set_of_frequent_selectors.keys()]
        # Sort the list of frequent selectors by tp
        list_of_frequent_selectors.sort(key=lambda x: x[1], reverse=True)
        # Return only the selectors
        return [x[0] for x in list_of_frequent_selectors]
