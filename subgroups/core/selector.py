# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Selector'. A 'Selector' is an IMMUTABLE structure which contains an attribute name, an operator and a value.
"""

from subgroups import exceptions
from subgroups.core.operator import Operator

class Selector(object):
    """This class represents a 'Selector'. A 'Selector' is an IMMUTABLE structure which contains an attribute name, an operator and a value.
    
    :type attribute_name: str
    :param attribute_name: the attribute name. It must be a non-empty str.
    :type operator: str
    :param operator: the operator between the attribute name and the value. If the value is of type str, only EQUAL and NOT EQUAL operators are available.
    :type value: str, int or float
    :param value: the value.
    """
    
    __slots__ = "_attribute_name", "_operator", "_value"
    
    def __init__(self, attribute_name, operator, value):
        if type(attribute_name) is not str:
            raise TypeError("The type of the parameter 'attribute_name' must be 'str'.")
        if not isinstance(operator, Operator):
            raise TypeError("The parameter 'operator' is not a valid Operator.")
        if (type(value) is not str) and (type(value) is not int) and (type(value) is not float):
            raise TypeError("The type of the parameter 'value' must be 'str', 'int' or 'float'.")
        if (type(value) is str) and (operator != Operator.EQUAL) and (operator != Operator.NOT_EQUAL):
            raise ValueError("If the type of the parameter 'value' is 'str', only EQUAL and NOT EQUAL operators are available.")
        self._attribute_name = attribute_name
        self._operator = operator
        self._value = value
    
    def _get_attribute_name(self):
        return self._attribute_name
    
    attribute_name = property(_get_attribute_name, None, None, "Attribute name.")
    
    def _get_operator(self):
        return self._operator
    
    operator = property(_get_operator, None, None, "The operator between the attribute name and the value.")
    
    def _get_value(self):
        return self._value
    
    value = property(_get_value, None, None, "Value.")
    
    def match(self, attribute_name, value):
        """Method to evaluate whether the parameters 'attribute_name' and 'value' match with the selector. In this case, "match" means that the expression ((attribute_name == self.attribute_name) and (value self.operator self.value)) is True.
        
        :type attribute_name: str
        :param attribute_name: the attribute name which is compared with self.attribute_name.
        :type value: str, int or float
        :param value: the value which is compared with self.value.
        :rtype: bool
        :return: whether the parameters 'attribute_name' and 'value' match with the selector.
        """
        if type(attribute_name) is not str:
            raise TypeError("The type of the parameter 'attribute_name' must be 'str'.")
        if (type(value) is not str) and (type(value) is not int) and (type(value) is not float):
            raise TypeError("The type of the parameter 'value' must be 'str', 'int' or 'float'.")
        # Evaluate the complete expression and return the result.
        return (attribute_name == self.attribute_name) and (self.operator.evaluate(value, self.value))
    
    @staticmethod
    def generate_from_str(input_str):
        """Static method to generate a Selector from a str.
        
        :type input_str: str
        :param input_str: the str from which to generate the Selector. We assume the following format: <attribute_name><whitespace><operator><whitespace><value>. Be careful with the whitespaces: (1) each part of the selector must be separated by only one whitespace and (2) whitespaces at the left side of the str or at the right side of the str are not allowed.
        :rtype: Selector
        :return: the Selector generated from the str.
        """
        if type(input_str) is not str:
            raise TypeError("The type of the parameter 'input_str' must be 'str'.")
        input_str_split = input_str.split(" ", 2) # Split the input str in 3 substrings using the space as a separator. The third part could have spaces.
        new_operator = Operator.generate_from_str(input_str_split[1])
        # We have to check the format of the value (i.e., input_str_split[2]).
        if (input_str_split[2][0] == input_str_split[2][-1] == "\'") or (input_str_split[2][0] == input_str_split[2][-1] == "\""): # The value is of type str.
            return Selector(input_str_split[0], new_operator, input_str_split[2][1:-1]) # [1:-1] -> Delete the characters "\'" or "\"".
        else: # The value could be of types int or float.
            try:
                if ("." in input_str_split[2]):
                    return Selector(input_str_split[0], new_operator, float(input_str_split[2]))
                else:
                    return Selector(input_str_split[0], new_operator, int(input_str_split[2]))
            except ValueError: # If we cannot transform to int or float, we return the value as a str.
                return Selector(input_str_split[0], new_operator, input_str_split[2])
    
    def __eq__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The type of the parameter must be 'Selector'.")
        return (self._attribute_name == other._attribute_name) and (self._operator == other._operator) and (self._value == other._value)
    
    def __ne__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The type of the parameter must be 'Selector'.")
        return (self._attribute_name != other._attribute_name) or (self._operator != other._operator) or (self._value != other._value)
    
    def __lt__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The type of the parameter must be 'Selector'.")
        if (self._attribute_name != other._attribute_name):
            return self._attribute_name < other._attribute_name
        elif (self._operator != other._operator):
            return self._operator < other._operator
        elif (self._value != other._value):
            try:
                return self._value < other._value
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '<' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self._value) < str(other._value)
        return False
    
    def __gt__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The type of the parameter must be 'Selector'.")
        if (self._attribute_name != other._attribute_name):
            return self._attribute_name > other._attribute_name
        elif (self._operator != other._operator):
            return self._operator > other._operator
        elif (self._value != other._value):
            try:
                return self._value > other._value
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '>' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self._value) > str(other._value)
        return False
    
    def __le__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The type of the parameter must be 'Selector'.")
        if (self._attribute_name != other._attribute_name):
            return self._attribute_name <= other._attribute_name
        elif (self._operator != other._operator):
            return self._operator <= other._operator
        elif (self._value != other._value):
            try:
                return self._value <= other._value
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '<=' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self._value) <= str(other._value)
        return True
    
    def __ge__(self, other):
        if not isinstance(other, Selector):
            raise TypeError("The type of the parameter must be 'Selector'.")
        if (self._attribute_name != other._attribute_name):
            return self._attribute_name >= other._attribute_name
        elif (self._operator != other._operator):
            return self._operator >= other._operator
        elif (self._value != other._value):
            try:
                return self._value >= other._value
            except TypeError:
                # If one value is of type str and the other is of any numeric type, the operator '>=' is not supported and a TypeError exception is raised.
                # - In this case, we transform to str and compare them.
                return str(self._value) >= str(other._value)
        return True
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        self_value = self._value
        if type(self._value) is str:
            self_value = "\'" + self_value + "\'"
        return self._attribute_name + " " + str(self._operator) + " " + str(self_value)
    
    def __hash__(self):
        return hash(str(self))
