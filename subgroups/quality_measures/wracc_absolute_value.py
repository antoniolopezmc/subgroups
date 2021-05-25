# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains a modification of the Weighted Relative Accuracy (WRAcc) quality measure. This quality measure always returns the absolute value of the original one.
"""

from subgroups.quality_measures.wracc import WRAcc

class WRAccAbsoluteValue(WRAcc):
    """This class defines the modified Weighted Relative Accuracy (WRAcc) quality measure. In this modification, the quality measure always returns the absolute value of the original one.
    """
    
    _singleton = None
    __slots__ = ()

    def __new__(cls):
        if WRAccAbsoluteValue._singleton is None:
            WRAccAbsoluteValue._singleton = object().__new__(cls)
            return WRAccAbsoluteValue._singleton
        else:
            return WRAccAbsoluteValue._singleton
    
    def compute(self, dict_of_parameters):
        """Method to compute the WRAccAbsoluteValue quality measure (you can also call to the instance for this purpose).
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :rtype: float
        :return: the computed value for the WRAccAbsoluteValue quality measure.
        """
        return abs( super().compute(dict_of_parameters) )
    
    def get_name(self):
        """Method to get the quality measure name (equal to the class name).
        """
        return "WRAccAbsoluteValue"
    
    def optimistic_estimate_of(self):
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :rtype: dict[str, QualityMeasure]
        :return: a python dictionary where the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict()
    
    def __call__(self, dict_of_parameters):
        """Compute the WRAccAbsoluteValue quality measure.
        
        :type dict_of_parameters: dict[str, int or float]
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :rtype: float
        :return: the computed value for the WRAcc quality measure.
        """
        return self.compute(dict_of_parameters)
