# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Qg quality measure.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import ParameterNotFoundError, SubgroupParameterNotFoundError

class Qg(QualityMeasure):
    """This class defines the Qg quality measure.
    """
    
    _singleton = None
    __slots__ = ()
    
    def __new__(cls):
        if Qg._singleton is None:
            Qg._singleton = super().__new__(cls)
        return Qg._singleton
    
    def compute(self, dict_of_parameters):
        """Method to compute the Qg quality measure (you can also call to the instance for this purpose). IMPORTANT: the generalisation parameter 'g' is needed in order to compute this quality measure. It also has to be in the dict of parameters.
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure. IMPORTANT: the generalisation parameter 'g' needs to be included.
        :rtype: float
        :return: the computed value for the Qg quality measure.
        """
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_tp not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
        if (QualityMeasure.SUBGROUP_PARAMETER_fp not in dict_of_parameters):
            raise SubgroupParameterNotFoundError("The subgroup parameter 'fp' is not in 'dict_of_parameters'.")
        # This quality measure also needs the generalisation parameter 'g'.
        if ("g" not in dict_of_parameters):
            raise ParameterNotFoundError("The generalisation parameter 'g' is not in 'dict_of_parameters'.")
        tp = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp]
        fp = dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp]
        g = dict_of_parameters["g"]
        return tp / ( fp + g ) # tp / ( fp + g )
    
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        return "Qg"
    
    def optimistic_estimate_of(self):
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict()
    
    def __call__(self, dict_of_parameters):
        """Compute the Qg quality measure. IMPORTANT: the generalisation parameter 'g' is needed in order to compute this quality measure. It also has to be in the dict of parameters.
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure. IMPORTANT: the generalisation parameter 'g' needs to be included.
        :rtype: float
        :return: the computed value for the Qg quality measure.
        """
        return self.compute(dict_of_parameters)
