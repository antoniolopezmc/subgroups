# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <fmora@um.es>

"""This file contains the implementation of odds ratio credibility measure computed using the contingency table.
"""

from subgroups.credibility_measures.credibility_measure import CredibilityMeasure
from subgroups.exceptions import ParameterNotFoundError
from math import inf

# Python annotations.
from typing import Union

class OddsRatioStatistic(CredibilityMeasure):
    """This class defines the odds ratio credibility measure computed using the contingency table.
    """

    _singleton = None
    __slots__ = ()

    def __new__(cls) -> 'OddsRatioStatistic':
        if OddsRatioStatistic._singleton is None:
            OddsRatioStatistic._singleton = object().__new__(cls)
        return OddsRatioStatistic._singleton
    
    def compute(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the odds ratio credibility measure using the contingency table (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the odds ratio credibility measure.
        """

        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        # Required parameters for the computation of the credibility measure. We need either 'tp', 'fp', 'TP' and 'FP' or 'appearance' and 'target_appearance'.
        if ("tp" not in dict_of_parameters or "fp" not in dict_of_parameters or "TP" not in dict_of_parameters or "FP" not in dict_of_parameters) and ("appearance" not in dict_of_parameters or "target_appearance" not in dict_of_parameters):
            raise ParameterNotFoundError("All the parameters 'tp', 'fp', 'TP' and 'FP' or 'appearance' and 'target_appearance' must be included in 'dict_of_parameters'.")
        # If the base statistics are provided, we use them to compute the odds ratio.
        if "tp" in dict_of_parameters:
            tp = dict_of_parameters["tp"]
            fp = dict_of_parameters["fp"]
            TP = dict_of_parameters["TP"]
            FP = dict_of_parameters["FP"]
        # If the appearance and target appearance vectors are provided, we compute the base statistics from them.
        else:
            appearance = dict_of_parameters["appearance"]
            target_appearance = dict_of_parameters["target_appearance"]
            tp = (appearance & target_appearance).sum()
            fp = (appearance & ~target_appearance).sum()
            TP = target_appearance.sum()
            FP = (~target_appearance).sum()
        # If the pattern covers all instances, we assign the minimum possible odds ratio so the pattern is not selected.
        if tp == TP and fp == FP:
            return 0
        # If the pattern covers all positive instances, we assign the maximum possible odds ratio.
        if tp == TP:
            return inf
        # If the pattern covers all negative instances but not all instances, we assign the minimum possible odds ratio so the pattern is not selected.
        if fp == FP:
            return 0
        # If the pattern does not cover any instance, we assign the minimum possible odds ratio so the pattern is not selected.
        if tp == 0 and fp == 0:
            return 0
        # If the pattern only covers positive instances, we assign the maximum possible odds ratio.
        if fp == 0:
            return inf
        return (tp/fp)/((TP-tp)/(FP-fp))
    
    def get_name(self) -> str:
        """Method to get the credibility measure name (equal to the class name).
        """
        return "OddsRatioStatistic"
    
    def __call__(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Compute the odds ratio credibility measure using the contingency table.
        """
        return self.compute(dict_of_parameters)