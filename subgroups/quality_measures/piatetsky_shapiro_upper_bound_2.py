# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of an Upper Bound of the Piatetsky-Shapiro quality measure.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import SubgroupParameterNotFoundError
from subgroups.quality_measures.piatetsky_shapiro import PiatetskyShapiro

class PiatetskyShapiroUpperBound2(QualityMeasure): # SOURCE: https://link.springer.com/chapter/10.1007%2F978-3-540-87479-9_47
    """This class defines an Upper Bound of the Piatetsky-Shapiro quality measure.
    """
    
    _singleton = None
    __slots__ = ()

    def __new__(cls):
        if PiatetskyShapiroUpperBound2._singleton is None:
            PiatetskyShapiroUpperBound2._singleton = super().__new__(cls)
            return PiatetskyShapiroUpperBound2._singleton
        else:
            return PiatetskyShapiroUpperBound2._singleton
    
    def compute(self, dict_of_parameters):
        """Method to compute the PiatetskyShapiroUpperBound2 quality measure (you can also call to the instance for this purpose).
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :rtype: float
        :return: the computed value for the PiatetskyShapiroUpperBound2 quality measure.
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
        tp = dict_of_parameters["tp"]
        fp = dict_of_parameters["fp"]
        TP = dict_of_parameters["TP"]
        FP = dict_of_parameters["FP"]
        return (tp+fp) * (tp / (tp+fp)) * ( 1 - ( TP / (TP+FP) ) ) # (tp+fp) * (tp / (tp+fp)) * ( 1 - ( TP / (TP+FP) ) )
    
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        return "PiatetskyShapiroUpperBound2"
    
    def upper_bound_of(self):
        """Method to get a python dictionary with quality measures of which this one is Upper Bound.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict({PiatetskyShapiro().get_name() : PiatetskyShapiro()})
    
    def __call__(self, dict_of_parameters):
        """Compute the PiatetskyShapiroUpperBound2 quality measure.
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :rtype: float
        :return: the computed value for the PiatetskyShapiroUpperBound2 quality measure.
        """
        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        return self.compute(dict_of_parameters)
