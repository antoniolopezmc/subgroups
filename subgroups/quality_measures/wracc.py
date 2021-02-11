# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Weighted Relative Accuracy (WRAcc) quality measure.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import SubgroupParameterNotFoundError
from subgroups.quality_measures.wracc_upper_bound_1 import WRAccUpperBound1

class WRAcc(QualityMeasure):
    """This class defines the Weighted Relative Accuracy (WRAcc) quality measure.
    """
    
    _singleton = None
    __slots__ = ()

    def __new__(cls):
        if WRAcc._singleton is None:
            WRAcc._singleton = super().__new__(cls)
            return WRAcc._singleton
        else:
            return WRAcc._singleton
    
    def compute(self, dict_of_parameters):
        """Method to compute the WRAcc quality measure (you can also call to the instance for this purpose).
        
        :type dict_of_parameters: dict[str, int] or dict[str, float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :rtype: float
        :return: the computed value for the WRAcc quality measure.
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
        return ( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) ) # ( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )
    
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        return "WRAcc"
    
    def get_upper_bounds(self):
        """Method to get a python dictionary with quality measures which are an Upper Bound of this one. The dictionary keys are the quality measure names and the dictionary values are the instances of those quality measures.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the upper bound names and the values are the instances of those upper bounds.
        """
        return dict({WRAccUpperBound1().get_name() : WRAccUpperBound1()})
    
    def __call__(self, dict_of_parameters):
        """Compute the WRAcc quality measure.
        
        :type dict_of_parameters: dict[str, int] or dict[str, float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with wich compute this quality measure.
        :rtype: float
        :return: the computed value for the WRAcc quality measure.
        """
        return self.compute(dict_of_parameters)
