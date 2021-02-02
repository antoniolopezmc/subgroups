# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the avaible operators which can be used by the selectors.
"""

from enum import Enum

class Operator(Enum):
    
    """This enumerator provides the available operators which can be used by the selectors.
    """
    
    EQUAL = "="
    NOT_EQUAL = "!="
    LESS = "<"
    GREATER = ">"
    LESS_OR_EQUAL = "<="
    GREATER_OR_EQUAL = ">="
    
    def __eq__(self, other):
        if not isinstance(other, Operator):
            print("The parameter is not of type Operator.")
        return self.value == other.value
    
    def __ne__(self, other):
        if not isinstance(other, Operator):
            print("The parameter is not of type Operator.")
        return self.value != other.value
    
    def __lt__(self, other):
        if not isinstance(other, Operator):
            print("The parameter is not of type Operator.")
        return self.value < other.value
    
    def __gt__(self, other):
        if not isinstance(other, Operator):
            print("The parameter is not of type Operator.")
        return self.value > other.value
    
    def __le__(self, other):
        if not isinstance(other, Operator):
            print("The parameter is not of type Operator.")
        return self.value <= other.value
    
    def __ge__(self, other):
        if not isinstance(other, Operator):
            print("The parameter is not of type Operator.")
        return self.value >= other.value
    
    def __hash__(self):
        return hash(self.value)
