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
    
    :type description: Pattern
    :param description: a Pattern.
    :type target: Selector
    :param target: a Selector.
    """
    
    __slots__ = "_description", "_target" 
    
    def __init__(self, description, target):
        if not isinstance(description, Pattern):
            raise TypeError("The type of the parameter 'description' must be 'Pattern'.")
        if not isinstance(target, Selector):
            raise TypeError("The type of the parameter 'target' must be 'Selector'.")
        self._description = description
        self._target = target
    
    def copy(self):
        """Method to copy the Subgroup.
        :rtype: Subgroup
        :return: the copy of the Subgroup.
        """
        # We create a copy of the pattern to avoid aliasing between subgroups.
        return Subgroup(self._description.copy(), self._target)
    
    def _get_description(self):
        return self._description
    
    description = property(_get_description, None, None, "The description.")
    
    def _get_target(self):
        return self._target
    
    target = property(_get_target, None, None, "The target variable of interest.")
    
    def filter(self, pandas_dataframe, use_description=True, use_target=True):
        """Method to filter a pandas DataFrame, retrieving only the rows covered by the subgroup.
        
        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: the DataFrame which is filtered.
        :type use_description: bool
        :param use_description: whether the subgroup description is used in the filtering process. By default, True.
        :type use_target: bool
        :param use_target: whether the subgroup target is used in the filtering process. By default, True.
        :rtype: tuple
        :return: a tuple of the form: (DataFrame, tp, fp, TP, FP). The first element is the DataFrame obtained after the filtering process. The other elements are the following subgroup parameters: the true positives tp (rows covered by the description and the target), the false positives fp (rows covered by the description but not by the target), the True Positives TP (rows covered by the target) and the False Positives FP (rows not covered by the target). IMPORTANT: the subgroup parameters are obtained with the complete subgroup (i.e., using the description and using the target). This means that, for a given DataFrame, they always have the same value no matter the values of the parameters 'use_description' and 'use_target'.
        """
        if not isinstance(pandas_dataframe, DataFrame):
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'pandas.Dataframe'.")
        if type(use_description) is not bool:
            raise TypeError("The type of the parameter 'use_description' must be 'bool'.")
        if type(use_target) is not bool:
            raise TypeError("The type of the parameter 'use_target' must be 'bool'.")
        pandas_DataFrame__all_except_the_target_attribute = pandas_dataframe[pandas_dataframe.columns.drop(self._target._attribute_name)]
        pandas_Series__target_attribute = pandas_dataframe[self._target._attribute_name]
        description_is_contained = self._description.is_contained(pandas_DataFrame__all_except_the_target_attribute)
        target_match = self._target.match(self._target._attribute_name, pandas_Series__target_attribute)
        bool_Series_description_is_contained_AND_target_match = description_is_contained & target_match
        tp = (bool_Series_description_is_contained_AND_target_match).sum()
        fp = (description_is_contained & (~ target_match)).sum()
        TP = target_match.sum()
        FP = len(pandas_dataframe) - TP
        if (use_description) and (use_target):
            return (pandas_dataframe[bool_Series_description_is_contained_AND_target_match], tp, fp, TP, FP)
        elif (use_description) and (not use_target):
            return (pandas_dataframe[description_is_contained], tp, fp, TP, FP)
        elif (not use_description) and (use_target):
            return (pandas_dataframe[target_match], tp, fp, TP, FP)
        else:
            return (pandas_dataframe, tp, fp, TP, FP)
    
    @staticmethod
    def generate_from_str(input_str):
        """Static method to generate a Subgroup from a str.
        
        :type input_str: str
        :param input_str: the str from which to generate the Subgroup. We assume the format defined by the following regular expressions: 'Description: <pattern>, Target: <selector>'. The format of <selector> and <pattern> is defined by their corresponding 'generate_from_str' methods.
        :rtype: Subgroup
        :return: the Subgroup generated from the str.
        """
        if type(input_str) is not str:
            raise TypeError("The type of the parameter 'input_str' must be 'str'.")
        input_str_split = input_str.split(", Target: ")
        target = Selector.generate_from_str(input_str_split[1])
        description = Pattern.generate_from_str(input_str_split[0][13:]) # [13:] -> Delete the initial string "Description: ".
        return Subgroup(description, target)
    
    def __eq__(self, other):
        if not isinstance(other, Subgroup):
            raise TypeError("The type of the parameter must be 'Subgroup'.")
        return (self._description == other._description) and (self._target == other._target)
    
    def __ne__(self, other):
        if not isinstance(other, Subgroup):
            raise TypeError("The type of the parameter must be 'Subgroup'.")
        return (self._description != other._description) or (self._target != other._target)
    
    def __str__(self):
        return "Description: " + str(self.description) + ", Target: " + str(self.target)
