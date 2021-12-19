# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Subgroup'. A 'Subgroup' has a description (Pattern) and a target variable of interest (Selector).
"""

from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern
from pandas import DataFrame

class Subgroup(object):
    """This class represents a 'Subgroup'. A 'Subgroup' has a description (Pattern) and a target variable of interest (Selector).
    
    :param description: a Pattern.
    :param target: a Selector.
    """
    
    __slots__ = ("_description", "_target")
    
    def __init__(self, description : Pattern, target : Selector):
        if not isinstance(description, Pattern):
            raise TypeError("The parameter 'description' must be an instance of the 'Pattern' class or of a subclass thereof.")
        if not isinstance(target, Selector):
            raise TypeError("The parameter 'target' must be an instance of the 'Selector' class or of a subclass thereof.")
        self._description = description
        self._target = target
    
    def copy(self) -> 'Subgroup':
        """Method to copy the Subgroup.

        :return: the copy of the Subgroup.
        """
        # We create a copy of the pattern to avoid aliasing between subgroups.
        return Subgroup(self._description.copy(), self._target)
    
    def _get_description(self) -> Pattern:
        return self._description
    
    def _get_target(self) -> Selector:
        return self._target
    
    description = property(_get_description, None, None, "The description.")
    target = property(_get_target, None, None, "The target variable of interest.")
    
    def filter(self, pandas_dataframe : DataFrame, use_description : bool = True, use_target : bool = True) -> tuple[DataFrame, int, int, int, int]:
        """Method to filter a pandas DataFrame, retrieving only the rows covered by the subgroup.
        
        :param pandas_dataframe: the DataFrame which is filtered.
        :param use_description: whether the subgroup description is used in the filtering process. By default, True.
        :param use_target: whether the subgroup target is used in the filtering process. By default, True.
        :return: a tuple of the form: (DataFrame, tp, fp, TP, FP). The first element is the DataFrame obtained after the filtering process. The other elements are the following subgroup parameters: the true positives tp (rows covered by the description and the target), the false positives fp (rows covered by the description but not by the target), the true population TP (rows covered by the target) and the false population FP (rows not covered by the target). IMPORTANT: the subgroup parameters are obtained with the complete subgroup (i.e., using the description and using the target). This means that, for a given DataFrame, they always have the same value no matter the values of the parameters 'use_description' and 'use_target'.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'pandas.Dataframe'.")
        if type(use_description) is not bool:
            raise TypeError("The type of the parameter 'use_description' must be 'bool'.")
        if type(use_target) is not bool:
            raise TypeError("The type of the parameter 'use_target' must be 'bool'.")
        # Original dataframe without the target attribute.
        pandas_DataFrame__all_except_the_target_attribute = pandas_dataframe[pandas_dataframe.columns.drop(self._target._attribute_name)]
        # Only the target attribute (in a Series).
        pandas_Series__target_attribute = pandas_dataframe[self._target._attribute_name]
        # We check the rows in which the description is contained.
        description_is_contained = self._description.is_contained(pandas_DataFrame__all_except_the_target_attribute)
        # We check the rows that match with the target.
        target_match = self._target.match(self._target._attribute_name, pandas_Series__target_attribute)
        # Rows that match with the target and in which the description is contained.
        bool_Series_description_is_contained_AND_target_match = description_is_contained & target_match
        # Compute the subgroup parameters.
        tp = (bool_Series_description_is_contained_AND_target_match).sum()
        fp = (description_is_contained & (~ target_match)).sum()
        TP = target_match.sum()
        FP = len(pandas_dataframe) - TP
        # Return depending on the function parameters specified above.
        if (use_description) and (use_target):
            return (pandas_dataframe[bool_Series_description_is_contained_AND_target_match], tp, fp, TP, FP)
        elif (use_description) and (not use_target):
            return (pandas_dataframe[description_is_contained], tp, fp, TP, FP)
        elif (not use_description) and (use_target):
            return (pandas_dataframe[target_match], tp, fp, TP, FP)
        else:
            return (pandas_dataframe, tp, fp, TP, FP)
    
    @staticmethod
    def generate_from_str(input_str : str) -> 'Subgroup':
        """Static method to generate a Subgroup from a str.
        
        :param input_str: the str from which to generate the Subgroup. We assume the format defined by the following regular expressions: 'Description: <pattern>, Target: <selector>'. The format of <selector> and <pattern> is defined by their corresponding 'generate_from_str' methods.
        :return: the Subgroup generated from the str.
        """
        if type(input_str) is not str:
            raise TypeError("The type of the parameter 'input_str' must be 'str'.")
        input_str_split = input_str.split(", Target: ")
        target = Selector.generate_from_str(input_str_split[1])
        description = Pattern.generate_from_str(input_str_split[0][13:]) # [13:] -> Delete the initial string "Description: ".
        return Subgroup(description, target)
    
    def __eq__(self, other : 'Subgroup') -> bool:
        if not isinstance(other, Subgroup):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Subgroup' class or of a subclass thereof.")
        return (self._description == other._description) and (self._target == other._target)
    
    def __ne__(self, other : 'Subgroup') -> bool:
        if not isinstance(other, Subgroup):
            raise TypeError("You are making a comparison with an object which is not an instance of the 'Subgroup' class or of a subclass thereof.")
        return (self._description != other._description) or (self._target != other._target)
    
    def __str__(self) -> str:
        return "Description: " + str(self.description) + ", Target: " + str(self.target)
