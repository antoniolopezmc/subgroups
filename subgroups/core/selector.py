# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Selector'. A 'Selector' is an IMMUTABLE structure which contains an attribute name, an operator and a value.
"""

from enum import Enum
from subgroups.core.operator import Operator

class Selector(tuple):
    """This class represents a 'Selector'. A 'Selector' is an IMMUTABLE structure which contains an attribute name, an operator and a value.
    
    :type attribute_name: str
    :param attribute_name: Attribute name. It must be a non-empty str.
    :type operator: str
    :param operator: The operator between the attribute name and the value. If the value is of type str, only EQUAL and NOT EQUAL operators are available.
    :type value: str, int or float
    :param value: Value.
    """
    
    # The selectors are stored in a selector pool. Two selectors with the same attribute name, the same operator and the same value are the same object.
    _dict_of_selectors = dict()
    
    def __new__(cls, attribute_name, operator, value):
        if type(attribute_name) is not str:
            raise TypeError("The parameter 'attribute_name' is not of type str.")
        if not isinstance(operator, Enum):
            raise TypeError("The parameter 'operator' is not a valid Operator.")
        if (type(value) is not str) and (type(value) is not int) and (type(value) is not float):
            raise TypeError("The parameter 'value' is not of types str, int or float.")
        if (type(value) is str) and (operator != Operator.EQUAL) and (operator != Operator.NOT_EQUAL):
            raise ValueError("If the parameter 'value' is of type str, only EQUAL and NOT EQUAL operators are available.")
        if (attribute_name not in Selector._dict_of_selectors):
            Selector._dict_of_selectors[attribute_name] = dict()
            Selector._dict_of_selectors[attribute_name][operator] = dict()
            new_instance = super().__new__(cls, (attribute_name, operator, value))
            new_instance._tuple = (attribute_name, operator, value)
            Selector._dict_of_selectors[attribute_name][operator][value] = new_instance
            return new_instance
        elif (operator not in Selector._dict_of_selectors[attribute_name]):
            Selector._dict_of_selectors[attribute_name][operator] = dict()
            new_instance = super().__new__(cls, (attribute_name, operator, value))
            new_instance._tuple = (attribute_name, operator, value)
            Selector._dict_of_selectors[attribute_name][operator][value] = new_instance
            return new_instance
        elif (value not in Selector._dict_of_selectors[attribute_name][operator]):
            new_instance = super().__new__(cls, (attribute_name, operator, value))
            new_instance._tuple = (attribute_name, operator, value)
            Selector._dict_of_selectors[attribute_name][operator][value] = new_instance
            return new_instance
        else:
            return Selector._dict_of_selectors[attribute_name][operator][value]
    
    def __del__(self):
        self_attribute_name = self.attribute_name
        self_operator = self.operator
        self_value = self.value
        # 1. Delete the key (self_value) and the value (instance) stored in the dictionary _dict_of_selectors[self_attribute_name][self_operator].
        del Selector._dict_of_selectors[self_attribute_name][self_operator][self_value]
        # 2. If the dictionary _dict_of_selectors[self_attribute_name][self_operator] is empty, delete the key (self_operator) and the value (dictionary) stored in the dictionary _dict_of_selectors[self_attribute_name].
        if (len(Selector._dict_of_selectors[self_attribute_name][self_operator]) == 0):
            del Selector._dict_of_selectors[self_attribute_name][self_operator]
            # 3. If the dictionary _dict_of_selectors[self_attribute_name] is empty, delete the key (self_attribute_name) and the value (dictionary) stored in the dictionary _dict_of_selectors.
            if (len(Selector._dict_of_selectors[self_attribute_name]) == 0):
                del Selector._dict_of_selectors[self_attribute_name]
    
    def _get_attribute_name(self):
        return self[0]
    
    attribute_name = property(_get_attribute_name, None, None, "Attribute name.")
    
    def _get_operator(self):
        return self[1]
    
    operator = property(_get_operator, None, None, "The operator between the attribute name and the value.")
    
    def _get_value(self):
        return self[2]
    
    value = property(_get_value, None, None, "Value.")
    
    def match(self, attribute_name, value):
        """Method to evaluate whether the parameters 'attribute_name' and 'value' match with the selector. In this case, "match" means that the expression ((attribute_name == self.attribute_name) and (value self.operator self.value)) is True.
        
        :type attribute_name: str
        :param attribute_name: The attribute name which is compared with self.attribute_name.
        :type value: str, int or float
        :param value: The value which is compared with self.value.
        :rtype: bool
        :return: Whether the parameters 'attribute_name' and 'value' match with the selector.
        """
        if type(attribute_name) is not str:
            raise TypeError("The parameter 'attribute_name' is not of type str.")
        if (type(value) is not str) and (type(value) is not int) and (type(value) is not float):
            raise TypeError("The parameter 'value' is not of types str, int or float.")
        # Evaluate the complete expression and return the result.
        return (attribute_name == self.attribute_name) and (self.operator.evaluate(value, self.value))
    
    def __eq__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The parameter is not of type Selector.")
        return (self[0] == other[0]) and (self[1] == other[1]) and (self[2] == other[2])
    
    def __ne__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The parameter is not of type Selector.")
        return (self[0] != other[0]) or (self[1] != other[1]) or (self[2] != other[2])

    def __lt__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The parameter is not of type Selector.")
        if (self[0] != other[0]):
            return self[0] < other[0]
        elif (self[1] != other[1]):
            return self[1] < other[1]
        elif (self[2] != other[2]):
            try:
                return self[2] < other[2]
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '<' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self[2]) < str(other[2])
        return False
    
    def __gt__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The parameter is not of type Selector.")
        if (self[0] != other[0]):
            return self[0] > other[0]
        elif (self[1] != other[1]):
            return self[1] > other[1]
        elif (self[2] != other[2]):
            try:
                return self[2] > other[2]
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '>' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self[2]) > str(other[2])
        return False
    
    def __le__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The parameter is not of type Selector.")
        if (self[0] != other[0]):
            return self[0] <= other[0]
        elif (self[1] != other[1]):
            return self[1] <= other[1]
        elif (self[2] != other[2]):
            try:
                return self[2] <= other[2]
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '<=' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self[2]) <= str(other[2])
        return True
    
    def __ge__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The parameter is not of type Selector.")
        if (self[0] != other[0]):
            return self[0] >= other[0]
        elif (self[1] != other[1]):
            return self[1] >= other[1]
        elif (self[2] != other[2]):
            try:
                return self[2] >= other[2]
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '>=' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self[2]) >= str(other[2])
        return True
    
    def __str__(self):
        self_value = self.value
        if type(self.value) is str:
            self_value = "\'" + self_value + "\'"
        return self[0] + " " + str(self[1]) + " " + str(self_value)
    
    def __hash__(self):
        return super().__hash__()
