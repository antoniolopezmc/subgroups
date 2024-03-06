# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains a modification of the Weighted Relative Accuracy (WRAcc) quality measure. This new quality measure called AbsoluteWRAcc always returns the absolute value of the original WRAcc quality measure.
"""

from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.quality_measures.wracc import WRAcc

# Python annotations.
from typing import Union

class AbsoluteWRAcc(WRAcc):
    """This class defines the AbsoluteWRAcc quality measure. This new quality measure always returns the absolute value of the original WRAcc quality measure.
    """
    
    _singleton = None
    __slots__ = ()
    
    def __new__(cls) -> 'AbsoluteWRAcc':
        if AbsoluteWRAcc._singleton is None:
            AbsoluteWRAcc._singleton = object().__new__(cls)
        return AbsoluteWRAcc._singleton
    
    def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the AbsoluteWRAcc quality measure (you can also call to the instance for this purpose).
        
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this quality measure.
        :return: the computed value for the AbsoluteWRAcc quality measure.
        """
        return abs( super().compute(dict_of_parameters) )
    
    def get_name(self) -> str:
        """Method to get the quality measure name (equal to the class name).
        """
        return "AbsoluteWRAcc"
    
    def optimistic_estimate_of(self) -> dict[str, QualityMeasure]:
        """Method to get a python dictionary with the quality measures of which this one is an optimistic estimate.
        
        :return: a python dictionary in which the keys are the quality measure names and the values are the instances of those quality measures.
        """
        return dict()
    
    def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Compute the AbsoluteWRAcc quality measure.
        
        :param dict_of_parameters: python dictionary which contains all the needed parameters with which to compute this quality measure.
        :return: the computed value for the AbsoluteWRAcc quality measure.
        """
        return self.compute(dict_of_parameters)
