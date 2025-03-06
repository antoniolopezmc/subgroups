# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <fmora@um.es>

"""This file contains the implementation of odds ratio credibility measure computed using the generalized linear model.
"""

from subgroups.credibility_measures.credibility_measure import CredibilityMeasure
from subgroups.exceptions import ParameterNotFoundError
import statsmodels.api as sm
from numpy import exp

# Python annotations.
from typing import Union

class OddsRatioGLM(CredibilityMeasure):
    """This class defines the odds ratio credibility measure computed using the generalized linear model.
    """

    _singleton = None
    __slots__ = ()

    def __new__(cls) -> 'OddsRatioGLM':
        if OddsRatioGLM._singleton is None:
            OddsRatioGLM._singleton = object().__new__(cls)
        return OddsRatioGLM._singleton
    
    def compute(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the odds ratio credibility measure using the generalized linear model (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the odds ratio credibility measure.
        """

        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        # Required parameters for the computation of the credibility measure.
        if "glm" not in dict_of_parameters and ("appearance" not in dict_of_parameters or "target_appearance" not in dict_of_parameters):
            raise ParameterNotFoundError("The parameters 'glm' or both 'appearance' and 'target_appearance' must be included in 'dict_of_parameters'.")
        # Generalized linear model provided. We return the odds ratio as the exponential of the coefficient.
        if "glm" in dict_of_parameters:
            glm = dict_of_parameters["glm"]
            return exp(glm.params.iloc[0])
        # We fit the generalized linear model and return the odds ratio as the exponential of the coefficient.
        results = sm.GLM(dict_of_parameters["target_appearance"], dict_of_parameters["appearance"], family=sm.families.Binomial()).fit()
        return exp(results.params.iloc[0])

    def get_name(self) -> str:
        """Method to get the credibility measure name (equal to the class name).
        """
        return "OddsRatioGLM"
    
    def __call__(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the odds ratio credibility measure using the generalized linear model (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the odds ratio credibility measure.
        """
        return self.compute(dict_of_parameters)