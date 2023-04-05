# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the QFinder algorithm.
"""

import itertools
from typing import Union
from pandas import DataFrame
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from bitarray import bitarray
from subgroups.data_structures.bitset_qfinder import Bitset_QFinder



def compute_rank(credibility: list[bool]) -> int:
    rank = 0
    for i in range(len(credibility)):
        # The fifth rank are subgroups of rank 3 OR 4 that also satisfy the fifth criterion, so we do not exit the loop is the fourth criterion is not satisfied.
        if not credibility[i] and i!=3:
            break
        if credibility[i]:
            rank = i+1
    return rank




def redundant(p1: Pattern, p2: Pattern) -> bool:
    # Since we are only using nominal attributes, we only need to check if one pattern is a subset of the other.
    pmin = p1 if len(p1) < len(p2) else p2
    pmax = p1 if len(p1) >= len(p2) else p2
    for s in pmin:
        if not s in pmax:
            return False
    return True

class QFinder(Algorithm):
    """
    This class represents the algorithm BSD (algorithm for subgroup discovery).

    :param cats: the number of maximum values for each column. If there is more values, we take the most frequent ones. If this value is -1, we take all the values.
    :param max_complexity: the maximum complexity (length) of the patterns.
    :param coverage_thld: the minimum coverage threshold.
    :param or_thld: the minimum odds ratio and adjusted odds ratio threshold.
    :param p_val_thld: the maximum p-value threshold. This threshold is used for p-values corrected for confounders and adjusted p-values.
    :param abs_contribution_thld: the minimum absolute contribution threshold.
    :param contribution_thld: the minimum contribution ratio threshold.
    :param write_results_in_file: if True, the results will be written in a file.
    :param file_path: the path of the file where the results will be written.
    :param delta: minimum delta to consider that a subgroup has a higher effect size.
    :param num_subgroups: the number of top subgroups to return.
    """

    __slots__ = ['_cats', '_max_complexity', '_coverage_thld', '_or_thld', '_p_val_thld', '_abs_contribution_thld', '_contribution_thld', '_file', '_file_path', '_df', '_coverages', '_odds_ratios', '_p_values', '_absolute_contributions', '_contribution_ratios', '_adjusted_odds_ratios', '_corrected_p_values', '_adjusted_corrected_p_values','_delta', '_num_subgroups']

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
        
        self._cats = cats
        self._max_complexity = max_complexity
        self._coverage_thld = coverage_thld
        self._or_thld = or_thld
        self._p_val_thld = p_val_thld
        self._abs_contribution_thld = abs_contribution_thld
        self._contribution_thld = contribution_thld
        self._delta = delta
        if (write_results_in_file):
                self._file_path = file_path
        else:
            self._file_path = None
        self._file = None
        self._top_patterns = []
        self._candidate_patterns = []
        self._top_patterns = []

    def _get_selected_subgrouops(self) -> int:
        return len(self._top_patterns)
    def _get_unselected_subgroups(self) -> int:
        return len(self._candidate_patterns) - len(self._top_patterns)

    def _get_top_patterns(self) -> list[Pattern]:
        return self._top_patterns
    

    selected_subgroups = property(_get_selected_subgrouops, None, None, "The number of selected subgroups.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "The number of unselected subgroups.") 
    top_patterns = property(_get_top_patterns, None, None, "The list of the selected patterns.")

    def _generate_candidate_patterns(self,df : DataFrame, tuple_target_attribute_value: tuple, max_complexity : int ,cats : int = -1) -> list[Pattern]:
        """Method to generate the set of candidate patterns for the QFinder algorithm.

        :param df: the dataset.
        :param tuple_as_target: the tuple which contains the target attribute name and the target attribute values.
        :param cats: the number of maximum values for each column. If there is more values, we take the most frequent ones. If this value is -1, we take all the values.
        :return: the set of candidate patterns.
        """
        if type(df) is not DataFrame:
            raise TypeError("The type of the parameter 'df' must be 'DataFrame'.")
        if type(tuple_target_attribute_value) is not tuple:
            raise TypeError("The type of the parameter 'tuple_as_target' must be 'tuple'.")
        if type(cats) is not int:
            raise TypeError("The type of the parameter 'cats' must be 'int'.")
        if type(max_complexity) is not int:
            raise TypeError("The type of the parameter 'max_complexity' must be 'int'.")
        if (len(tuple_target_attribute_value) != 2):
            raise InconsistentMethodParametersError("The parameter 'tuple_as_target' must contain two elements.")
        if (not is_string_dtype(df[tuple_target_attribute_value[0]])):
            raise DatasetAttributeTypeError("The attribute '{}' must be a string.".format(tuple_target_attribute_value[0]))
        
        df_without_target = df.drop(columns=[tuple_target_attribute_value[0]])

        # We generate the list of candidate simple patterns (length 1).
        simple_patterns = []

        for column in df_without_target:
            n_values = len(df_without_target[column].unique())
            # If we don't have to limit the number of values, we take all of them.
            if (n_values <= cats or cats == -1):
                for value in df_without_target[column].unique():
                    simple_patterns.append(Pattern([Selector(column, Operator.EQUAL, value)]))
            # If we have to limit the number of values, we take the cats-1 most frequent ones and the rest of them are grouped in the "other" value.
            else:
                value_counts = df_without_target[column].value_counts()
                # If the "other" value is already in the dataset, we need to make sure that the added value is different.
                other = "other"
                while other in value_counts.index:
                    other += "_"
                top_values = value_counts.nlargest(cats-1).index
                other_values = value_counts.nsmallest(n_values - cats + 1).index
                for value in top_values:
                    simple_patterns.append(Pattern([Selector(column, Operator.EQUAL, value)]))
                # We edit the dataset to set the "other" value to the rows which have a value that is not in the top_values.
                df_without_target.loc[df_without_target[column].isin(other_values), column] = other
                simple_patterns.append(Pattern([Selector(column, Operator.EQUAL, other)]))
        
        complex_patterns = []

        # We generate the list of candidate patterns by combining the simple patterns.
        for L in range(2, max_complexity):
            # We take each combination of L simple patterns.
            for subset in itertools.combinations(simple_patterns, L):
                column_values = [ s.get_selector(0).attribute_name for s in subset ]
                # If we are taking twice the same column, the pattern is not valid.
                if (len(column_values) != len(set(column_values))):
                    continue
                pattern = Pattern([])
                for s in subset:
                    pattern.add_selector(s.get_selector(0))
                complex_patterns.append(pattern)
        
        return simple_patterns + complex_patterns



    def rank_patterns(self) -> list[Pattern]:
        sorted_patterns = sorted(self._patterns, key=lambda pattern: self._p_values[str(pattern)])
        ranks = []
        for i in range(len(sorted_patterns)):
            pattern = sorted_patterns[i]
            credibility = []
            credibility.append((self._coverages[str(pattern)]>= self._coverage_thld))
            credibility.append((self._odds_ratios[str(pattern)]>= self._or_thld))
            credibility.append((self._p_values[str(pattern)]<= self._p_val_thld))
            credibility.append((self._absolute_contributions[str(pattern)]>= self._abs_contribution_thld))
            credibility.append((self._contribution_ratios[str(pattern)]<= self._contribution_thld))
            credibility.append((self._adjusted_odds_ratios[str(pattern)]>= self._or_thld))
            credibility.append((self._corrected_p_values[str(pattern)]<= self._p_val_thld))
            credibility.append((self._adjusted_corrected_p_values[str(pattern)]<= self._p_val_thld))
            rank = compute_rank(credibility)
            ranks.append(rank)
        # We sort the patterns according to their ranks.
        # If two patterns have the same rank, we sort them according to their appearance in sorted_patterns (i.e. according to their p-values).
        ranked_patterns = sorted(sorted_patterns, key=lambda pattern: ranks[sorted_patterns.index(pattern)], reverse=True)
        return ranked_patterns



    def _select_top_k(self, ranked_patterns) -> list[Pattern]:
        top_k_patterns = []
        ranked_patterns_by_length = {}
        for pattern in ranked_patterns:
            if (len(pattern) not in ranked_patterns_by_length):
                ranked_patterns_by_length[len(pattern)] = []
            ranked_patterns_by_length[len(pattern)].append(pattern)
        for length in ranked_patterns_by_length:
            for pattern in ranked_patterns_by_length[length]:
                if self._p_values[str(pattern)] <= max(map(lambda pattern: self._p_values[str(pattern)], top_k_patterns)) and len(top_k_patterns) == self._num_subgroups:
                    break
                for top_pattern in top_k_patterns:
                    if redundant(pattern, top_pattern):
                        if len(pattern) == len(top_pattern):
                            break
                        if len(pattern) > len(top_pattern) and self._odds_ratios[str(pattern)] <= self._odds_ratios[str(top_pattern)] + self._delta:
                            break
                else: 
                    # If we didn't break...
                    for top_pattern in top_k_patterns:
                        if redundant(pattern,top_pattern) and len(pattern) > len(top_pattern) and \
                            self._odds_ratios[str(pattern)] > self._odds_ratios[str(top_pattern)] + self._delta and \
                                self._p_values[str(pattern)] < self._p_values[str(top_pattern)]:
                            top_k_patterns.remove(top_pattern)
                    top_k_patterns.append(pattern)
                    if len(top_k_patterns) > self._num_subgroups:
                        max_p_val_pattern = max(top_k_patterns, key=lambda pattern: self._p_values[str(pattern)])
                        top_k_patterns.remove(max_p_val_pattern)
                
                # If we did break the first top_pattern in top_patterns loop, we continue to the next pattern.
                break
        return top_k_patterns

                    
    def fit(self, dataset: DataFrame, tuple_target_attribute_value: tuple) -> None:
        df = dataset.copy()
        self._candidate_patterns = self._generate_candidate_patterns(df, tuple_target_attribute_value, self._max_complexity, self._cats)
        qfinder_bitset = Bitset_QFinder()
        qfinder_bitset.generate_bitset(df, tuple_target_attribute_value, self._candidate_patterns)
        # coverages, odds_ratios, p_values,absolute_contributions, contribution_ratios, adjusted_odds_ratios, corrected_p_values, adjusted_corrected_p_values
        self._coverages, self._odds_ratios, self._p_values, self._absolute_contributions, self._contribution_ratios,self._adjusted_odds_ratios, self._corrected_p_values, self._adjusted_corrected_p_values \
            = qfinder_bitset.compute_confidence_measures()
        ranked_patterns = self.rank_patterns()
        self._top_patterns = self._select_top_k(ranked_patterns)
        if self._file_path is not None:
            self._to_file(tuple_target_attribute_value)
    
    def _to_file(self, target):
        self._file = open(self._file_path, "w")
        for pat in self._top_patterns:
            subgroup = Subgroup(pat, Selector(target[0], Operator.EQUAL, target[1]))
            self._file.write(str(subgroup) + " ; ")
            self._file.write("coverage: " + str(self._coverages[str(pat)]) + " ; ")
            self._file.write("odds_ratio: " + str(self._odds_ratios[str(pat)]) + " ; ")
            self._file.write("p_value: " + str(self._p_values[str(pat)]) + " ; ")
            self._file.write("absolute_contribution: " + str(self._absolute_contributions[str(pat)]) + " ; ")
            self._file.write("contribution_ratio: " + str(self._contribution_ratios[str(pat)]) + " ; ")
            self._file.write("adjusted_odds_ratio: " + str(self._adjusted_odds_ratios[str(pat)]) + " ; ")
            self._file.write("corrected_p_value: " + str(self._corrected_p_values[str(pat)]) + " ; ")
            self._file.write("adjusted_corrected_p_value: " + str(self._adjusted_corrected_p_values[str(pat)]) + " ; ")
            self._file.write("\n")
        
        

