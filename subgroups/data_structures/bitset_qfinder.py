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
        """
        This method generates a bitset from a dataset and a list of candidate patterns.
        Each column of the bitset represents a candidate pattern and each row represents an instance of the dataset.
        The value of each cell is True if the corresponding pattern appears in the corresponding instance and False otherwise.

        :param df: dataset from which the bitset is generated.
        :param tuple_target_attribute_value: tuple which contains the name of the target attribute and its value.
        :param list_of_candidate_patterns: list of candidate patterns.

        
        """
        self._TP = len(df[df[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]])
        self._FP = len(df) - self._TP
        
        df_without_target = df.drop(columns=[tuple_target_attribute_value[0]])
        
        pattern_matches = {}
        for pattern in list_of_candidate_patterns:
            entry = None
            for selector in pattern:
                if entry is None:
                    entry = df_without_target[selector.attribute_name] == selector.value
                else:
                    entry = entry & (df_without_target[selector.attribute_name] == selector.value)
            # If the pattern is empty (it does not appear in the dataset), we do not add it to the bitset.
            if entry.sum() != 0:
                pattern_matches[str(pattern)] = entry
            # else:
            #     print( entry.to_list())
        self._df = DataFrame(pattern_matches)


    def get_non_empty_patterns(self) -> list[Pattern]:
        """
            Method to get the candidate patterns after removing those that do not appear in the dataset.
        """
        return [Pattern.generate_from_str(pattern_as_str) for pattern_as_str in self._df.columns]

    
    def compute_credibility_measures(self, target_column) -> tuple[dict, dict, dict, dict, dict, dict]:

        """
            Method to compute the credibility measures for each candidate pattern.
            
            :param target_column: target column of the dataset.
            :return: a tuple with dictionaries with the credibility values for each candidate pattern.

        """

        # WARNING: Corrected measures for confounders are not implemented yet
        # We create the global model for corrected and adjusted credibility measures
        # results = sm.Logit(target_column, self._df).fit(method='nm')
        # adjusted_odds_ratios = results.params.apply(np.exp).to_dict()
        # corrected_p_values = results.pvalues.to_dict()
        
        odds_ratios = {}
        p_values = {}
        coverages = {}
        absolute_contributions = {}
        contribution_ratios = {}

        # We create models to calculate the odds ratios and p-values for each pattern
        for pattern in self._df.columns:
            # results = sm.Logit(target_column, self._df[pattern]).fit()
            results = sm.GLM(target_column, self._df[pattern], family=sm.families.Binomial()).fit()
            odds_ratios[pattern] = np.exp(results.params[0])
            p_values[pattern] = results.pvalues[0]
            coverages[pattern] = len(self._df[self._df[pattern]])/(self._TP + self._FP)

        # We calculate the absolute contribution and the contribution ratio for each pattern
        for pattern_as_str in self._df.columns:
            minimum_absolute_contribution = 1
            maximum_absolute_contribution = 0
            odds_ratio = odds_ratios[pattern_as_str]
            pattern = Pattern.generate_from_str(pattern_as_str)
            if len(pattern) == 1:
                minimum_absolute_contribution = 1
                maximum_absolute_contribution = 1
            else:
                for selector in pattern:
                    pattern_without_selector = pattern.copy()
                    pattern_without_selector.remove_selector(selector)
                    pattern_without_selector_odds_ratio = odds_ratios[str(pattern_without_selector)]
                    minimum_absolute_contribution = min(minimum_absolute_contribution, odds_ratio/pattern_without_selector_odds_ratio)
                    maximum_absolute_contribution = max(maximum_absolute_contribution, odds_ratio/pattern_without_selector_odds_ratio)
            absolute_contributions[pattern_as_str] = minimum_absolute_contribution
            if minimum_absolute_contribution == 0:
                contribution_ratios[pattern_as_str] = np.inf
            else:
                contribution_ratios[pattern_as_str] = maximum_absolute_contribution/minimum_absolute_contribution
        

        # We use the Bonferroni correction for adjusted corrected p-values: each p_value is multiplied by the number of predictors
        adjusted_p_values = {pat : p_values[pat] * len(self._df.columns) for pat in p_values.keys()}

        return coverages, odds_ratios, p_values, absolute_contributions, contribution_ratios, adjusted_p_values
