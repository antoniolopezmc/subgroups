# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the Bitset data structure used in the QFinder to create the regression models.
"""

from pandas import DataFrame, Series

# Python annotations.
from typing import Union
from subgroups.core.operator import Operator
import statsmodels.api as sm
import numpy as np

from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern

class Bitset_QFinder:
    
    """
    This class represents a bitset used in the QFinder algorithm.
    """


    __slots__ = ["_df","_TP", "_FP"]



    def __init__(self):
        self._df = DataFrame()




    def generate_bitset(self, df : DataFrame, tuple_target_attribute_value: tuple, list_of_candidate_patterns: list[Pattern]) -> None:
        self._TP = len(df[df[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]])
        self._FP = len(df) - self._TP
        
        df_without_target = df.drop(columns=[tuple_target_attribute_value[0]])
        for pattern in list_of_candidate_patterns:
            entry = None
            for selector in pattern:
                if entry is None:
                    entry = df_without_target[selector.attribute_name] == selector.value
                else:
                    entry = entry & (df_without_target[selector.attribute_name] == selector.value)
            self._df[str(pattern)] = entry
        



    
    def compute_confidence_measures(self, target_column) -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:


        # We create the global model for corrected and adjusted confidence measures
        results = sm.Logit(target_column, self._df).fit()
        adjusted_odds_ratios = results.params.apply(np.exp).to_dict()
        corrected_p_values = results.pvalues.to_dict()
        # We use the Bonferroni correction for adjusted corrected p-values: each p_value is multiplied by the number of predictors
        adjusted_corrected_p_values = results.pvalues.apply(lambda x: x * len(corrected_p_values)).to_dict()
        
        odds_ratios = {}
        p_values = {}
        coverages = {}
        absolute_contributions = {}
        contribution_ratios = {}

        # We create models to calculate the odds ratios and p-values for each pattern
        for pattern in self._df.columns:
            results = sm.Logit(target_column, self._df[pattern]).fit()
            odds_ratios[pattern] = np.exp(results.params[0])
            p_values[pattern] = results.pvalues[0]
            coverages[pattern] = len(self._df[self._df[pattern]])/(self._TP + self._FP)

        # We calculate the absolute contribution and the contribution ratio for each pattern
        for pattern_as_str in self._df.columns:
            minimum_absolute_contribution = 0
            maximum_absolute_contribution = 1
            odds_ratio = odds_ratios[pattern_as_str]
            pattern = Pattern.generate_from_str(pattern_as_str)
            if len(pattern) == 1:
                minimum_absolute_contribution = 1
            else:
                for selector in pattern:
                    pattern_without_selector = pattern.copy()
                    pattern_without_selector.remove_selector(selector)
                    pattern_without_selector_odds_ratio = odds_ratios[str(pattern_without_selector)]
                    minimum_absolute_contribution = min(minimum_absolute_contribution, pattern_without_selector_odds_ratio/odds_ratio)
                    maximum_absolute_contribution = max(maximum_absolute_contribution, pattern_without_selector_odds_ratio/odds_ratio)
            absolute_contributions[pattern_as_str] = minimum_absolute_contribution
            contribution_ratios[pattern_as_str] = maximum_absolute_contribution/minimum_absolute_contribution

        return coverages, odds_ratios, p_values,absolute_contributions, contribution_ratios, adjusted_odds_ratios, corrected_p_values, adjusted_corrected_p_values
