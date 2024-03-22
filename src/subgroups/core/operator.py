# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the avaible operators which can be used by the selectors.
"""

from enum import Enum
from subgroups.exceptions import OperatorNotSupportedError
from pandas import Series

# Python annotations.
from typing import Union

class Operator(Enum):
    """This enumerator provides the available operators which can be used by the selectors.
    """
    
    EQUAL = 1
    NOT_EQUAL = 2
    LESS = 3
    GREATER = 4
    LESS_OR_EQUAL = 5
    GREATER_OR_EQUAL = 6
    
    def evaluate(self, left_element : Union[str, int, float, Series], right_element : Union[str, int, float, Series]) -> Union[bool, Series]:
        """Method to evaluate whether the expression (left_element self right_element) is True. IMPORTANT: if the operator is not supported between both elements, a TypeError exception is raised.
        
        :param left_element: the left element of the expression. It can be also of type 'pandas.Series' in order to allow comparisons with whole arrays.
        :param right_element: the right element of the expression. It can be also of type 'pandas.Series' in order to allow comparisons with whole arrays.
        :return: whether the expression (left_element self right_element) is True. In case of both elements are of type Series, a Series in which each element is of type bool is returned.
        """
        if (type(left_element) is not str) and (type(left_element) is not int) and (type(left_element) is not float) and (type(left_element) is not Series):
            raise TypeError("The type of the parameter 'left_element' must be 'str', 'int', 'float' or 'pandas.Series'.")
        if (type(right_element) is not str) and (type(right_element) is not int) and (type(right_element) is not float) and (type(right_element) is not Series):
            raise TypeError("The type of the parameter 'right_element' must be 'str', 'int', 'float' or 'pandas.Series'.")
        if self == Operator.EQUAL:
            return left_element == right_element
        elif self == Operator.NOT_EQUAL:
            return left_element != right_element
        elif self == Operator.LESS:
            return left_element < right_element
        elif self == Operator.GREATER:
            return left_element > right_element
        elif self == Operator.LESS_OR_EQUAL:
            return left_element <= right_element
        elif self == Operator.GREATER_OR_EQUAL:
            return left_element >= right_element
        else:
            raise OperatorNotSupportedError("This operator has not been added to the method 'evaluate'.")
    
    @staticmethod
    def generate_from_str(input_str : str) -> 'Operator':
        """Static method to generate an Operator from a str.
        
        :param input_str: the str from which to generate the Operator.
        :return: the Operator generated from the str.
        """
        if type(input_str) is not str:
            raise TypeError("The type of the parameter 'input_str' must be 'str'.")
        if input_str == "=":
            return Operator.EQUAL
        elif input_str == "!=":
            return Operator.NOT_EQUAL
        elif input_str == "<":
            return Operator.LESS
        elif input_str == ">":
            return Operator.GREATER
        elif input_str == "<=":
            return Operator.LESS_OR_EQUAL
        elif input_str == ">=":
            return Operator.GREATER_OR_EQUAL
        else:
            raise AttributeError("The parameter 'input_str' (with the value '" + input_str + "') does not match with any operator.")
    
    def __eq__(self, other : 'Operator') -> bool:
        if type(other) is not Operator:
            raise TypeError("You are making a comparison with an object whose type is not 'Operator'.")
        return self.value == other.value
    
    def __ne__(self, other : 'Operator') -> bool:
        if type(other) is not Operator:
            raise TypeError("You are making a comparison with an object whose type is not 'Operator'.")
        return self.value != other.value
    
    def __lt__(self, other : 'Operator') -> bool:
        if type(other) is not Operator:
            raise TypeError("You are making a comparison with an object whose type is not 'Operator'.")
        return self.value < other.value
    
    def __gt__(self, other : 'Operator') -> bool:
        if type(other) is not Operator:
            raise TypeError("You are making a comparison with an object whose type is not 'Operator'.")
        return self.value > other.value
    
    def __le__(self, other : 'Operator') -> bool:
        if type(other) is not Operator:
            raise TypeError("You are making a comparison with an object whose type is not 'Operator'.")
        return self.value <= other.value
    
    def __ge__(self, other : 'Operator') -> bool:
        if type(other) is not Operator:
            raise TypeError("You are making a comparison with an object whose type is not 'Operator'.")
        return self.value >= other.value
    
    def __str__(self) -> str:
        if self == Operator.EQUAL:
            return "="
        elif self == Operator.NOT_EQUAL:
            return "!="
        elif self == Operator.LESS:
            return "<"
        elif self == Operator.GREATER:
            return ">"
        elif self == Operator.LESS_OR_EQUAL:
            return "<="
        elif self == Operator.GREATER_OR_EQUAL:
            return ">="
        else:
            raise OperatorNotSupportedError("This operator does not have a string representation.")
    
    def __hash__(self) -> int:
        return hash(self.value)
