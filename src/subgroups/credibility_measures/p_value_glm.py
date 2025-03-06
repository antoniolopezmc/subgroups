# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <fmora@um.es>

"""This file contains the implementation of the significance credibility measure computed using the generalized linear model.
"""

from subgroups.credibility_measures.credibility_measure import CredibilityMeasure
from subgroups.exceptions import ParameterNotFoundError
import statsmodels.api as sm

# Python annotations.
from typing import Union

class PValueGLM(CredibilityMeasure):
    """This class defines the significance credibility measure computed using the generalized linear model.
    """

    _singleton = None
    __slots__ = ()

    def __new__(cls) -> 'PValueGLM':
        if PValueGLM._singleton is None:
            PValueGLM._singleton = object().__new__(cls)
        return PValueGLM._singleton
    
    def compute(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the significance credibility measure using the generalized linear model (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the pvalue.
        """

        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        # Required parameters for the computation of the credibility measure. We need the generalized linear model or both the appearance and target_appearance parameters.
        if "glm" not in dict_of_parameters and ("appearance" not in dict_of_parameters or "target_appearance" not in dict_of_parameters):
            raise ParameterNotFoundError("The parameters 'glm' or 'appearance' and 'target_appearance' must be included in 'dict_of_parameters'.")
        # If the glm is included in the dictionary, we extract the p value from it.
        if "glm" in dict_of_parameters:
            glm = dict_of_parameters["glm"]
            return glm.pvalues.iloc[0]
        # Otherwise, we compute the generalized linear model and extract the p value from it.
        results = sm.GLM(dict_of_parameters["target_appearance"], dict_of_parameters["appearance"], family=sm.families.Binomial()).fit()
        return results.pvalues.iloc[0]

    def get_name(self) -> str:
        """Method to get the credibility measure name (equal to the class name).
        """
        return "PValueGLM"
    
    def __call__(self, dict_of_parameters: dict[str, int | float]) -> float:
        """Method to compute the significance credibility measure using the generalized linear model (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the p value credibility measure.
        """
        return self.compute(dict_of_parameters)