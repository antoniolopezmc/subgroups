# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Vertical List data structure used in the VLSD algorithm.
"""

from pandas import Index
from subgroups.quality_measures._base import QualityMeasure

class VerticalList(object):
    """This class represents a Vertical List.
    
    :type list_of_selectors: list[Selector]
    :param list_of_selectors: the list of selectors represented by the vertical list.
    :type sequence_of_instances_tp: pandas.Index
    :param sequence_of_instances_tp: the sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors') and also by the target. The number of elements in this sequence would be the true positives tp of the equivalent subgroup with the same list of selectors and with the same target.
    :type sequence_of_instances_fp: pandas.Index
    :param sequence_of_instances_fp: the sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target. The number of elements in this sequence would be the false positives fp of the equivalent subgroup with the same list of selectors and with the same target.
    :type quality_value: int or float.
    :param quality_value: the vertical list quality value.
    """
    
    __slots__ = "_list_of_selectors", "_sequence_of_instances_tp", "_sequence_of_instances_fp", "_quality_value"
    
    def __init__(self, list_of_selectors, sequence_of_instances_tp, sequence_of_instances_fp, quality_value):
        if type(list_of_selectors) is not list:
            raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
        if not isinstance(sequence_of_instances_tp, Index):
            raise TypeError("The parameter 'sequence_of_instances_tp' must be of type 'Index' or a subclass of 'Index'.")
        if not isinstance(sequence_of_instances_fp, Index):
            raise TypeError("The parameter 'sequence_of_instances_fp' must be of type 'Index' or a subclass of 'Index'.")
        if (type(quality_value) is not int) and (type(quality_value) is not float):
            raise TypeError("The type of the parameter 'quality_value' must be 'int' or 'float'.")
        self._list_of_selectors = list_of_selectors
        self._sequence_of_instances_tp = sequence_of_instances_tp
        self._sequence_of_instances_fp = sequence_of_instances_fp 
        self._quality_value = quality_value
    
    def _get_list_of_selectors(self):
        return self._list_of_selectors
    
    def _get_sequence_of_instances_tp(self):
        return self._sequence_of_instances_tp
    
    def _get_sequence_of_instances_fp(self):
        return self._sequence_of_instances_fp
    
    def _get_tp(self):
        return len(self._sequence_of_instances_tp)
    
    def _get_fp(self):
        return len(self._sequence_of_instances_fp)
    
    def _get_n(self):
        return len(self._sequence_of_instances_tp) + len(self._sequence_of_instances_fp) 
    
    def _get_quality_value(self):
        return self._quality_value
    
    def _set_quality_value(self, quality_value):
        self._quality_value = quality_value
    
    list_of_selectors = property(_get_list_of_selectors, None, None, "The list of selectors represented by the vertical list.")
    sequence_of_instances_tp = property(_get_sequence_of_instances_tp, None, None, "The sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors') and also by the target.")
    sequence_of_instances_fp = property(_get_sequence_of_instances_fp, None, None, "The sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target.")
    tp = property(_get_tp, None, None, "The number of dataset instances which are covered by the selectors ('list_of_selectors') and also by the target.")
    fp = property(_get_fp, None, None, "The number of dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target.")
    n = property(_get_n, None, None, "The number of dataset instances which are covered by the selectors ('list_of_selectors') no matter the target.") 
    quality_value = property(_get_quality_value, _set_quality_value, None, "The vertical list quality value.")
    
    def compute_quality_value(self, quality_measure, dict_of_parameters):
        """Method to compute the vertical list quality value using the dictionary of parameters passed by parameter. This method uses the parameters 'tp' and 'fp' of the vertical list, not of the dictionary of parameters passed by parameter. IMPORTANT: this method does not modify the vertical list.
        
        :type quality_measure: QualityMeasure
        :param quality_measure: the quality measure which is used.
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute the vertical list quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the vertical list, not of the dictionary of parameters passed by parameter.
        :rtype: float
        :return: the computed value for the vertical list quality value.
        """
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be a subclass of QualityMeasure.")
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        new_dict_of_parameters = dict_of_parameters.copy()
        new_dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp] = self._get_tp() 
        new_dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp] = self._get_fp()
        return quality_measure.compute(new_dict_of_parameters)
    
    def union(self, other_vertical_list, quality_measure, dict_of_parameters):
        """Method to create a new vertical list as a result of the union of two vertical lists. The union of two vertical lists implies the following: (1) the last selector of the list of selectors of the second vertical list is added to the end of the list of selectors of the first vertical list, and (2) the new sequences of IDs (both) are the intersection of the corresponding original ones.
        
        :type other_vertical_list: VerticalList
        :param other_vertical_list: the vertical list with which to make the union.
        :type quality_measure: QualityMeasure
        :param quality_measure: the quality measure which is used to compute the quality value of the created vertical list.
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute the vertical list quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the vertical list, not of the dictionary of parameters passed by parameter.
        :rtype: VerticalList
        :return: a new vertical list as a result of the union of this vertical list (self) and 'other_vertical_list'.
        """
        if type(other_vertical_list) is not VerticalList:
            raise TypeError("The type of the parameter 'other_vertical_list' must be 'VerticalList'.")
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be a subclass of QualityMeasure.")
        # Add the last element of 'other_vertical_list'.
        new_list_of_selectors = self._list_of_selectors.copy()
        new_list_of_selectors.append(other_vertical_list._list_of_selectors[-1])
        # Make the intersections.
        new_sequence_of_instances_tp = self._sequence_of_instances_tp.intersection(other_vertical_list._sequence_of_instances_tp, sort=False)
        new_sequence_of_instances_fp = self._sequence_of_instances_fp.intersection(other_vertical_list._sequence_of_instances_fp, sort=False)
        new_tp = len(new_sequence_of_instances_tp)
        new_fp = len(new_sequence_of_instances_fp)
        # Finally, obtain the quality value.
        new_dict_of_parameters = dict_of_parameters.copy()
        new_dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp] = new_tp 
        new_dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp] = new_fp
        new_quality_value = quality_measure.compute(new_dict_of_parameters)
        # Return the new vertical list.
        return VerticalList(new_list_of_selectors, new_sequence_of_instances_tp, new_sequence_of_instances_fp, new_quality_value)
