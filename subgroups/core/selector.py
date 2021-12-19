# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Selector'. A 'Selector' is an IMMUTABLE structure which contains an attribute name, an operator and a value.
"""

from subgroups.core.operator import Operator
from weakref import WeakValueDictionary
from pandas import Series

# Python annotations.
from typing import Union, ClassVar

class Selector(object):
    """This class represents a 'Selector'. A 'Selector' is an IMMUTABLE structure which contains an attribute name, an operator and a value.
    
    :param attribute_name: the attribute name. It must be a non-empty str.
    :param operator: the operator between the attribute name and the value. If the value is of type str, only EQUAL and NOT EQUAL operators are available.
    :param value: the value.
    """
    
    __slots__ = ("_attribute_name", "_operator", "_value", "__weakref__")
    
    # We implement a selector pool using Weak References.
    _dict_of_selectors : ClassVar[WeakValueDictionary[str, 'Selector']] = WeakValueDictionary()
    
    def __new__(cls, attribute_name : str, operator : Operator, value : Union[str, int, float]) -> 'Selector':
        if type(attribute_name) is not str:
            raise TypeError("The type of the parameter 'attribute_name' must be 'str'.")
        if type(operator) is not Operator:
            raise TypeError("The type of the parameter 'operator' must be 'Operator'.")
        if (type(value) is not str) and (type(value) is not int) and (type(value) is not float):
            raise TypeError("The type of the parameter 'value' must be 'str', 'int' or 'float'.")
        if (type(value) is str) and (operator != Operator.EQUAL) and (operator != Operator.NOT_EQUAL):
            raise ValueError("If the type of the parameter 'value' is 'str', only EQUAL and NOT EQUAL operators are available.")
        # The key of the dictionary '_dict_of_selectors' will be a string representation of the selector.
        # For this reason, we must check the value type in order to avoid errors.
        # - EXAMPLE: The selectors Selector("a", Operator.EQUAL, 23) and Selector("a", Operator.EQUAL, "23") must be different.
        # In order to solve this problem, we are going to add simple quotes to the values of type str, but not to the values of numeric types.
        value_for_dictionary_key = value
        if type(value_for_dictionary_key) is str:
            value_for_dictionary_key = "\'" + value_for_dictionary_key + "\'"
        key = attribute_name + " " + str(operator) + " " + str(value_for_dictionary_key)
        if key in Selector._dict_of_selectors:
            return Selector._dict_of_selectors[key]
        else:
            new_instance = super().__new__(cls)
            new_instance._attribute_name = attribute_name
            new_instance._operator = operator
            new_instance._value = value # In this point, we use the initial value (without the simple quotes).
            Selector._dict_of_selectors[key] = new_instance
            return new_instance
    
    def _get_attribute_name(self) -> str:
        return self._attribute_name
        
    def _get_operator(self) -> Operator:
        return self._operator
        
    def _get_value(self) -> Union[str, int, float]:
        return self._value
    
    attribute_name = property(_get_attribute_name, None, None, "The attribute name.")
    operator = property(_get_operator, None, None, "The operator between the attribute name and the value.")
    value = property(_get_value, None, None, "The value.")
    
    def match(self, attribute_name : str, value : Union[str, int, float, Series]) -> Union[bool, Series]:
        """Method to check whether the parameters 'attribute_name' and 'value' match with the selector. In this case, "match" means that the expression ((attribute_name == self.attribute_name) and (value self.operator self.value)) is True. IMPORTANT: if the selector operator is not supported between value and self.value, a TypeError exception is raised.
        
        :param attribute_name: the attribute name which is compared with self.attribute_name.
        :param value: the value which is compared with self.value. The value can be also of type 'pandas.Series' in order to allow comparisons with whole arrays.
        :return: whether the parameters 'attribute_name' and 'value' match with the selector.
        """
        if type(attribute_name) is not str:
            raise TypeError("The type of the parameter 'attribute_name' must be 'str'.")
        if (type(value) is not str) and (type(value) is not int) and (type(value) is not float) and (type(value) is not Series):
            raise TypeError("The type of the parameter 'value' must be 'str', 'int', 'float' or 'pandas.Series'.")
        # Evaluate the complete expression and return the result.
        return (attribute_name == self.attribute_name) and (self.operator.evaluate(value, self.value))
    
    @staticmethod
    def generate_from_str(input_str : str) -> 'Selector':
        """Static method to generate a Selector from a str.
        
        :param input_str: the str from which to generate the Selector. We assume the following format: <attribute_name><whitespace><operator><whitespace><value>. Be careful with the whitespaces: (1) each part of the selector must be separated by only one whitespace and (2) whitespaces at the left side of the str or at the right side of the str are not allowed.
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
    
    def __eq__(self, other : 'Selector') -> bool:
        if not isinstance(other, Selector):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Selector' class or of a subclass thereof.")
        return (self._attribute_name == other._attribute_name) and (self._operator == other._operator) and (self._value == other._value)
    
    def __ne__(self, other : 'Selector') -> bool:
        if not isinstance(other, Selector):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Selector' class or of a subclass thereof.")
        return (self._attribute_name != other._attribute_name) or (self._operator != other._operator) or (self._value != other._value)
    
    def __lt__(self, other : 'Selector') -> bool:
        if not isinstance(other, Selector):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Selector' class or of a subclass thereof.")
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
    
    def __gt__(self, other : 'Selector') -> bool:
        if not isinstance(other, Selector):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Selector' class or of a subclass thereof.")
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
    
    def __le__(self, other : 'Selector') -> bool:
        if not isinstance(other, Selector):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Selector' class or of a subclass thereof.")
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
    
    def __ge__(self, other : 'Selector') -> bool:
        if not isinstance(other, Selector):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Selector' class or of a subclass thereof.")
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
    
    def __repr__(self) -> str:
        return str(self)
    
    def __str__(self) -> str:
        # When transforming the Selector to str, we have to be able to distinguish the value type (i.e., whether it is str or numeric).
        self_value = self._value
        if type(self_value) is str:
            self_value = "\'" + self_value + "\'"
        return self._attribute_name + " " + str(self._operator) + " " + str(self_value)
    
    def __hash__(self) -> int:
        return hash(str(self))
