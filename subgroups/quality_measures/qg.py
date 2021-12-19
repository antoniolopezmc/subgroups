# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Qg quality measure.
"""

from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import ParameterNotFoundError, SubgroupParameterNotFoundError

# Python annotations.
from typing import Union

class Qg(QualityMeasure):
    """This class defines the Qg quality measure.
    """
    
    _singleton = None
    __slots__ = ()
    
    def __new__(cls) -> 'Qg':
        if Qg._singleton is None:
            Qg._singleton = object().__new__(cls)
        return Qg._singleton
    
    def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the Qg quality measure (you can also call to the instance for this purpose). IMPORTANT: the generalisation parameter 'g' is needed in order to compute this quality measure. It also has to be in the dict of parameters.
        
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure. IMPORTANT: the generalisation parameter 'g' needs to be included.
        :return: the computed value for the Qg quality measure.
        """
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if (QualityMeasure.TRUE_POSITIVES not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.FALSE_POSITIVES not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'fp' is not in 'dict_of_parameters'.")
        # This quality measure also needs the generalisation parameter 'g'.
        if ("g" not in dict_of_parameters):
            raise ParameterNotFoundError("The generalisation parameter 'g' is not in 'dict_of_parameters'.")
        tp = dict_of_parameters[QualityMeasure.TRUE_POSITIVES]
        fp = dict_of_parameters[QualityMeasure.FALSE_POSITIVES]
        g = dict_of_parameters["g"]
        return tp / ( fp + g )
    
    def get_name(self) -> str:
        """Method to get the quality measure name (equal to the class name).
        """
        return "Qg"
    
    def optimistic_estimate_of(self) -> dict[str, QualityMeasure]:
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :return: a python dictionary in which the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict()
    
    def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Compute the Qg quality measure. IMPORTANT: the generalisation parameter 'g' is needed in order to compute this quality measure. It also has to be in the dict of parameters.
        
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure. IMPORTANT: the generalisation parameter 'g' needs to be included.
        :return: the computed value for the Qg quality measure.
        """
        return self.compute(dict_of_parameters)
