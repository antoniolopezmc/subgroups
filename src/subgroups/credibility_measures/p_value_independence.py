# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <franciscojose.morac@um.es>

"""This file contains the implementation of the significance credibility measure computed using statistical independece hypothesis test.
"""

from subgroups.credibility_measures.credibility_measure import CredibilityMeasure
from subgroups.exceptions import ParameterNotFoundError
from math import sqrt
from scipy.stats import norm

# Python annotations.
from typing import Union

class PValueIndependence(CredibilityMeasure):
    """This class defines the significance credibility measure computed using statistical independece hypothesis test.
    """

    _singleton = None
    __slots__ = ()

    def __new__(cls) -> 'PValueIndependence':
        if PValueIndependence._singleton is None:
            PValueIndependence._singleton = object().__new__(cls)
        return PValueIndependence._singleton
    
    def compute(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the significance credibility measure using statistical independece hypothesis test (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the pvalue.
        """

        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        # Required parameters for the computation of the credibility measure.
        if "tp" not in dict_of_parameters:
            raise ParameterNotFoundError("The subgroup parameter 'tp' is not in 'dict_of_parameters'.")
        if "fp" not in dict_of_parameters:
            raise ParameterNotFoundError("The subgroup parameter 'fp' is not in 'dict_of_parameters'.")
        if "TP" not in dict_of_parameters:
            raise ParameterNotFoundError("The subgroup parameter 'TP' is not in 'dict_of_parameters'.")
        if "FP" not in dict_of_parameters:
            raise ParameterNotFoundError("The subgroup parameter 'FP' is not in 'dict_of_parameters'.")
        tp = dict_of_parameters["tp"]
        fp = dict_of_parameters["fp"]
        TP = dict_of_parameters["TP"]
        FP = dict_of_parameters["FP"]
        N = TP + FP
        # If the pattern covers all instances, we assign the maximum possible p-value so the pattern is not selected.
        if tp == TP and fp == FP:
            return 1
        # If the pattern does not cover any instance, we assign the maximum possible p-value so the pattern is not selected.
        if tp == 0 and fp == 0:
            return 1
        z_score = (tp-(tp+fp)*TP/N)/sqrt((tp+fp)*TP/N*FP/N)
        # Return the p-value estimated by the z-score (two-tailed test).
        return 2*(1-norm.cdf(abs(z_score)))

    def get_name(self) -> str:
        """Method to get the credibility measure name (equal to the class name).
        """
        return "PValueIndependence"
    
    def __call__(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the significance credibility measure using statistical independece hypothesis test (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the p value credibility measure.
        """
        return self.compute(dict_of_parameters)
