# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Pattern'. A 'Pattern' is a sorted list of non-repeated selectors.
"""

from subgroups.core.selector import Selector
from bisect import bisect_left
from pandas import Series, DataFrame

# Python annotations.
from typing import Iterator

class Pattern(object):
    """This class represents a 'Pattern'. A 'Pattern' is a sorted list of non-repeated selectors.
    
    :param list_of_selectors: a list of selectors. IMPORTANT: we assume that the list only contains selectors.
    """
    
    __slots__ = ("_list_of_selectors")
    
    def __init__(self, list_of_selectors : list[Selector]) -> None:
        if type(list_of_selectors) is not list:
            raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
        # We use a temporal list in order to store a copy of the list 'list_of_selectors'. IMPORTANT: We only copy the list, but not the selectors contained in it.
        temporal_list_of_selectors = list_of_selectors.copy()
        # Sort the temporal list of selectors.
        temporal_list_of_selectors.sort()
        # Initialize 'self._list_of_selectors' to empty list.
        self._list_of_selectors = []
        # Append the elements of the list 'temporal_list_of_selectors' to the list 'self._list_of_selectors', avoiding the duplicates.
        for elem in temporal_list_of_selectors:
            if (len(self._list_of_selectors) == 0) or (self._list_of_selectors[-1] != elem):
                self._list_of_selectors.append(elem)
    
    def add_selector(self, selector : Selector) -> None:
        """Method to add a selector to the pattern. If the selector already exists, this method does nothing.
        
        :param selector: the selector which is added.
        """
        if not isinstance(selector, Selector):
            raise TypeError("The parameter 'selector' must be an instance of the 'Selector' class or of a subclass thereof.")
        # We can use the bisection algorithm because the list is sorted.
        index = bisect_left(self._list_of_selectors, selector)
        if (index == len(self._list_of_selectors)): # The list is empty OR the element will be inserted in the right side of the list.
            self._list_of_selectors.append(selector)
        elif (self._list_of_selectors[index] != selector): # The list is not empty AND the element will not be inserted in the right side of the list.
            self._list_of_selectors.insert(index, selector)
    
    def remove_selector(self, selector : Selector) -> None:
        """Method to remove a selector from the pattern. If the selector does not exist, this method does nothing.
        
        :param selector: the selector which is removed.
        """
        if not isinstance(selector, Selector):
            raise TypeError("The parameter 'selector' must be an instance of the 'Selector' class or of a subclass thereof.")
        # We can use the bisection algorithm because the list is sorted.
        index = bisect_left(self._list_of_selectors, selector)
        if (index < len(self._list_of_selectors)) and (self._list_of_selectors[index] == selector):
            self._list_of_selectors.pop(index)
    
    def remove_selector_by_index(self, index : int) -> None:
        """Method to remove a selector from the pattern by index. If the index is out of range, an 'IndexError' exception is raised.
        
        :param index: the index which is used.
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        self._list_of_selectors.pop(index)
    
    def get_selector(self, index : int) -> Selector:
        """Method to get a selector from the pattern by index. If the index is out of range, an 'IndexError' exception is raised.
        
        :param index: the index which is used.
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._list_of_selectors[index]
    
    def copy(self) -> 'Pattern':
        """Method to copy the Pattern.
        
        :return: the copy of the Pattern WITH THE SAME SELECTORS (THE SAME OBJECTS). This method does not copy the selectors of the list (it is not needed because the selectors are immutable).
        """
        new_list_of_selectors = self._list_of_selectors.copy()
        new_pattern = Pattern([]) # The list of selectors is already sorted. It is not needed to sort it in the __init__ method.
        new_pattern._list_of_selectors = new_list_of_selectors
        return new_pattern
    
    def is_contained(self, pandas_dataframe : DataFrame) -> Series:
        """Method to check whether the pattern is contained in each row of the pandas.DataFrame passed by parameter. IMPORTANT: If an attribute name of a selector of the pattern is not in the pandas.DataFrame passed by parameter, a KeyError exception is raised.
        
        :param pandas_dataframe: the pandas.DataFrame with which the pattern is checked.
        :return: whether the pattern is contained in each row of the pandas.DataFrame passed by parameter.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'pandas.DataFrame'.")
        final_result = Series([True] * len(pandas_dataframe)) # The empty pattern is contained in all the rows of a pandas DataFrame.
        # For each selector, we process the whole corresponding attribute (i.e., the complete Series).
        # If all the boolean values of 'final_result' are False, we can stop the process.
        current_index = 0
        while (final_result.sum() > 0) and (current_index < len(self._list_of_selectors)):
            current_selector = self._list_of_selectors[current_index]
            current_attribute_name = current_selector.attribute_name
            corresponding_Series = pandas_dataframe[current_attribute_name]
            final_result = final_result & current_selector.match(current_attribute_name, corresponding_Series)
            current_index = current_index + 1
        return final_result
    
    def is_refinement(self, refinement_candidate : 'Pattern', refinement_of_itself : bool) -> bool:
        """Method to check whether 'refinement_candidate' is a refinement of this (i.e., of 'self').
        
        :param refinement_candidate: pattern candidate to be a refinement of this (i.e., of 'self').
        :param refinement_of_itself: is a pattern a refinement of itself? Sometimes it may be better to assume yes and sometimes no. Therefore, if both patterns are equal, then this method returns the value of 'refinement_of_itself'.
        :return: whether 'refinement_candidate' is a refinement of this (i.e., 'self').
        """
        # TODO: implementing it more efficiently (i.e., not using sets), and verify whether it is actually more efficient. 
        self_as_set = set(self._list_of_selectors)
        refinement_candidate_as_set = set(refinement_candidate._list_of_selectors)
        if (len(self_as_set) > len(refinement_candidate_as_set)):
            return False
        elif self_as_set == refinement_candidate_as_set:
            return refinement_of_itself
        else:
            return self_as_set.issubset(refinement_candidate_as_set)
    
    @staticmethod
    def generate_from_str(input_str : str) -> 'Pattern':
        r"""Static method to generate a Pattern from a str.
        
        :param input_str: the str from which to generate the Pattern. We assume the format defined by one of the following regular expressions: (1) '\\[\\]' (empty Pattern), (2) '\\[selector\\]' (Pattern with only one selector), (3) '\\[selector(, selector)+\\]' (Pattern with more than one selector).
        :return: the Pattern generated from the str.
        """
        if type(input_str) is not str:
            raise TypeError("The type of the parameter 'input_str' must be 'str'.")
        if (input_str == "[]"):
            return Pattern([])
        else:
            list_of_selectors = []
            list_of_selectors_as_text = input_str[1:-1] # Delete the initial '[' and the final ']'.
            list_of_selectors_as_text_split = list_of_selectors_as_text.split(", ") # Separator: ', ' (comma and whitespce).
            for element in list_of_selectors_as_text_split:
                list_of_selectors.append(Selector.generate_from_str(element))
            return Pattern(list_of_selectors)
    
    def __eq__(self, other : 'Pattern') -> bool:
        if not isinstance(other, Pattern):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Pattern' class or of a subclass thereof.")
        if len(self._list_of_selectors) != len(other._list_of_selectors):
            return False # If they have different lengths, return False.
        for index in range(len(self._list_of_selectors)): # We check only the length of one list, because the length of the other list is the same.
            if (self._list_of_selectors[index] != other._list_of_selectors[index]):
                return False
        return True
    
    def __ne__(self, other : 'Pattern') -> bool:
        if not isinstance(other, Pattern):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Pattern' class or of a subclass thereof.")
        if len(self._list_of_selectors) != len(other._list_of_selectors):
            return True # If they have different lengths, return True.
        for index in range(len(self._list_of_selectors)): # We check only the length of one list, because the length of the other list is the same.
            if (self._list_of_selectors[index] != other._list_of_selectors[index]):
                return True
        return False
    
    def __str__(self) -> str:
        if len(self._list_of_selectors) == 0:
            return "[]"
        else:
            result = "["
            current_index = 0
            while (current_index < (len(self._list_of_selectors)-1)):
                result = result + str(self._list_of_selectors[current_index]) + ", "
                current_index = current_index + 1
            result = result + str(self._list_of_selectors[-1]) + "]" # -1 -> The last element.
            return result
    
    def __len__(self) -> int:
        return len(self._list_of_selectors)
    
    def __contains__(self, item : Selector) -> bool:
        if not isinstance(item, Selector):
            raise TypeError("You are using an object which is not an instance of the 'Selector' class or of a subclass thereof.")
        # We can use the bisection algorithm because the list is sorted.
        index = bisect_left(self._list_of_selectors, item)
        return (len(self._list_of_selectors) > 0) and (self._list_of_selectors[index] == item)
    
    def __iter__(self) -> Iterator[Selector]:
        return iter(self._list_of_selectors)
