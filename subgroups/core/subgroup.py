# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a 'Subgroup'. A 'Subgroup' has a description (Pattern) and a target variable of interest (Selector).
"""

from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern
from pandas import DataFrame, Series

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
    
    def filter(self, pandas_dataframe : DataFrame) -> tuple[Series, Series, Series]:
        """Method to filter a pandas DataFrame, retrieving only certain information related to this subgroup.
        
        :param pandas_dataframe: the DataFrame which is filtered. IMPORTANT: If an attribute name of a selector of the subgroup is not in the pandas.DataFrame passed by parameter, a KeyError exception is raised.
        :return: a tuple of the form: (Series, Series, Series). \
It is formed by the following elements: \
(1) a pandas Series of booleans of the same size as pandas_dataframe indicating whether rows are covered by the description and the target, \
(2) a pandas Series of booleans of the same size as pandas_dataframe indicating whether rows are covered by the description but not by the target, and \
(3) a pandas Series of booleans of the same size as pandas_dataframe indicating whether rows are covered by the target.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'pandas.Dataframe'.")
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
        # Rows that do not match with the target and in which the description is contained.
        bool_Series_description_is_contained_AND_target_do_not_match = description_is_contained & (~target_match)
        # Return depending on the function parameters specified above.
        return (bool_Series_description_is_contained_AND_target_match, bool_Series_description_is_contained_AND_target_do_not_match, target_match)
    
    def is_refinement(self, refinement_candidate : 'Subgroup', refinement_of_itself : bool) -> bool:
        """Method to check whether 'refinement_candidate' is a refinement of this (i.e., of 'self'). A subgroup Y is a refinements of other subgroup X, if the description of Y is a refinement of the description of X, and the targets are equal.
        
        :param refinement_candidate: subgroup candidate to be a refinement of this (i.e., of 'self').
        :param refinement_of_itself: is a pattern a refinement of itself (in this case, the description of a subgroup)? Sometimes it may be better to assume yes and sometimes no. Therefore, if both subgroups are equal (i.e., the descriptions of both subgroups and the targets), then this method returns the value of 'refinement_of_itself'.
        :return: whether 'refinement_candidate' is a refinement of this (i.e., 'self').
        """
        return self.description.is_refinement(refinement_candidate.description, refinement_of_itself) and (self.target == refinement_candidate.target)
    
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
    
    
    def match_element(self, transaction, index_dict) :
        """Method to check if an example (also called element, row or object of a database) is covered by a subgroup. Unlike with the coversTransaction method, the input is named tuple, not a pandas.DataFrame
    
        :type transaction: tuple
        :param transaction: Element of the database (row) that will be checked.
        :type index_dict: dict
        :param index_dict: python dictionary that matches the pandas indexing (names of the columns) with the integer indexing
        :rtype: bool
        :return: True if the subgroup covers the transaction. False otherwise
        """
        
        '''
        # No need to check the parameters, it will be done by the Selectors
        if not isinstance(transaction, tuple) :
            raise TypeError("Parameter 'transaction' must be a tuple.")
        for i in transaction :
            if type(i) is not int and type(i) is not float and type(i) is not str :
                raise TypeError("Parameter 'transaction': the elements of the tuple must be integer, float or string.")
        
        if type(index_dict) is not dict :
            raise TypeError("Parameter 'index_dict' must be a python dictionary.")
        # Check if each key match just one integer index
        if len(transaction) != len(index_dict) :
            raise TypeError("Parameter 'index_dict': each key does not a map a unique integer value (transaction and index_dict have differente lenght).")
        index_int_list = [*range(0,len(transaction),1)]
        for i in index_dict :
            try: 
                index_int_list.remove(index_dict[i])
            except ValueError as e:
                raise TypeError("Parameter 'index_dict': each key does not a map a unique integer value (couldn't match the key "+ i +" with an integer value).")
        '''
                
        if not self._get_description().match_element(transaction, index_dict) :
            return False
        if not self._get_target().match(self._get_target()._get_attribute_name(), transaction[index_dict[self._get_target()._get_attribute_name()]]) :
            return False
        return True   
    
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
