# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Pattern'. A 'Pattern' is a sorted list of non-repeated selectors.
"""

from subgroups.core.selector import Selector
import bisect

class Pattern(object):
    """This class represents a 'Pattern'. A 'Pattern' is a sorted list of non-repeated selectors.
    
    :type list_of_selectors: list[Selector]
    :param list_of_selectors: a list of selectors. IMPORTANT: we assume that the list only contains selectors.
    """
    
    __slots__ = "_list_of_selectors"
    
    def __init__(self, list_of_selectors):
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
    
    def add_selector(self, selector):
        """Method to add a selector to the pattern. If the selector already exists, this method does nothing.
        
        :type selector: Selector
        :param selector: the selector which is added.
        """
        if not isinstance(selector, Selector):
            raise TypeError("The type of the parameter 'selector' must be 'Selector'.")
        # We can use the bisection algorithm because the list is sorted.
        index = bisect.bisect_left(self._list_of_selectors, selector)
        if (index == len(self._list_of_selectors)): # The list is empty OR the element will be inserted in the right side of the list.
            self._list_of_selectors.append(selector)
        elif (self._list_of_selectors[index] != selector): # The list is not empty AND the element will not be inserted in the right side of the list.
            self._list_of_selectors.insert(index, selector)
    
    def remove_selector(self, selector):
        """Method to remove a selector from the pattern. If the selector does not exist, this method does nothing.
        
        :type selector: Selector
        :param selector: the selector which is removed.
        """
        if not isinstance(selector, Selector):
            raise TypeError("The type of the parameter 'selector' must be 'Selector'.")
        # We can use the bisection algorithm because the list is sorted.
        index = bisect.bisect_left(self._list_of_selectors, selector)
        if (index < len(self._list_of_selectors)) and (self._list_of_selectors[index] == selector):
            self._list_of_selectors.pop(index)
    
    def remove_selector_by_index(self, index):
        """Method to remove a selector from the pattern by index. If the index is out of range, an 'IndexError' exception is raised.
        
        :type index: int
        :param index: the index which is used.
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        self._list_of_selectors.pop(index)
    
    def get_selector(self, index):
        """Method to get a selector from the pattern by index. If the index is out of range, an 'IndexError' exception is raised.
        
        :type index: int
        :param index: the index which is used.
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._list_of_selectors[index]
    
    def copy(self):
        """Method to copy the Pattern.
        
        :rtype: Pattern
        :return: the copy of the Pattern WITH THE SAME SELECTORS (THE SAME OBJECTS). This method does not copy the selectors of the list (it is not needed because the selectors are immutable).
        """
        new_list_of_selectors = self._list_of_selectors.copy()
        new_pattern = Pattern([]) # The list of selectors is already sorted. It is not needed to sort it in the __init__ method.
        new_pattern._list_of_selectors = new_list_of_selectors
        return new_pattern
    
    @staticmethod
    def generate_from_str(input_str):
        """Static method to generate a Pattern from a str.
        
        :type input_str: str
        :param input_str: the str from which to generate the Pattern. We assume the format defined by the following regular expressions: (1) '\[\]' (empty Pattern), (2) '\[selector\]' (Pattern with only one selector) or (3) '\[selector(, selector)+\]' (Pattern with more than one selector).
        :rtype: Pattern
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
    
    def __eq__(self, other):
        if not isinstance(other, Pattern):
            raise TypeError("The type of the parameter must be 'Pattern'.")
        if len(self._list_of_selectors) != len(other._list_of_selectors):
            return False # If they have different lengths, return False.
        for index in range(len(self._list_of_selectors)): # We check only the length of one list, because the length of the other list is the same.
            if (self._list_of_selectors[index] != other._list_of_selectors[index]):
                return False
        return True
    
    def __ne__(self, other):
        if not isinstance(other, Pattern):
            raise TypeError("The type of the parameter must be 'Pattern'.")
        if len(self._list_of_selectors) != len(other._list_of_selectors):
            return True # If they have different lengths, return True.
        for index in range(len(self._list_of_selectors)): # We check only the length of one list, because the length of the other list is the same.
            if (self._list_of_selectors[index] != other._list_of_selectors[index]):
                return True
        return False
    
    def __str__(self):
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
    
    def __len__(self):
        return len(self._list_of_selectors)
    
    def __contains__(self, item):
        if not isinstance(item, Selector):
            raise TypeError("The type of the item must be 'Selector'.")
        # We can use the bisection algorithm because the list is sorted.
        index = bisect.bisect_left(self._list_of_selectors, item)
        return (len(self._list_of_selectors) > 0) and (self._list_of_selectors[index] == item)
    
    def __iter__(self):
        return iter(self._list_of_selectors)
