# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the parent class for all the quality measures.
"""

from abc import ABC, abstractmethod

class QualityMeasure(ABC):
    """This abstract class defines the parent class for all the quality measures.
    """
    
    __slots__ = ()
    
    ## We consider the following subgroup parameters. We can compute all the quality measures using these general elements. ##
    # true positives tp (rows covered by the subgroup description and by the subgroup target).
    SUBGROUP_PARAMETER_tp = "tp"
    # false positives fp (rows covered by the subgroup description but not by the subgroup target).
    SUBGROUP_PARAMETER_fp = "fp"
    # True Positives TP (rows covered by the subgroup target).
    SUBGROUP_PARAMETER_TP = "TP"
    # False Positives FP (rows not covered by the subgroup target).
    SUBGROUP_PARAMETER_FP = "FP"
    
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
    def compute(self, dict_of_parameters):
        """Method to compute the corresponding quality measure (you can also call to the instance for this purpose).
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :rtype: float
        :return: the computed value for the corresponding quality measure.
        """
        pass
    
    @abstractmethod
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        pass
    
    @abstractmethod
    def optimistic_estimate_of(self):
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the quality measure names and the values are the instances of those quality measures.
        """
        pass
    
    @abstractmethod
    def __call__(self, dict_of_parameters):
        """Compute the corresponding quality measure.
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :rtype: float
        :return: the computed value for the corresponding quality measure.
        """
        pass
