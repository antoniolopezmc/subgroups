# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of an Upper Bound of the Weighted Relative Accuracy (WRAcc) quality measure.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import SubgroupParameterNotFoundError
from subgroups.quality_measures.wracc import WRAcc

class WRAccUpperBound1(QualityMeasure):
    """This class defines an Upper Bound of the Weighted Relative Accuracy (WRAcc) quality measure.
    """
    
    _singleton = None
    __slots__ = ()

    def __new__(cls):
        if WRAccUpperBound1._singleton is None:
            WRAccUpperBound1._singleton = super().__new__(cls)
            return WRAccUpperBound1._singleton
        else:
            return WRAccUpperBound1._singleton
    
    def compute(self, dict_of_parameters):
        """Method to compute the WRAccUpperBound1 quality measure (you can also call to the instance for this purpose).
        
        :type dict_of_parameters: dict[str, int] or dict[str, float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :rtype: float
        :return: the computed value for the WRAccUpperBound1 quality measure.
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
        return ( (tp*tp)/(tp+fp) ) * ( 1 - ( TP/(TP+FP) ) ) # ( (tp*tp)/(tp+fp) ) * ( 1 - ( TP/(TP+FP) ) )
    
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        return "WRAccUpperBound1"
    
    def upper_bound_of(self):
        """Method to get a python dictionary with quality measures of which this one is Upper Bound.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict({WRAcc().get_name() : WRAcc()})
    
    def __call__(self, dict_of_parameters):
        """Compute the WRAccUpperBound1 quality measure.
        
        :type dict_of_parameters: dict[str, int] or dict[str, float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with wich compute this quality measure.
        :rtype: float
        :return: the computed value for the WRAccUpperBound1 quality measure.
        """
        return self.compute(dict_of_parameters)
