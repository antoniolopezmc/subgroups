# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Vertical List data structure used in the VLSD algorithm.
"""

from collections.abc import Iterable
from bitarray import bitarray
from subgroups.quality_measures._base import QualityMeasure

class VerticalList(object):
    """This class represents a Vertical List.
    
    :type list_of_selectors: list[Selector]
    :param list_of_selectors: the list of selectors represented by the vertical list.
    :type sequence_of_instances_tp: collections.abc.Iterator
    :param sequence_of_instances_tp: the sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors') and also by the target. The number of elements in this sequence would be the true positives tp of the equivalent subgroup with the same list of selectors and with the same target.
    :type sequence_of_instances_fp: collections.abc.Iterator
    :param sequence_of_instances_fp: the sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target. The number of elements in this sequence would be the false positives fp of the equivalent subgroup with the same list of selectors and with the same target.
    :type dataset_size: int
    :param dataset_size: the total number of instances in the dataset.
    :type quality_value: int or float.
    :param quality_value: the vertical list quality value.
    """
    
    __slots__ = "_list_of_selectors", "_sequence_of_instances_tp", "_tp", "_sequence_of_instances_fp", "_fp", "_quality_value"
    
    def __init__(self, list_of_selectors, sequence_of_instances_tp, sequence_of_instances_fp, dataset_size, quality_value):
        if type(list_of_selectors) is not list:
            raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
        if not isinstance(sequence_of_instances_tp, Iterable):
            raise TypeError("The parameter 'sequence_of_instances_tp' must be iterable.")
        if not isinstance(sequence_of_instances_fp, Iterable):
            raise TypeError("The parameter 'sequence_of_instances_fp' must be iterable.")
        if (type(dataset_size) is not int):
            raise TypeError("The type of the parameter 'dataset_size' must be 'int'.")
        if (type(quality_value) is not int) and (type(quality_value) is not float):
            raise TypeError("The type of the parameter 'quality_value' must be 'int' or 'float'.")
        self._list_of_selectors = list_of_selectors
        self._quality_value = quality_value
        # sequence of instances tp.
        self._sequence_of_instances_tp = bitarray(dataset_size, endian = "big")
        self._sequence_of_instances_tp.setall(0)
        for elem in sequence_of_instances_tp:
            self._sequence_of_instances_tp[elem] = 1
        self._tp = len(sequence_of_instances_tp)
        # sequence of instances fp.
        self._sequence_of_instances_fp = bitarray(dataset_size, endian = "big")
        self._sequence_of_instances_fp.setall(0)
        for elem in sequence_of_instances_fp:
            self._sequence_of_instances_fp[elem] = 1
        self._fp = len(sequence_of_instances_fp)
    
    def _get_list_of_selectors(self):
        return self._list_of_selectors
    
    def _get_sequence_of_instances_tp(self):
        return self._sequence_of_instances_tp
    
    def _get_sequence_of_instances_fp(self):
        return self._sequence_of_instances_fp
    
    def _get_tp(self):
        return self._tp
    
    def _get_fp(self):
        return self._fp
    
    def _get_n(self):
        return self._tp + self._fp
    
    def _get_quality_value(self):
        return self._quality_value
    
    def _set_quality_value(self, quality_value):
        self._quality_value = quality_value
    
    list_of_selectors = property(_get_list_of_selectors, None, None, "The list of selectors represented by the vertical list.")
    sequence_of_instances_tp = property(_get_sequence_of_instances_tp, None, None, "The sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors') and also by the target. IMPORTANT: the sequence is returned as a bitarray.")
    sequence_of_instances_fp = property(_get_sequence_of_instances_fp, None, None, "The sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target. IMPORTANT: the sequence is returned as a bitarray.")
    tp = property(_get_tp, None, None, "The number of dataset instances which are covered by the selectors ('list_of_selectors') and also by the target.")
    fp = property(_get_fp, None, None, "The number of dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target.")
    n = property(_get_n, None, None, "The number of dataset instances which are covered by the selectors ('list_of_selectors'), no matter the target.") 
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
    
    def union(self, other_vertical_list, quality_measure, dict_of_parameters, return_None_if_n_is_0 = False):
        """Method to create a new vertical list as a result of the union of two vertical lists. The union of two vertical lists implies the following: (1) the last selector of the list of selectors of the second vertical list is added to the end of the list of selectors of the first vertical list, and (2) the new sequences of IDs (both) are the intersection of the corresponding original ones.
        
        :type other_vertical_list: VerticalList
        :param other_vertical_list: the vertical list with which to make the union.
        :type quality_measure: QualityMeasure
        :param quality_measure: the quality measure which is used to compute the quality value of the created vertical list.
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute the vertical list quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the vertical list, not of the dictionary of parameters passed by parameter.
        :type return_None_if_n_is_0: bool
        :param return_None_if_n_is_0: if the subgroup parameter n (i.e., tp + fp) of the resulting vertical list (i.e., the union) is 0, this means that both sequence of instances are empty and, therefore, this means that the pattern represented by the vertical list is not in any instance in the dataset. If this parameter is True, None will be returned instead of a vertical list object. By default, this parameter is False.
        :rtype: VerticalList
        :return: a new vertical list as a result of the union of this vertical list (self) and 'other_vertical_list'.
        """
        if type(other_vertical_list) is not VerticalList:
            raise TypeError("The type of the parameter 'other_vertical_list' must be 'VerticalList'.")
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be a subclass of QualityMeasure.")
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if type(return_None_if_n_is_0) is not bool:
            raise TypeError("The type of the parameter 'return_None_if_n_is_0' must be 'bool'.")
        # Initially, the result is None.
        result = None
        # First, make the intersection of both sequences (using the AND operator, because both sequences are bitarrays).
        new_sequence_of_instances_tp = self._sequence_of_instances_tp & other_vertical_list._sequence_of_instances_tp
        new_sequence_of_instances_fp = self._sequence_of_instances_fp & other_vertical_list._sequence_of_instances_fp
        new_tp = new_sequence_of_instances_tp.count(1)
        new_fp = new_sequence_of_instances_fp.count(1)
        # Continue if the parameter 'return_None_if_n_is_0' is False OR n is greater than 0. In other case, return None.
        if (not return_None_if_n_is_0) or ((new_tp + new_fp) > 0):
            # Second, add the last element of 'other_vertical_list'.
            new_list_of_selectors = self._list_of_selectors.copy()
            new_list_of_selectors.append(other_vertical_list._list_of_selectors[-1])
            # Third, obtain the quality value.
            new_dict_of_parameters = dict_of_parameters.copy()
            new_dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp] = new_tp 
            new_dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp] = new_fp
            new_quality_value = quality_measure.compute(new_dict_of_parameters)
            # Finally, create the object.
            result = VerticalList(new_list_of_selectors, [], [], 0, new_quality_value)
            result._sequence_of_instances_tp = new_sequence_of_instances_tp
            result._sequence_of_instances_fp = new_sequence_of_instances_fp
            result._tp = new_tp
            result._fp = new_fp
        # Return the result.
        return result
    
    def __str__(self):
        # List of selectors.
        list_of_selectors_as_str = "["
        for e in self._list_of_selectors:
            list_of_selectors_as_str = list_of_selectors_as_str + str(e) + ", "
        if len(self._list_of_selectors) == 0:
            list_of_selectors_as_str = list_of_selectors_as_str + "]"
        else:
            list_of_selectors_as_str = list_of_selectors_as_str[:-2]
            list_of_selectors_as_str = list_of_selectors_as_str + "]"
        # Sequence of instances tp.
        sequence_of_instances_tp_as_str = "["
        index = 0
        for bit in self._sequence_of_instances_tp:
            if bit:
                sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str + str(index) + ", "
            index = index + 1
        if (sequence_of_instances_tp_as_str[-1] == " ") and (sequence_of_instances_tp_as_str[-2] == ","):
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str[:-2]
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str + "]"
        else:
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str + "]"
        # Sequence of instances fp.
        sequence_of_instances_fp_as_str = "["
        index = 0
        for bit in self._sequence_of_instances_fp:
            if bit:
                sequence_of_instances_fp_as_str = sequence_of_instances_fp_as_str + str(index) + ", "
            index = index + 1
        if (sequence_of_instances_fp_as_str[-1] == " ") and (sequence_of_instances_fp_as_str[-2] == ","):
            sequence_of_instances_fp_as_str = sequence_of_instances_fp_as_str[:-2]
            sequence_of_instances_fp_as_str = sequence_of_instances_fp_as_str + "]"
        else:
            sequence_of_instances_fp_as_str = sequence_of_instances_fp_as_str + "]"
        # Return.
        return "List of selectors: " + list_of_selectors_as_str + \
            ", Sequence of instances (tp): " + sequence_of_instances_tp_as_str + \
            ", Sequence of instances (fp): " + sequence_of_instances_fp_as_str + \
            ", Quality value: " + str(self._quality_value)
