# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <franciscojose.morac@um.es>

"""This file contains the implementation of the absolute contribution and contribution ratio credibility measures.
"""

from subgroups.credibility_measures.credibility_measure import CredibilityMeasure
from subgroups.credibility_measures.odds_ratio_stat import OddsRatioStatistic
from subgroups.credibility_measures.odds_ratio_glm import OddsRatioGLM
from subgroups.exceptions import ParameterNotFoundError
import statsmodels.api as sm
from pandas import Series
from math import inf

# Python annotations.
from typing import Union

class SelectorContribution(CredibilityMeasure):
    """This class defines the credibility measures of absolute contribution and contribution ratio.
    """

    _singleton = None
    __slots__ = ()

    def __new__(cls) -> 'SelectorContribution':
        if SelectorContribution._singleton is None:
            SelectorContribution._singleton = object().__new__(cls)
        return SelectorContribution._singleton
    
    def compute(self, dict_of_parameters: dict[str, int | float]) -> tuple[float, float]:
        """Method to compute the absolute contribution and contribution ratio credibility measures (you can also call to the instance for this purpose).

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute these credibility measures.
        :return: a tuple with the computed values for the absolute contribution and contribution ratio credibility measures.
        """

        if type(dict_of_parameters) is not dict:
            raise TypeError("The type of the parameter 'dict_of_parameters' must be 'dict'.")
        # Required parameters for the computation of the credibility measures.
        if "odds_ratios" not in dict_of_parameters and "selector_appearances" not in dict_of_parameters:
            raise ParameterNotFoundError("One of the parameters 'odds_ratios' or 'selector_appearances' must be included in 'dict_of_parameters'.")
        if "selector_appearances" in dict_of_parameters and "target_appearance" not in dict_of_parameters:
            raise ParameterNotFoundError("The parameter 'target_appearance' must be included in 'dict_of_parameters' if the odds ratios are not included.")
        if "odds_ratio_definition" not in dict_of_parameters:
            raise ParameterNotFoundError("The parameter 'odds_ratio_definition' must be included in 'dict_of_parameters'.")
        if "pattern" not in dict_of_parameters:
            raise ParameterNotFoundError("The parameter 'pattern' must be included in 'dict_of_parameters'.")
        # The odds ratio definition must be 'glm' (computed from the generalized linear model) or 'statistic' (computed from the contingency table).
        if dict_of_parameters["odds_ratio_definition"] != "glm" and dict_of_parameters["odds_ratio_definition"] != "statistic":
            raise ValueError("The parameter 'odds_ratio_definition' must be 'glm' or 'statistic'.")
        # The minimum absolute contribution threshold can be provided to reduce computation time.
        absolute_contribution_threshold = None
        if "absolute_contribution_threshold" in dict_of_parameters:
            absolute_contribution_threshold = dict_of_parameters["absolute_contribution_threshold"]
        # Minimum and maximum absolute contribution values are recorded to compute the returned absolute contribution and contribution ratio.
        minimum_absolute_contribution = inf
        maximum_absolute_contribution = -inf
        pattern = dict_of_parameters["pattern"]
        definition = dict_of_parameters["odds_ratio_definition"]
        # If the pattern is empty, we return the absolute contribution and contribution ratio as 0.
        if len(pattern) == 0:
            return 0, 0
        # If the pattern is a single selector, we return the absolute contribution and contribution ratio as 1.
        if len(pattern) == 1:
            return 1, 1
        # If we have previously computed the odds ratios, we use them to compute the credibility measures.
        if "odds_ratios" in dict_of_parameters:
            odds_ratios = dict_of_parameters["odds_ratios"]
            pattern_as_str = str(pattern)
            odds_ratio = odds_ratios[pattern_as_str]
        # If we have to compute the odds ratios using the contingency table, we initialize the credibility measure class.
        else:
            selector_appearances = dict_of_parameters["selector_appearances"]
            target_appearance = dict_of_parameters["target_appearance"]
            # Index of the instances of the dataset (used to initialized the pattern appearances).
            instances_index = selector_appearances[list(selector_appearances.keys())[0]].index
            # Initialize the odds ratio measure class depending on the definition provided.
            if definition == "glm":
                odds_ratio_measure = OddsRatioGLM()
            elif definition == "statistic":
                odds_ratio_measure = OddsRatioStatistic()
            pattern_appearance = Series(True, index = instances_index)
            # Iterate over the selectors of the pattern to compute the pattern appearance.
            for selector in pattern:
                pattern_appearance &= selector_appearances[selector]
            # Compute the odds ratio of the pattern using the definition provided.
            odds_ratio = odds_ratio_measure({"appearance": pattern_appearance, "target_appearance": target_appearance})
        # Compute the absolute contribution of each selector in the pattern.
        for selector in pattern:
            # Compute the pattern without the selector.
            pattern_without_selector = pattern.copy()
            pattern_without_selector.remove_selector(selector)
            # If odds ratios are provided, we use them to compute contribution.
            if "odds_ratios" in dict_of_parameters:
                pattern_without_selector_odds_ratio = dict_of_parameters["odds_ratios"][str(pattern_without_selector)]
            # If odds ratios are not provided, we compute the odds ratio of the pattern without the selector.
            else:
                pattern_without_selector_appearance = Series(True, index = instances_index)
                for selector in pattern_without_selector:
                    pattern_without_selector_appearance &= selector_appearances[selector]
                pattern_without_selector_odds_ratio = odds_ratio_measure({"appearance": pattern_without_selector_appearance, "target_appearance": target_appearance})
            # Compute the absolute contribution with the odds ratio of the pattern without the selector.
            contribution = odds_ratio - pattern_without_selector_odds_ratio
            # If the minimum absolute contribution threshold is provided and it is not reached, we do not need to compute the rest of the contributions,
            # we already know that the threshold is not met and we do not need to compute the contribution ratio to compute the rank of the pattern.
            if absolute_contribution_threshold is not None and contribution < absolute_contribution_threshold:
                return contribution, inf
            minimum_absolute_contribution = min(minimum_absolute_contribution, contribution)
            maximum_absolute_contribution = max(maximum_absolute_contribution, contribution)
        # The returned absolute contribution is the minimum absolute contribution.
        absolute_contribution = minimum_absolute_contribution
        # The contribution ratio is the maximum absolute contribution divided by the minimum absolute contribution.
        if minimum_absolute_contribution == 0:
            contribution_ratio = inf
        elif minimum_absolute_contribution == inf and maximum_absolute_contribution == inf:
            contribution_ratio = 1
        else:
            contribution_ratio = maximum_absolute_contribution/minimum_absolute_contribution
        return absolute_contribution, contribution_ratio
    
    def get_name(self) -> str:
        """Method to get the credibility measure name (equal to the class name).
        """
        return "SelectorContribution"
    
    def __call__(self, dict_of_parameters: dict[str, int | float]) -> tuple[float, float]:
        """Compute the absolute contribution and contribution ratio credibility measures.
        """
        return self.compute(dict_of_parameters)

        


        
        
        


