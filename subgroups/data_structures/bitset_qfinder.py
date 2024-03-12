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
from bitarray import bitarray

from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern

class Bitset_QFinder(object):
    
    """
    This class represents a bitset used in the QFinder algorithm.
    """


    __slots__ = ["_df","_TP", "_FP"]



    def __init__(self):
        self._df = DataFrame()




    def generate_bitset(self, df : DataFrame, tuple_target_attribute_value: tuple, list_of_candidate_patterns: list[Series], selectors: Series) -> None:
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
        
        selectors_df = {}

        for s in selectors.items():
            entry = df_without_target[s[1].attribute_name] == s[1].value
            selectors_df[s[0]] = entry
        
        selectors_df = DataFrame(selectors_df)

        self._df = {}

        for pattern in list_of_candidate_patterns:
            # The indexes of each pattern are the base selectors and the values contain wheter we are using the selector or not
            # With this line, we get the list of selectors that are in the pattern
            selectors_in_pattern = pattern.index[pattern]
            pattern_key = pattern.astype(int).astype(str).str.cat() # [True, False, True] -> '101'
            # The bitset is the result of the intersection of the selectors that are in the pattern
            entry = selectors_df[selectors_in_pattern].all(axis=1)
            # We only add the pattern to the bitset if it is not empty
            if entry.any():
                self._df[pattern_key] = entry
        
        self._df = DataFrame(self._df)


    def get_non_empty_patterns(self) -> list[Series]:
        """
            Method to get the candidate patterns after removing those that do not appear in the dataset.
        """
        
        # The keys are stored as strings, so we need to convert them back to pandas Series
        return [Series(bitarray(pattern),dtype = bool) for pattern in self._df.columns]
    
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
        for pattern_key in self._df.columns:
            results = sm.GLM(target_column, self._df[pattern_key], family=sm.families.Binomial()).fit()
            odds_ratios[pattern_key] = np.exp(results.params[0])
            p_values[pattern_key] = results.pvalues[0]
            coverages[pattern_key] = len(self._df[self._df[pattern_key]])/(self._TP + self._FP)

        # We calculate the absolute contribution and the contribution ratio for each pattern
        for pattern_key in self._df.columns:
            minimum_absolute_contribution = 1
            maximum_absolute_contribution = 0
            odds_ratio = odds_ratios[pattern_key]
            pattern_as_series = Series(bitarray(pattern_key),dtype = bool)
            # pattern = Pattern.generate_from_str(pattern_as_str)
            # if len(pattern) == 1:
            if pattern_as_series.sum() == 1:
                minimum_absolute_contribution = 1
                maximum_absolute_contribution = 1
            else:
                for selector, value in pattern_as_series.items():
                    if not value:
                        continue
                    pattern_without_selector = pattern_as_series.copy()
                    pattern_without_selector[selector] = False
                    pattern_without_selector_key = pattern_without_selector.astype(int).astype(str).str.cat()
                    pattern_without_selector_odds_ratio = odds_ratios[pattern_without_selector_key]
                    minimum_absolute_contribution = min(minimum_absolute_contribution, odds_ratio/pattern_without_selector_odds_ratio)
                    maximum_absolute_contribution = max(maximum_absolute_contribution, odds_ratio/pattern_without_selector_odds_ratio)
            absolute_contributions[pattern_key] = minimum_absolute_contribution
            if minimum_absolute_contribution == 0:
                contribution_ratios[pattern_key] = np.inf
            else:
                contribution_ratios[pattern_key] = maximum_absolute_contribution/minimum_absolute_contribution
        

        # We use the Bonferroni correction for adjusted corrected p-values: each p_value is multiplied by the number of predictors
        adjusted_p_values = {pat : p_values[pat] * len(self._df.columns) for pat in p_values.keys()}

        rv = DataFrame({
            "coverage": coverages,
            "odds_ratio": odds_ratios,
            "p_value": p_values,
            "absolute_contribution": absolute_contributions,
            "contribution_ratio": contribution_ratios,
            # "adjusted_odds_ratio": adjusted_odds_ratios,
            # "corrected_p_value": corrected_p_values,
            "adjusted_p_value": adjusted_p_values
        })

        return rv