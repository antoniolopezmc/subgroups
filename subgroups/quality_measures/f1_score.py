# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the F1 Score. This quality measure is also called as F1 Measure.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import SubgroupParameterNotFoundError

# Python annotations.
from typing import Union

class F1Score(QualityMeasure):
    """This class defines the F1 Score. This quality measure is also called as F1 Measure.
    """
    
    _singleton = None
    __slots__ = ()
    
    def __new__(cls) -> 'F1Score':
        if F1Score._singleton is None:
            F1Score._singleton = object().__new__(cls)
        return F1Score._singleton
    
    def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the F1Score quality measure (you can also call to the instance for this purpose).
        
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :return: the computed value for the F1Score quality measure.
        """
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_tp not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_fp not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'fp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_TP not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'TP' is not in 'dict_of_parameters'.")
        tp = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp]
        fp = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp]
        TP = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_TP]
        return (2*tp) / (tp+fp+TP) # 2 * PPV * Sensitivity / (PPV + Sensitivity)
    
    def get_name(self) -> str:
        """Method to get the quality measure name (equal to the class name).
        """
        return "F1Score"
    
    def optimistic_estimate_of(self) -> dict[str, QualityMeasure]:
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :return: a python dictionary in which the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict()
    
    def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Compute the F1Score quality measure.
        
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :return: the computed value for the F1Score quality measure.
        """
        return self.compute(dict_of_parameters)
