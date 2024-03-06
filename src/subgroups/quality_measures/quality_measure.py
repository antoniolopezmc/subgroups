# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the root class of all the implemented quality measures. This class is an abstract class and cannot be instantiated.
"""

from abc import ABC, abstractmethod

# Python annotations.
from typing import Union, ClassVar

class QualityMeasure(ABC):
    """This abstract class defines the root class of all the implemented quality measures.
    """
    
    __slots__ = ()
    
    ## We consider the following subgroup parameters. We can compute all the quality measures using these general elements. ##
    # true positives tp (rows covered by the subgroup description and by the subgroup target).
    TRUE_POSITIVES : ClassVar[str] = "tp"
    # false positives fp (rows covered by the subgroup description but not by the subgroup target).
    FALSE_POSITIVES : ClassVar[str] = "fp"
    # true population TP (rows covered by the subgroup target).
    TRUE_POPULATION : ClassVar[str] = "TP"
    # false population FP (rows not covered by the subgroup target).
    FALSE_POPULATION : ClassVar[str] = "FP"
    
    ### IMPORTANT ###
    ## There are other elements/parameters which are also used in the Subgroup Discovery literature. We define the following equivalences:
    #
    # n = tp + fp
    # N = TP + FP
    # p = tp / (tp + fp)
    # p0 = TP / (TP + FP)
    # tn = FP - fp
    # fn = TP - tp
    #
    ## At the same time, we can also define the following equivalences:
    #
    # tp = p * n
    # TP = p0 * N
    #  
    
    @abstractmethod
    def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the corresponding quality measure (you can also call to the instance for this purpose).
        
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :return: the computed value for the corresponding quality measure.
        """
        raise NotImplementedError("The 'compute' method from the 'QualityMeasure' abstract class is an abstract method.")
    
    @abstractmethod
    def get_name(self) -> str:
        """Method to get the quality measure name (equal to the class name).
        """
        raise NotImplementedError("The 'get_name' method from the 'QualityMeasure' abstract class is an abstract method.")
    
    @abstractmethod
    def optimistic_estimate_of(self) -> dict[str, 'QualityMeasure']:
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :return: a python dictionary in which the keys are the quality measure names and the values are the instances of those quality measures.
        """
        raise NotImplementedError("The 'optimistic_estimate_of' method from the 'QualityMeasure' abstract class is an abstract method.")
    
    @abstractmethod
    def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Compute the corresponding quality measure.
        
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :return: the computed value for the corresponding quality measure.
        """
        raise NotImplementedError("The '__call__' method from the 'QualityMeasure' abstract class is an abstract method.")
