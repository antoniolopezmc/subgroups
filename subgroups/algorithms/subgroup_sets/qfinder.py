# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the QFinder algorithm.
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
from subgroups.data_structures.bitset_qfinder import Bitset_QFinder
import operator

class QFinder(Algorithm):
    """
    This class represents the QFinder algorithm.

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

    __slots__ = ('_num_subgroups','_cats', '_max_complexity', '_thresholds','_credibility_values' , '_file', '_file_path' , '_df','_delta', '_num_subgroups', '_top_patterns','_selectors', '_candidate_patterns')

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
        "adjusted_p_value" : operator.le
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
        self._top_patterns = []
        self._candidate_patterns = []
        self._selectors = []
        # Thresholds for each credibility measure.
        self._thresholds = {
            "coverage" : coverage_thld,
            "odds_ratio" : or_thld,
            "p_value" : p_val_thld,
            "absolute_contribution" : abs_contribution_thld,
            "contribution_ratio" : contribution_thld,
            # "adjusted_odds_ratio" : self._or_thld,
            # "corrected_p_value" : self._p_val_thld,
            "adjusted_p_value" : p_val_thld
        }

    def _get_selected_subgrouops(self) -> int:
        return len(self._top_patterns)

    def _get_unselected_subgroups(self) -> int:
        return len(self._candidate_patterns) - len(self._top_patterns)

    def _get_visited_subgroups(self) -> int:
        return len(self._candidate_patterns)

    def _get_top_patterns(self) -> list[Pattern]:
        return self._top_patterns
    
    selected_subgroups = property(_get_selected_subgrouops, None, None, "The number of selected subgroups.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "The number of unselected subgroups.")
    visited_subgroups = property(_get_visited_subgroups, None, None, "The number of visited subgroups.")
    top_patterns = property(_get_top_patterns, None, None, "The list of the selected patterns.")

    def _generate_candidate_patterns(self,df : DataFrame, tuple_target_attribute_value: tuple) -> None:
        """Method to generate the set of candidate patterns for the QFinder algorithm.

        :param df: the dataset.
        :param tuple_as_target: the tuple which contains the target attribute name and the target attribute values.
        """
        if type(df) is not DataFrame:
            raise TypeError("The type of the parameter 'df' must be 'DataFrame'.")
        if type(tuple_target_attribute_value) is not tuple:
            raise TypeError("The type of the parameter 'tuple_as_target' must be 'tuple'.")
        if (len(tuple_target_attribute_value) != 2):
            raise InconsistentMethodParametersError("The parameter 'tuple_as_target' must contain two elements.")
        if (not is_string_dtype(df[tuple_target_attribute_value[0]])):
            raise DatasetAttributeTypeError("The attribute '{}' must be a string.".format(tuple_target_attribute_value[0]))
        # We do not generate patterns with the target attribute.
        df_without_target = df.drop(columns=[tuple_target_attribute_value[0]])
        # We generate the list of selectors. We will use them to generate the candidate patterns.
        selectors = []
        for column in df_without_target:
            # Number of different values for the current column.
            n_values = df_without_target[column].nunique()
            # If we don't have to limit the number of values, we take all of them.
            if (n_values <= self._cats or self._cats == -1):
                for value in df_without_target[column].unique():
                    # We will save each selector (column = value) as a pattern.
                    selectors.append(Selector(column, Operator.EQUAL, value))
            # If we have to limit the number of values, we take the cats-1 most frequent ones and the rest of them are grouped in the "other" value.
            else:
                value_counts = df_without_target[column].value_counts()
                # If the "other" value is already in the dataset, we need to make sure that the added value is different.
                other = "other"
                while other in value_counts.index:
                    other += "_"
                # Most frequent values.
                top_values = value_counts.nlargest(self._cats-1).index
                # Least frequent values. These values will be grouped in the "other" value.
                other_values = value_counts.nsmallest(n_values - self._cats + 1).index
                for value in top_values:
                    selectors.append(Selector(column, Operator.EQUAL, value))
                # We edit our copy of the dataset to set the "other" value to the rows which have a value that is not in the top_values.
                df_without_target.loc[df_without_target[column].isin(other_values), column] = other
                selectors.append(Selector(column, Operator.EQUAL, other))
        selectors = Series(selectors)
        candidate_patterns = []
        if (self._max_complexity == -1):
            self._max_complexity = len(df_without_target.columns)
        # We generate the list of candidate patterns by combining the selectors. Each pattern is represented as a pandas Series of booleans, where each boolean represents a selector.
        for complexity in range(1, self._max_complexity+1):
            for subset in itertools.combinations(selectors.index, complexity):
                # Initialize the pattern with False values.
                pattern = Series(False, index = selectors.index)
                # Set the values of the pattern to True if the selector is in the subset.
                pattern.loc[list(subset)] = True
                candidate_patterns.append(pattern)
        self._candidate_patterns = candidate_patterns
        self._selectors = selectors

    def _handle_individual_result(self,credibility: list[bool]) -> int:
        """Method to compute the rank of a pattern.

        :param credibility: the list of booleans representing the pattern's credibility.
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

    def _redundant(self,p1: Series, p2: Series) -> bool:
        """Check if two patterns are redundant.

        :param p1: the first pattern (as a Series).
        :param p2: the second pattern (as a Series).
        :return: True if the patterns are redundant, False otherwise.
        """
        # Since we are only using nominal attributes, we only need to check if one pattern is a refinement of the other. We consider a pattern to be a refinement of itself.
        # Since we are also representing the patterns as pandas Series, we can use logical operations to check if a pattern is a refinement of the other.
        return (p1 & p2).equals(p1) or (p1 & p2).equals(p2)

    def _rank_patterns(self) -> list[Pattern]:
        """Method to assing a rank to each of the candidate patterns.

        :return: the list of candidate patterns sorted by their rank.
        """
        # We first sort the patterns by their p_value. This sorting will be used in case of ties in the ranking.
        sorted_patterns = sorted(self._candidate_patterns, key=lambda pattern: self._credibility_values["p_value"][pattern.astype(int).astype(str).str.cat()])
        ranks = []
        for pattern in sorted_patterns:
            pattern_key = pattern.astype(int).astype(str).str.cat()
            # We compute the credibility of each pattern. The credibility of a pattern is a list of booleans, where each boolean represents a criterion.
            credibility = []
            for cred in QFinder._credibility_criterions:
                credibility.append(QFinder._credibility_criterions[cred](self._credibility_values[cred][pattern_key],self._thresholds[cred]))
            # We compute the rank of the pattern.
            rank = self._handle_individual_result(credibility)
            ranks.append(rank)
        sorted_patterns_ranks = list(zip(sorted_patterns, ranks))
        # We sort the patterns according to their ranks.
        # If two patterns have the same rank, we sort them according to their appearance in sorted_patterns (i.e. according to their p-values).
        sorted_patterns_ranks.sort(key = lambda x:x[1], reverse = True)
        ranked_patterns = list(map(lambda x:x[0],sorted_patterns_ranks))
        return ranked_patterns

    def _select_top_k(self, ranked_patterns) -> list[Pattern]:
        """Method to select the top-k patterns according to the ranking and the redundancy criterion.

        :param ranked_patterns: the list of candidate patterns sorted by their rank.
        :return: the list of top-k patterns.
        """
        top_k_patterns = []
        # We separate the patterns by their length
        ranked_patterns_by_length = {}
        for pattern_as_series in ranked_patterns:
            if (pattern_as_series.sum() not in ranked_patterns_by_length):
                ranked_patterns_by_length[pattern_as_series.sum()] = []
            ranked_patterns_by_length[pattern_as_series.sum()].append(pattern_as_series)
        # We iterate over the patterns by length, from the shortest to the longest.
        for length in sorted(ranked_patterns_by_length.keys()):
            for pattern_as_series in ranked_patterns_by_length[length]:
                pattern_key = pattern_as_series.astype(int).astype(str).str.cat()
                # If p-value(pattern) > max(p-value(top_k_patterns)) and |top_k_patterns| == k, we continue to the next length.
                if (len(top_k_patterns) == self._num_subgroups) and (self._credibility_values["p_value"][pattern_key] > max(map(lambda pattern: self._credibility_values["p_value"][pattern.astype(int).astype(str).str.cat()], top_k_patterns))):
                    break
                # We check the redundancy of the pattern with the patterns in top_k_patterns. Breaking the loop means that the pattern is redundant and we continue to the next pattern.
                for top_pattern_as_series in top_k_patterns:
                    top_pattern_key = top_pattern_as_series.astype(int).astype(str).str.cat()
                    if self._redundant(pattern_as_series, top_pattern_as_series):
                        # If the complexity of both patterns is the same, we continue to the next pattern.
                        if pattern_as_series.sum() == top_pattern_as_series.sum():
                            break
                        # If the effect size (odds_ratio) of the pattern is not significantly larger than the effect size of the top pattern, we continue to the next pattern.
                        if pattern_as_series.sum() > top_pattern_as_series.sum() and self._credibility_values["odds_ratio"][pattern_key] <= self._credibility_values["odds_ratio"][top_pattern_key] + self._delta:
                            break
                else: 
                    # If we didn't break, the pattern is not redundant or we justify the redundancy with a high effect size.
                    # In this case, we remove the patterns in top_k_patterns that are redundant with the new pattern and we add the pattern to top_k_patterns.
                    patterns_to_remove = []
                    for top_pattern_as_series in top_k_patterns:
                        if self._redundant(pattern_as_series,top_pattern_as_series) and pattern_as_series.sum() > top_pattern_as_series.sum() and \
                            self._credibility_values["odds_ratio"][pattern_key] > self._credibility_values["odds_ratio"][top_pattern_key] + self._delta and \
                                self._credibility_values["p_value"][pattern_key] < self._credibility_values["p_value"][top_pattern_key]:
                            # top_k_patterns.remove(top_pattern_as_series)
                            patterns_to_remove(list(top_pattern_as_series))
                    top_k_patterns = list(filter(lambda p : list(p) not in patterns_to_remove , top_k_patterns))
                    
                    top_k_patterns.append(pattern_as_series)
                    # If |top_k_patterns| > k, we remove the pattern with the highest p-value.
                    if len(top_k_patterns) > self._num_subgroups:
                        max_p_val_pattern = max(top_k_patterns, key=lambda pattern: self._credibility_values["p_value"][pattern.astype(int).astype(str).str.cat()])
                        # top_k_patterns.remove(max_p_val_pattern)
                        top_k_patterns = list(filter(lambda p : list(p) != list(max_p_val_pattern), top_k_patterns))
        return top_k_patterns
    
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
        # We generate the list of candidate patterns.
        self._generate_candidate_patterns(df, tuple_target_attribute_value)
        # We compute the credibility measures for each candidate pattern using the bitset structure.
        qfinder_bitset = Bitset_QFinder()
        qfinder_bitset.generate_bitset(df, tuple_target_attribute_value, self._candidate_patterns, self._selectors)
        self._candidate_patterns = qfinder_bitset.get_non_empty_patterns()
        self._credibility_values = qfinder_bitset.compute_credibility_measures(df[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1])
        ranked_patterns = self._rank_patterns()
        self._top_patterns = self._select_top_k(ranked_patterns)
        if self._file_path is not None:
            self._to_file(self._file_path,tuple_target_attribute_value, self._credibility_values)

    def test_subgroups(self,test_dataframe : DataFrame, tuple_target_attribute_value: tuple, write_to_file:bool=False, file_path: Union[str,None]=None):
        """Method to test the best subgroups on a different dataset. This method can only be called after the fit method.
        
        :param test_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: a dictionary with the credibility measures for each subgroup.
        """
        # We make sure that the fit method has been called before.
        if self._top_patterns is None:
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
        qfinder_bitset.generate_bitset(test_dataframe, tuple_target_attribute_value, self._top_patterns)
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
    
    def _to_file(self, file_path, target, credibility_values):
        """Writes the top-k patterns to a file.

        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        self._file = open(file_path, "w")
        for pat_as_series in self._top_patterns:
            pat_selectors = []
            pat_key = pat_as_series.astype(int).astype(str).str.cat()
            for i, value in pat_as_series.items():
                if value:
                    pat_selectors.append(self._selectors[i])
            subgroup = Subgroup(Pattern(pat_selectors), Selector(target[0], Operator.EQUAL, target[1]))
            self._file.write(str(subgroup) + " ; ")
            for cred in credibility_values:
                self._file.write(cred + ": " + str(credibility_values[cred][str(pat_key)]) + " ; ")
            self._file.write("\n")
        self._file.close()
        self._file = None
