# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the root class of all the implemented Vertical Lists (data structure used by the VLSD algorithm). Conceptually, a Vertical List is similar to a Subgroup. This class is an abstract class and cannot be instantiated.
"""

from abc import ABC, abstractmethod
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.core.selector import Selector
from collections.abc import Collection

# Python annotations.
from typing import Union

class VerticalList(ABC):
    """This abstract class defines the root class of all the implemented Vertical Lists (data structure used by the VLSD algorithm). Conceptually, a Vertical List is similar to a Subgroup.
    """
    
    __slots__ = ("_list_of_selectors", "_sequence_of_instances_tp", "_tp", "_sequence_of_instances_fp", "_fp", "_number_of_dataset_instances", "_quality_value")

    def __init__(self, list_of_selectors : list[Selector], sequence_of_instances_tp : Collection[int], sequence_of_instances_fp : Collection[int], number_of_dataset_instances : int, quality_value : Union[int, float]) -> None:
        if type(list_of_selectors) is not list:
            raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
        if not isinstance(sequence_of_instances_tp, Collection):
            raise TypeError("The parameter 'sequence_of_instances_tp' must be an instance of a subclass of the 'Collection' class.")
        if not isinstance(sequence_of_instances_fp, Collection):
            raise TypeError("The parameter 'sequence_of_instances_fp' must be an instance of a subclass of the 'Collection' class.")
        if (type(number_of_dataset_instances) is not int):
            raise TypeError("The type of the parameter 'number_of_dataset_instances' must be 'int'.")
        if (type(quality_value) is not int) and (type(quality_value) is not float):
            raise TypeError("The type of the parameter 'quality_value' must be 'int' or 'float'.")
        self._list_of_selectors = list_of_selectors
        self._number_of_dataset_instances = number_of_dataset_instances
        self._quality_value = quality_value
    
    def _get_list_of_selectors(self) -> list[Selector]:
        return self._list_of_selectors

    @property
    @abstractmethod
    def sequence_of_instances_tp(self) -> Collection[int]:
        """The sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors') and also by the target.
        """
        raise NotImplementedError("The '_get_sequence_of_instances_tp' method from the 'VerticalList' abstract class is an abstract method.")
    
    @property
    @abstractmethod
    def sequence_of_instances_fp(self) -> Collection[int]:
        """The sequence of IDs of the dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target.
        """
        raise NotImplementedError("The '_get_sequence_of_instances_fp' method from the 'VerticalList' abstract class is an abstract method.")
    
    @property
    @abstractmethod
    def tp(self) -> int:
        """The number of dataset instances which are covered by the selectors ('list_of_selectors') and also by the target.
        """
        raise NotImplementedError("The '_get_tp' method from the 'VerticalList' abstract class is an abstract method.")
    
    @property
    @abstractmethod
    def fp(self) -> int:
        """The number of dataset instances which are covered by the selectors ('list_of_selectors'), but not by the target.
        """
        raise NotImplementedError("The '_get_fp' method from the 'VerticalList' abstract class is an abstract method.")
    
    @property
    @abstractmethod
    def n(self) -> int:
        """The number of dataset instances which are covered by the selectors ('list_of_selectors'), no matter the target.
        """
        raise NotImplementedError("The '_get_n' method from the 'VerticalList' abstract class is an abstract method.")

    def _get_number_of_dataset_instances(self) -> int:
        return self._number_of_dataset_instances

    def _get_quality_value(self) -> Union[int, float]:
        return self._quality_value
    
    def _set_quality_value(self, quality_value : Union[int, float]) -> None:
        self._quality_value = quality_value

    list_of_selectors = property(_get_list_of_selectors, None, None, "The list of selectors represented by the Vertical List.")
    number_of_dataset_instances = property(_get_number_of_dataset_instances, None, None, "Number of instances of the dataset from which this Vertical List has been generated.")
    quality_value = property(_get_quality_value, _set_quality_value, None, "The Vertical List quality value.")

    @abstractmethod
    def compute_quality_value(self, quality_measure : QualityMeasure, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the Vertical List quality value using the dictionary of parameters passed by parameter. This method uses the parameters 'tp' and 'fp' of the Vertical List, not of the dictionary of parameters passed by parameter. IMPORTANT: this method does not modify the Vertical List.
        
        :param quality_measure: the quality measure which is used.
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute the Vertical List quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the Vertical List, not of the dictionary of parameters passed by parameter.
        :return: the computed value for the Vertical List quality value.
        """
        raise NotImplementedError("The 'compute_quality_value' method from the 'VerticalList' abstract class is an abstract method.")

    @abstractmethod
    def join(self, other_vertical_list : 'VerticalList', quality_measure : QualityMeasure, dict_of_parameters : dict[str, Union[int, float]], return_None_if_n_is_0 : bool = False) -> Union['VerticalList', None]:
        """Method to create a new Vertical List as a result of the join of two Vertical Lists. The join of two Vertical Lists implies the following: (1) the last selector of the list of selectors of the second Vertical List is added to the end of the list of selectors of the first Vertical List, and (2) the new sequences of IDs (both) are the intersection of the corresponding original ones.
        
        :param other_vertical_list: the Vertical List with which to make the join.
        :param quality_measure: the quality measure which is used to compute the quality value of the created Vertical List.
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute the Vertical List quality value. IMPORTANT: this method uses the 'tp' and 'fp' parameters of the created Vertical List, not of the dictionary of parameters passed by parameter.
        :param return_None_if_n_is_0: if the subgroup parameter n (i.e., tp + fp) of the resulting Vertical List (i.e., the join) is 0, this means that both sequence of instances are empty and, therefore, this means that the pattern represented by the Vertical List is not in any instance in the dataset. If the parameter 'return_None_if_n_is_0' is True, None will be returned instead of a Vertical List object. By default, this parameter is False.
        :return: a new Vertical List as a result of the join of this Vertical List (self) and 'other_vertical_list'.
        """
        raise NotImplementedError("The 'join' method from the 'VerticalList' abstract class is an abstract method.")
