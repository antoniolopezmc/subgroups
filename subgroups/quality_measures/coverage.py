# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Coverage quality measure.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import SubgroupParameterNotFoundError

class Coverage(QualityMeasure):
    """This class defines the Coverage quality measure.
    """
    
    _singleton = None
    __slots__ = ()
    
    def __new__(cls):
        if Coverage._singleton is None:
            Coverage._singleton = object().__new__(cls)
        return Coverage._singleton
    
    def compute(self, dict_of_parameters):
        """Method to compute the Coverage quality measure (you can also call to the instance for this purpose).
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :rtype: float
        :return: the computed value for the Coverage quality measure.
        """
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_tp not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_fp not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'fp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_TP not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'TP' is not in 'dict_of_parameters'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_FP not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'FP' is not in 'dict_of_parameters'.")
        tp = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp]
        fp = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp]
        TP = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_TP]
        FP = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_FP]
        return ( tp + fp ) / ( TP + FP ) # ( tp + fp ) / ( TP + FP )
    
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        return "Coverage"
    
    def optimistic_estimate_of(self):
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict()
    
    def __call__(self, dict_of_parameters):
        """Compute the Coverage quality measure.
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :rtype: float
        :return: the computed value for the Coverage quality measure.
        """
        return self.compute(dict_of_parameters)
