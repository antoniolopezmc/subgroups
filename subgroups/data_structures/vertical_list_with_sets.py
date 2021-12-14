# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of a Vertical List data structure whose sequences are implemented using python sets.
"""

from collections.abc import Collection
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.core.selector import Selector
from subgroups.data_structures.vertical_list import VerticalList
from subgroups.exceptions import VerticalListSizeError

# Python annotations.
from typing import Union

class VerticalListWithSets(VerticalList):
    """This class represents a Vertical List data structure whose sequences are implemented using python sets.
    
    :param list_of_selectors: the list of selectors represented by the Vertical List.
    :param sequence_of_instances_tp: the sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors') and also by the target. The number of elements in this sequence would be the true positives tp of the equivalent subgroup with the same list of selectors and with the same target.
    :param sequence_of_instances_fp: the sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target. The number of elements in this sequence would be the false positives fp of the equivalent subgroup with the same list of selectors and with the same target.
    :param dataset_size: the total number of instances in the dataset.
    :param quality_value: the Vertical List quality value.
    """
    
    __slots__ = ()
    
    def __init__(self, list_of_selectors : list[Selector], sequence_of_instances_tp : Collection[int], sequence_of_instances_fp : Collection[int], dataset_size : int, quality_value : Union[int, float]) -> None:
        # Call to __init__ method of the parent class.
        super().__init__(list_of_selectors, sequence_of_instances_tp, sequence_of_instances_fp, dataset_size, quality_value)
        # sequence of instances tp.
        self._sequence_of_instances_tp = set(sequence_of_instances_tp)
        self._tp = len(sequence_of_instances_tp)
        # sequence of instances fp.
        self._sequence_of_instances_fp = set(sequence_of_instances_fp)
        self._fp = len(sequence_of_instances_fp)
    
    @property
    def sequence_of_instances_tp(self) -> set[int]:
        return self._sequence_of_instances_tp
    
    @property
    def sequence_of_instances_fp(self) -> set[int]:
        return self._sequence_of_instances_fp
    
    @property
    def tp(self) -> int:
        return self._tp
    
    @property
    def fp(self) -> int:
        return self._fp
    
    @property
    def n(self) -> int:
        return self._tp + self._fp
    
    def compute_quality_value(self, quality_measure : QualityMeasure, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the Vertical List quality value using the dictionary of parameters passed by parameter. This method uses the parameters 'tp' and 'fp' of the Vertical List, not of the dictionary of parameters passed by parameter. IMPORTANT: this method does not modify the Vertical List.
        
        :param quality_measure: the quality measure which is used.
        :param dict_of_parameters: python dictionary which contains all needed parameters with which to compute the Vertical List quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the Vertical List, not of the dictionary of parameters passed by parameter.
        :return: the computed value for the Vertical List quality value.
        """
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be an instance of a subclass of the 'QualityMeasure' class.")
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        new_dict_of_parameters = dict_of_parameters.copy()
        new_dict_of_parameters[QualityMeasure.TRUE_POSITIVES] = self.tp 
        new_dict_of_parameters[QualityMeasure.FALSE_POSITIVES] = self.fp
        return quality_measure.compute(new_dict_of_parameters)
    
    def join(self, other_vertical_list : 'VerticalListWithSets', quality_measure : QualityMeasure, dict_of_parameters : dict[str, Union[int, float]], return_None_if_n_is_0 : bool = False) -> Union['VerticalListWithSets', None]:
        """Method to create a new Vertical List as a result of the join of two Vertical Lists. The join of two Vertical Lists implies the following: (1) the last selector of the list of selectors of the second Vertical List is added to the end of the list of selectors of the first Vertical List, and (2) the new sequences of IDs (both) are the intersection of the corresponding original ones.
        
        :param other_vertical_list: the Vertical List with which to make the join.
        :param quality_measure: the quality measure which is used to compute the quality value of the created Vertical List.
        :param dict_of_parameters: python dictionary which contains all needed parameters with which to compute the Vertical List quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the created Vertical List, not of the dictionary of parameters passed by parameter.
        :param return_None_if_n_is_0: if the subgroup parameter n (i.e., tp + fp) of the resulting Vertical List (i.e., the join) is 0, this means that both sequence of instances are empty and, therefore, this means that the pattern represented by the Vertical List is not in any instance in the dataset. If the parameter 'return_None_if_n_is_0' is True, None will be returned instead of a Vertical List object. By default, this parameter is False.
        :return: a new Vertical List as a result of the join of this Vertical List (self) and 'other_vertical_list'.
        """
        if type(other_vertical_list) is not VerticalListWithSets:
            raise TypeError("The type of the parameter 'other_vertical_list' must be 'VerticalListWithSets'.")
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be an instance of a subclass of the 'QualityMeasure' class.")
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if type(return_None_if_n_is_0) is not bool:
            raise TypeError("The type of the parameter 'return_None_if_n_is_0' must be 'bool'.")
        if (self._dataset_size != other_vertical_list._dataset_size):
            raise VerticalListSizeError("Vertical Lists with different 'dataset_size' value cannot be joined.")
        # Initially, the result is None.
        result = None
        # First, make the intersection of both sequences.
        new_sequence_of_instances_tp = self._sequence_of_instances_tp.intersection(other_vertical_list._sequence_of_instances_tp)
        new_sequence_of_instances_fp = self._sequence_of_instances_fp.intersection(other_vertical_list._sequence_of_instances_fp)
        new_tp = len(new_sequence_of_instances_tp)
        new_fp = len(new_sequence_of_instances_fp)
        # Continue if the parameter 'return_None_if_n_is_0' is False OR n is greater than 0. In other case, return None.
        if (not return_None_if_n_is_0) or ((new_tp + new_fp) > 0):
            # Second, add the last element of 'other_vertical_list'.
            new_list_of_selectors = self._list_of_selectors.copy()
            new_list_of_selectors.append(other_vertical_list._list_of_selectors[-1])
            # Third, obtain the quality value.
            new_dict_of_parameters = dict_of_parameters.copy()
            new_dict_of_parameters[QualityMeasure.TRUE_POSITIVES] = new_tp 
            new_dict_of_parameters[QualityMeasure.FALSE_POSITIVES] = new_fp
            new_quality_value = quality_measure.compute(new_dict_of_parameters)
            # Finally, create the object.
            result = VerticalListWithSets(new_list_of_selectors, [], [], 0, new_quality_value)
            result._sequence_of_instances_tp = new_sequence_of_instances_tp
            result._sequence_of_instances_fp = new_sequence_of_instances_fp
            result._tp = new_tp
            result._fp = new_fp
            result._dataset_size = self._dataset_size
        # Return the result.
        return result
    
    def __str__(self) -> str:
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
        sequence_of_instances_tp_as_list = list(self._sequence_of_instances_tp)
        sequence_of_instances_tp_as_list.sort()
        sequence_of_instances_tp_as_str = "["
        for x in sequence_of_instances_tp_as_list:
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str + str(x) + ", "
        if (sequence_of_instances_tp_as_str[-1] == " ") and (sequence_of_instances_tp_as_str[-2] == ","):
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str[:-2]
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str + "]"
        else:
            sequence_of_instances_tp_as_str = sequence_of_instances_tp_as_str + "]"
        # Sequence of instances fp.
        sequence_of_instances_fp_as_list = list(self._sequence_of_instances_fp)
        sequence_of_instances_fp_as_list.sort()
        sequence_of_instances_fp_as_str = "["
        for x in sequence_of_instances_fp_as_list:
            sequence_of_instances_fp_as_str = sequence_of_instances_fp_as_str + str(x) + ", "
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
