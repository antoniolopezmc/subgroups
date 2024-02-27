# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the SequentialQFinder algorithm.
"""

import itertools
from typing import Union
from pandas import DataFrame, Series
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from bitarray import bitarray
from subgroups.data_structures.bitset_qfinder import Bitset_QFinder
import operator
import statsmodels.api as sm
import numpy as np

class SQFinder(Algorithm):
    """
    This class represents the SQFinder algorithm.

    :param cats: the number of maximum values for each column. If there is more values, we take the most frequent ones. If this value is -1, we take all the values.
    :param max_complexity: the maximum complexity (length) of the patterns.
    :param coverage_thld: the minimum coverage threshold.
    :param or_thld: the minimum odds ratio and adjusted odds ratio threshold.
    :param p_val_thld: the maximum p-value threshold. This threshold is used for p-values corrected for confounders and adjusted p-values.
    :param abs_contribution_thld: the minimum absolute contribution threshold.
    :param contribution_thld: the minimum contribution ratio threshold.
    :param write_results_in_file: if True, the results will be written in a file.
    :param file_path: the path of the file where the results will be written.
    :param write_stats_in_file: if True, the statistics will be written in a HTML file.
    :param stats_path: the path of the file where the statistics will be written.
    :param delta: minimum delta to consider that a subgroup has a higher effect size.
    :param num_subgroups: the number of top subgroups to return.
    """

    __slots__ = ('_num_subgroups','_cats', '_max_complexity', '_thresholds','_credibility_values' , '_file', '_file_path','_visited_subgroups' , '_df','_delta', '_top_subgroups','_top_subgroups_credibilities', '_candidate_patterns')

    # A credibility criterion is a credibility measure and a threshold. Here we set if the credibility measure value
    # should be greater or equal than the threshold or less or equal than the threshold.
    _credibility_criterions = {
        "coverage" :  operator.ge,
        "odds_ratio" : operator.ge,
        "p_value" : operator.le,
        "absolute_contribution" : operator.ge,
        "contribution_ratio" : operator.le,
        # "adjusted_odds_ratio" : operator.ge,
        # "corrected_p_value" : operator.le,
        # "adjusted_p_value" : operator.le
    }

    def __init__(self, num_subgroups :int, cats : int = -1, max_complexity: int = -1, coverage_thld: float = 0.1, or_thld: float = 1.2, p_val_thld: float = 0.05, abs_contribution_thld: float = 0.2, contribution_thld: float = 5, delta :float = 0.2, write_results_in_file: bool = False, file_path: Union[str,None] = None) -> None:
        if type(num_subgroups) is not int:
            raise TypeError("The type of the parameter 'num_subgroups' must be 'int'.")
        if type(cats) is not int:
            raise TypeError("The type of the parameter 'cats' must be 'int'.")
        if type(max_complexity) is not int:
            raise TypeError("The type of the parameter 'max_complexity' must be 'int'.")
        if type(coverage_thld) is not float and type(coverage_thld) is not int:
            raise TypeError("The type of the parameter 'coverage_thld' must be 'float'.")
        if type(or_thld) is not float and type(or_thld) is not int:
            raise TypeError("The type of the parameter 'or_thld' must be 'float'.")
        if type(p_val_thld) is not float and type(p_val_thld) is not int:
            raise TypeError("The type of the parameter 'p_val_thld' must be 'float'.")
        if type(abs_contribution_thld) is not float and type(abs_contribution_thld) is not int:
            raise TypeError("The type of the parameter 'abs_contribution_thld' must be 'float'.")
        if type(contribution_thld) is not float and type(contribution_thld) is not int:
            raise TypeError("The type of the parameter 'contribution_thld' must be 'float'.")
        if type(delta) is not float and type(delta) is not int:
            raise TypeError("The type of the parameter 'delta' must be 'float'.")
        # We check that that the parameter values are valid.
        if (cats < -1):
            raise InconsistentMethodParametersError("The parameter 'cats' must be greater than or equal to -1.")
        if (coverage_thld < 0 or coverage_thld > 1):
            raise InconsistentMethodParametersError("The parameter 'coverage_thld' must be between 0 and 1.")
        if (or_thld < 0):
            raise InconsistentMethodParametersError("The parameter 'or_thld' must be greater than or equal to 0.")
        if (p_val_thld < 0 or p_val_thld > 1):
            raise InconsistentMethodParametersError("The parameter 'p_val_thld' must be between 0 and 1.")
        if (abs_contribution_thld < 0 or abs_contribution_thld > 1):
            raise InconsistentMethodParametersError("The parameter 'abs_contribution_thld' must be between 0 and 1.")
        if (contribution_thld < 0):
            raise InconsistentMethodParametersError("The parameter 'contribution_thld' must be greater than or equal to 0.")
        # If 'write_results_in_file' is True, 'file_path' must not be None.
        if (write_results_in_file) and (file_path is None):
            raise ValueError("If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        self._num_subgroups = num_subgroups
        self._cats = cats
        self._max_complexity = max_complexity
        self._delta = delta
        if (write_results_in_file):
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None
        self._top_subgroups = []
        self._top_subgroups_credibilities = []
        self._visited_subgroups = 0
        # Thresholds for each credibility measure.
        self._thresholds = {
            "coverage" : coverage_thld,
            "odds_ratio" : or_thld,
            "p_value" : p_val_thld,
            "absolute_contribution" : abs_contribution_thld,
            "contribution_ratio" : contribution_thld,
            # "adjusted_odds_ratio" : self._or_thld,
            # "corrected_p_value" : self._p_val_thld,
            # "adjusted_p_value" : p_val_thld
        }

    ##TODO: Update these get functions

    def _get_selected_subgrouops(self) -> int:
        return len(self._top_subgroups)

    def _get_unselected_subgroups(self) -> int:
        return self._visited_subgroups - len(self._top_subgroups)

    def _get_visited_subgroups(self) -> int:
        return self._visited_subgroups

    def _get_top_subgroups(self) -> list[Pattern]:
        return self._top_subgroups
    
    selected_subgroups = property(_get_selected_subgrouops, None, None, "The number of selected subgroups.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "The number of unselected subgroups.")
    visited_subgroups = property(_get_visited_subgroups, None, None, "The number of visited subgroups.")
    top_subgroups = property(_get_top_subgroups, None, None, "The list of the selected patterns.")

    def _reduce_categories(self,df : DataFrame,tuple_target_attribute_value: tuple) -> DataFrame:
        """ Method to reduce the number of different values for the categorical attributes. If cats = -1, we take all the values.
        Otherwise, we take the cats-1 most frequent ones and the rest of them are grouped in the "other" value.

        :param df: the dataset.
        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        :return: the dataset with the reduced number of different values for the categorical attributes.
        
        """

        # If we don't have to limit the number of values, we take all of them.
        if self._cats == -1:
            return df
        
        df_without_target = df.drop(columns=[tuple_target_attribute_value[0]])
        for column in df_without_target:
            # Number of different values for the current column.
            n_values = df_without_target[column].nunique()
            # If we don't have to limit the number of values, we take all of them.
            if (n_values <= self._cats):
                continue
            else:
                value_counts = df_without_target[column].value_counts()
                # We edit our copy of the dataset to set the "other" value to the rows which have a value that is not in the top_values.
                # If the "other" value is already in the dataset, we need to make sure that the added value is different.
                other_string = "other"
                while other_string in value_counts.index:
                    other_string += "_"
                # Least frequent values. These values will be grouped in the "other" value.
                other_values = value_counts.nsmallest(n_values - self._cats+1).index
                # We edit our copy of the dataset to set the "other" value to the rows which have a value that is not in the top_values.
                df.loc[df_without_target[column].isin(other_values), column] = other_string
        return df

    def _generate_candidate_selectors(self,df : DataFrame, tuple_target_attribute_value: tuple) -> list[Selector]:
        """ Method to generate the set of candidate selectors for the SQFinder algorithm.

        :param df: the dataset after reducing the number of different values for the categorical attributes.
        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        :return: the set of candidate selectors.

        """
        selectors = []
        for column in df:
            for value in df[column].unique():
                selectors.append(Selector(column, Operator.EQUAL, value))
        return selectors
    
    def _handle_individual_result(self, df: DataFrame, target_column: Series, selectors: tuple, appearance: Series) -> int:
        """Method to compute the credibility measures for a pattern.

        :param df: the dataset.
        :param target_column: the target column of the dataset represented as a pandas Series of booleans (True if equal to the target value, False otherwise).
        :param selectors: tuple of selectors that represent the pattern.
        :param appearance: the appearance of the pattern in the dataset as a pandas Series.

        """
        if type(df) is not DataFrame:
            raise TypeError("The type of the parameter 'df' must be 'DataFrame'.")
        if type(selectors) is not tuple:
            raise TypeError("The type of the parameter 'subset' must be 'tuple'.")
        if type(appearance) is not Series or appearance.dtype != bool:
            raise TypeError("The type of the parameter 'appearance' must be 'Series' and its dtype must be 'bool'.")
        
        # WARNING: Corrected measures for confounders are not implemented yet

        linear_model = sm.GLM(target_column, appearance, family=sm.families.Binomial()).fit()
        odds_ratio = np.exp(linear_model.params.iloc[0])
        p_value = linear_model.pvalues.iloc[0]
        coverage = appearance.sum() / len(appearance)


        if len(selectors) == 1:
                minimum_absolute_contribution = 1
                maximum_absolute_contribution = 1
        else:
            minimum_absolute_contribution = 1
            maximum_absolute_contribution = 0
            for selector in selectors:
                pattern_without_selector = list(selectors)
                pattern_without_selector.remove(selector)
                appearance_without_selector = None
                for s in pattern_without_selector:
                    if appearance_without_selector is None:
                        appearance_without_selector = df[s.attribute_name] == s.value
                    else:
                        appearance_without_selector = appearance_without_selector & (df[s.attribute_name] == s.value)
                linear_model = sm.GLM(target_column, appearance_without_selector, family=sm.families.Binomial()).fit()
                patter_wo_selector_odds_ratio = np.exp(linear_model.params.iloc[0])
                contribution = odds_ratio / patter_wo_selector_odds_ratio
                minimum_absolute_contribution = min(minimum_absolute_contribution, contribution)
                maximum_absolute_contribution = max(maximum_absolute_contribution, contribution)
        
        absolute_contribution = minimum_absolute_contribution
        if absolute_contribution == 0:
            contribution_ratio = np.inf
        else:
            contribution_ratio = maximum_absolute_contribution / minimum_absolute_contribution
        #TODO: We cannot apply Bonferroni correction since we need the total number of tested patterns.
        # adjusted_p_value = p_value * len(canidadate_patterns)
        credibility = {
            "coverage": coverage,
            "odds_ratio": odds_ratio,
            "p_value": p_value,
            "absolute_contribution": absolute_contribution,
            "contribution_ratio": contribution_ratio,
            # "adjusted_odds_ratio": adjusted_odds_ratio,
            # "corrected_p_value": corrected_p_value,
            # "adjusted_p_value": adjusted_p_value
        }
        return credibility


    def _compute_rank(self,credibility: bitarray) -> int:
        """Method to compute the rank of a pattern.

        :param credibility: the bitarray representing the pattern's credibility.
        :return: the rank of the pattern.
        """
        rank = 0
        # Since most of the ranks are achieved only if the previous ones are also achieved, we can stop the loop when we find the first rank that is not achieved.
        # This won't work for the fifth rank, since it only requieres that either the third or the fourth rank are achieved (and its own criterion).
        for i in range(len(credibility)):
            # The fifth rank consists in subgroups of rank 3 OR 4 that also satisfy the fifth criterion, so we do not exit the loop if the fourth criterion is not satisfied.
            if not credibility[i] and i!=3:
                break
            if credibility[i]:
                rank = i+1
        return rank

    def _generate_top_subgroups(self,df : DataFrame, tuple_target_attribute_value: tuple):
        """Method to generate the set of top subgroups for the SQFinder algorithm.

        :param df: the dataset after reducing the number of different values for the categorical attributes.
        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        :param max_complexity: the maximum length of the patterns.

        """
        if type(df) is not DataFrame:
            raise TypeError("The type of the parameter 'df' must be 'DataFrame'.")
        if type(tuple_target_attribute_value) is not tuple:
            raise TypeError("The type of the parameter 'tuple_as_target' must be 'tuple'.")
        if (len(tuple_target_attribute_value) != 2):
            raise InconsistentMethodParametersError("The parameter 'tuple_as_target' must contain two elements.")
        if (not is_string_dtype(df[tuple_target_attribute_value[0]])):
            raise DatasetAttributeTypeError("The attribute '{}' must be a string.".format(tuple_target_attribute_value[0]))
        
        df = self._reduce_categories(df, tuple_target_attribute_value)
        selectors = self._generate_candidate_selectors(df, tuple_target_attribute_value)
        top_subgroups = []
        target_column_as_boolean = df[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]
        if self._max_complexity == -1:
            self._max_complexity = len(selectors)
        for length in range(1, self._max_complexity+1):
            for subset in itertools.combinations(selectors, length):
                self._visited_subgroups += 1
                # If we are taking twice the same column, the pattern is not valid.
                attributes = []
                for selector in subset:
                    attributes.append(selector.attribute_name)
                if len(attributes) != len(set(attributes)):
                    continue
                # Bit array to store the appearance of the pattern in each row of the dataset.
                appearance = None
                for selector in subset:
                    if appearance is None:
                        appearance = df[selector.attribute_name] == selector.value
                    else:
                        appearance = appearance & (df[selector.attribute_name] == selector.value)
                # If the pattern does not appear in the dataset, we continue to the next pattern.
                if appearance.sum() == 0:
                    continue
                # We compute the credibility measures for the pattern.
                credibility_values = self._handle_individual_result(df, target_column_as_boolean, subset, appearance)
                # We compute the total credibility of the pattern, represented as an array of booleans (True if the credibility measure is better than the threshold, False otherwise).
                credibility = bitarray()
                for cred in SQFinder._credibility_criterions:
                    # The credibility_criterions dictionary contains the function to compare the credibility measure with the threshold.
                    credibility.append(SQFinder._credibility_criterions[cred](credibility_values[cred],self._thresholds[cred]))
                # We compute the numerical rank of the pattern given its credibility.
                rank = self._compute_rank(credibility)
                # We obtain the p_value and effect size (odds ratio) for the pattern. We will use these values to select the top subgroups.
                p_value = credibility_values["p_value"]
                odds_ratio = credibility_values["odds_ratio"]
                # Create the pattern object and check if we can add it to the list of top subgroups
                pattern = Pattern(list(subset))
                # The original pruning performed in QFinder cannot be performed here, since we have not sorted all
                # candidate patterns with the same complexity. We can only continue to the next pattern instead of to the next complexity.
                # Compute the minimum rank for top subgroups with the same complexity
                top_subgroups_with_same_complexity = [s for s in top_subgroups if len(s[0]) == len(pattern)]
                if len(top_subgroups_with_same_complexity) == 0:
                    min_rank = 0
                else:
                    min_rank = min([r for (_, r, _, _, _) in top_subgroups_with_same_complexity])
                # Max p-value for top subgroups (all complexities)
                if len(top_subgroups) == 0:
                    max_p_value = 0
                else:
                    max_p_value = max([p for _, _, p, _, _ in top_subgroups])
                if rank < min_rank and p_value > max_p_value and len(top_subgroups) == self._num_subgroups:
                    continue
                for s, s_rank, s_p_value, s_odds_ratio,s_credibility_values in top_subgroups:
                    if self._redundant(pattern, s):
                        if len(pattern) == len(s):
                            if s_rank < rank:
                                top_subgroups.remove((s, s_rank, s_p_value, s_odds_ratio,s_credibility_values))
                            elif rank < s_rank:
                                break # And continue to next combination of selectors
                            else: # rank == g_rank
                                if p_value < s_p_value:
                                    top_subgroups.remove((s, s_rank, s_p_value, s_odds_ratio,s_credibility_values))
                                else:
                                    break # And continue to next combination of selectors
                        else: # len(pattern) > len(g) since we generate the combinations in increasing order of length
                            if odds_ratio <= s_odds_ratio + self._delta:
                                break # And continue to next combination of selectors
                else: # If we didn't break, we add the pattern to the list of top subgroups
                    for s, s_rank, s_p_value, s_odds_ratio,s_credibility_values in top_subgroups:
                        if self._redundant(s, pattern) and len(pattern) > len(s) and \
                            odds_ratio > s_odds_ratio + self._delta and p_value < s_p_value:
                            top_subgroups.remove((s, s_rank, s_p_value, s_odds_ratio,s_credibility_values))
                    # Add the pattern to the list of top subgroups. If the list is full, we remove the subgroup with the highest p-value.
                    top_subgroups.append((pattern, rank, p_value, odds_ratio, credibility_values))
                    if len(top_subgroups) > self._num_subgroups:
                        top_subgroups = sorted(top_subgroups, key=lambda x: x[2])
                        top_subgroups.pop()
        self._top_subgroups = [Subgroup(s, Selector(tuple_target_attribute_value[0], Operator.EQUAL, tuple_target_attribute_value[1])) for s, _, _, _, _ in top_subgroups]
        self._top_subgroups_credibilities = [credibility for _, _, _, _, credibility in top_subgroups]
                        


    def _redundant(self,p1: Pattern, p2: Pattern) -> bool:
        """Check if two patterns are redundant.

        :param p1: the first pattern.
        :param p2: the second pattern.
        :return: True if the patterns are redundant, False otherwise.
        """
        # Since we are only using nominal attributes, we only need to check if one pattern is a refinement of the other. We consider a pattern to be a refinement of itself.
        return p1.is_refinement(p2,True) or p2.is_refinement(p1,True)
    
    def fit(self, pandas_dataframe: DataFrame, tuple_target_attribute_value: tuple) -> None:
        """Main method to run the QFinder algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        
        :param data: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        if type(pandas_dataframe) != DataFrame:
            raise TypeError("The dataset must be a pandas DataFrame.")
        if type(tuple_target_attribute_value) != tuple:
            raise TypeError("The target must be a tuple.")
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise DatasetAttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
        # We copy the DataFrame to avoid modifying the original when dealing with "other" values.
        df = pandas_dataframe.copy()
        self._generate_top_subgroups(df, tuple_target_attribute_value)
        if self._file_path is not None:
            self._to_file(self._file_path)

    #TODO: Update this method
    def test_subgroups(self,test_dataframe : DataFrame, tuple_target_attribute_value: tuple, write_to_file:bool=False, file_path: Union[str,None]=None):
        """Method to test the best subgroups on a different dataset. This method can only be called after the fit method.
        
        :param test_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: a dictionary with the credibility measures for each subgroup.
        """
        # We make sure that the fit method has been called before.
        if self._top_subgroups is None:
            raise ValueError("The fit method must be called before testing subgroups.")
        if type(test_dataframe) != DataFrame:
            raise TypeError("The dataset must be a pandas DataFrame.")
        if type(tuple_target_attribute_value) != tuple:
            raise TypeError("The target must be a tuple.")
        if type(write_to_file) != bool:
            raise TypeError("The write_to_file parameter must be a boolean.")
        # If wirte_to_file is True, file_path must not be None.
        if write_to_file and file_path is None:
            raise ValueError("The file path must be specified.")
        elif write_to_file and type(file_path) != str:
            raise TypeError("The file path must be a string.")
        # We generate a different bitset for the test dataset, which whill be used to compute the credibility measures.
        qfinder_bitset = Bitset_QFinder()
        qfinder_bitset.generate_bitset(test_dataframe, tuple_target_attribute_value, self._top_subgroups)
        coverages, odds_ratios, p_values, absolute_contributions, contribution_ratios, adjusted_p_values \
            = qfinder_bitset.compute_credibility_measures(test_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1])
        parameters = {
            "coverages": coverages,
            "odds_ratios": odds_ratios,
            "p_values": p_values,
            "absolute_contributions": absolute_contributions,
            "contribution_ratios": contribution_ratios,
            "adjusted_p_values": adjusted_p_values
        }
        if write_to_file:
            self._to_file(file_path, tuple_target_attribute_value, parameters)
        return parameters
    
    def _to_file(self, file_path):
        """Writes the top-k patterns to a file.

        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        self._file = open(file_path, "w")
        # for subgroup,_,_,_,credibility_values in self._top_subgroups:
        for i in range(len(self._top_subgroups)):
            subgroup = self._top_subgroups[i]
            credibility_values = self._top_subgroups_credibilities[i]
            self._file.write(str(subgroup) + " ; ")
            for cred in credibility_values:
                self._file.write(cred + ": " + str(credibility_values[cred]) + " ; ")
            self._file.write("\n")
        self._file.close()
        self._file = None
