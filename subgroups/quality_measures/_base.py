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
    # true positives tp (rows covered by the condition and the target).
    SUBGROUP_PARAMETER_tp = "tp"
    # false positives fp (rows covered by the condition but not by the target).
    SUBGROUP_PARAMETER_fp = "fp"
    # True Positives TP (rows covered by the target).
    SUBGROUP_PARAMETER_TP = "TP"
    # False Positives FP (rows not covered by the target).
    SUBGROUP_PARAMETER_FP = "FP"
    
    ### IMPORTANT ###
    ## There are other elements/parameters which are also used in the Subgroup Discovery technique. We define the following equivalences:
    #
    # n = tp + fp
    # N = TP + FP
    # p = tp / (tp + fp)
    # p0 = TP / (TP + FP)
    # tn = FP - fp
    # fn = TP - tp
    #
    
    @abstractmethod
    def compute(self, dict_of_parameters):
        pass
    
    @abstractmethod
    def get_name(self):
        pass
    
    @abstractmethod
    def get_upper_bounds(self):
        pass
    
    @abstractmethod
    def __call__(self, dict_of_parameters):
        pass
