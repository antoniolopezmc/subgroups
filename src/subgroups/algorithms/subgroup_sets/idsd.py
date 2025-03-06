# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles <fmora@um.es>

"""This file contains the implementation of the Iterative-Depeening Subgroup Discovery algorithm.
"""

from typing import Union
from pandas import DataFrame, Series
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.exceptions import DatasetAttributeTypeError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.quality_measures.coverage import Coverage
from subgroups.credibility_measures.odds_ratio_stat import OddsRatioStatistic
from subgroups.credibility_measures.p_value_independence import PValueIndependence
from subgroups.credibility_measures.selector_contribution import SelectorContribution
import operator
from math import inf

class IDSD(Algorithm):
    """This class implements the Iterative-Depeening Subgroup Discovery algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.

    :param num_subgroups: the number of subgroups to be selected.
    :param cats: the maximum number of different values for each column. If cats = -1, all the values are taken.
    :param max_complexity: the maximum size of the patterns to be generated. If max_complexity = -1, the maximum complexity is the number of attributes.
    :param coverage_thld: the minimum coverage threshold for the credibility measure.
    :param or_thld: the minimum odds ratio threshold for the credibility measure.
    :param p_val_thld: the maximum p-value threshold for the credibility measure.
    :param abs_contribution_thld: the minimum absolute contribution threshold for the credibility measure.
    :param contribution_thld: the maximum contribution ratio threshold for the credibility measure.
    :param write_results_in_file: a boolean to indicate if the results are written in a file.
    :param file_path: the path of the file where the results are written. If write_results_in_file is False, this parameter is ignored.
    """

    _credibility_criterions = {
        "coverage" :  operator.ge,
        "odds_ratio" : operator.ge,
        "p_value" : operator.le,
        "absolute_contribution" : operator.ge,
        "contribution_ratio" : operator.le,
    }

    __slots__ = ['_num_subgroups', '_cats', '_max_complexity', '_file', '_top_k_subgroups', '_visited_subgroups', '_non_unique_visited_subgroups', '_pruned_subgroups', '_selectors', '_thresholds','_file_path','_TP','_FP','_N', '_entry_template', '_selector_appearances', '_odds_ratio_measure', '_p_value_measure','_coverage_measure', '_selector_contribution_measure']

    def __init__(self, num_subgroups :int, cats : int = -1, max_complexity: int = -1, coverage_thld: float = 0.1, or_thld: float = 1.2, p_val_thld: float = 0.05, abs_contribution_thld: float = 0.2, contribution_thld: float = 5, write_results_in_file: bool = False, file_path: Union[str,None] = None) -> None:
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
        if type(write_results_in_file) is not bool:
            raise TypeError("The type of the parameter 'write_results_in_file' must be 'bool'.")
        if file_path is not None and type(file_path) is not str:
            raise TypeError("The type of the parameter 'file_path' must be 'str'.")
        # We check that that the parameter values are valid.
        if (num_subgroups < 1):
            raise ValueError("The parameter 'num_subgroups' must be greater than 0.")
        if (cats < -1) or (cats == 0):
            raise ValueError("The parameter 'cats' must be greater than zero or equal to -1.")
        if (coverage_thld < 0 or coverage_thld > 1):
            raise ValueError("The parameter 'coverage_thld' must be between 0 and 1.")
        if (or_thld < 0):
            raise ValueError("The parameter 'or_thld' must be greater than or equal to 0.")
        if (p_val_thld < 0 or p_val_thld > 1):
            raise ValueError("The parameter 'p_val_thld' must be between 0 and 1.")
        if (abs_contribution_thld < 0):
            raise ValueError("The parameter 'abs_contribution_thld' must be greater than or equal to 0.")
        if (contribution_thld < 0):
            raise ValueError("The parameter 'contribution_thld' must be greater than or equal to 0.")
        # If 'write_results_in_file' is True, 'file_path' must not be None.
        if (write_results_in_file) and (file_path is None):
            raise ValueError("If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        # Initialize the number of unique subgroups explored
        self._visited_subgroups = 0
        # Initialize the number of non-unique subgroups explored (this includes the same subgroup visited multiple times when performing the iterative deepening search).
        self._non_unique_visited_subgroups = 0
        # Initialize the number of pruned subgroups.
        self._pruned_subgroups = 0
        self._num_subgroups = num_subgroups
        self._cats = cats
        self._max_complexity = max_complexity
        if (write_results_in_file):
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None
        self._top_k_subgroups = []
        self._selectors = []
        # Thresholds for each credibility measure.
        self._thresholds = {
            "coverage" : coverage_thld,
            "odds_ratio" : or_thld,
            "p_value" : p_val_thld,
            "absolute_contribution" : abs_contribution_thld,
            "contribution_ratio" : contribution_thld,
        }
        # Dictionary used to save the appearance of each selector in the dataset (key: Selector, value: pandas series of boolean values).
        self._selector_appearances = dict()
        # We initialize the credibility measures objects.
        self._coverage_measure = Coverage()
        self._odds_ratio_measure = OddsRatioStatistic()
        self._p_value_measure = PValueIndependence()
        self._selector_contribution_measure = SelectorContribution()


    def _get_selected_subgroups(self) -> int:
        return len(self._top_k_subgroups)

    def _get_unselected_subgroups(self) -> int:
        return self._visited_subgroups - len(self._top_k_subgroups)

    def _get_visited_subgroups(self) -> int:
        return self._visited_subgroups
    
    def _get_non_unique_visited_subgroups(self) -> int:
        return self._non_unique_visited_subgroups.value

    def _get_top_patterns(self) -> list[Pattern]:
        return self._top_k_subgroups.copy()
    
    def _get_pruned_subgroups(self) -> int:
        return self._pruned_subgroups
    
    selected_subgroups = property(_get_selected_subgroups, None, None, "The number of selected subgroups.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "The number of unselected subgroups.")
    visited_subgroups = property(_get_visited_subgroups, None, None, "The number of unique visited subgroups. We don't count the same subgroup twice when iterating the maximum complexity.")
    pruned_subgroups = property(_get_pruned_subgroups, None, None, "The number of pruned subgroups by the coverage.")
    non_unique_visited_subgroups = property(_get_non_unique_visited_subgroups, None, None, "The number of non-unique visited subgroups. Subgroups are considered each time they are visited.")
    top_patterns = property(_get_top_patterns, None, None, "The list of the selected patterns.")


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
                # Appearances of each value in the column.
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
        
    def _generate_selectors(self,df : DataFrame,tuple_target_attribute_value: tuple) -> Series:
        """ 
        Method to generate the list of selectors in a given dataset.
        We use this function after reducing the number of categories.

        :param df: the dataset.
        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        """
        selectors = []
        for column in df.columns:
            # We don't generate selectors for the target attribute.
            if column != tuple_target_attribute_value[0]:
                for value in df[column].unique():
                    sel = Selector(column,Operator.EQUAL,value)
                    selectors.append(sel)
                    # Pandas series recording the appearance of the selector in the dataset.
                    appearance = df[column] == value
                    # We store the appearance of the selector in the dataset. This will be used to compute the credibility measures of the discovered patterns.
                    self._selector_appearances[sel] = appearance
        return selectors
    
    def _handle_individual_result(self,target_column: Series, pattern: Pattern, appearance: Series) -> None:
        """ Method to compute the credibility measures of a pattern, its rank and update the top-k subgroups.
        
        :param target_column: the target column of the dataset represented as a pandas Series of booleans (True if equal to the target value, False otherwise).
        :param pattern: the pattern to be evaluated.
        :param appearance: pandas boolean Series containing the rows that satisfy the pattern.
        """

        # We compute the number of true positives and false positives using the target column and the appearance of the pattern.
        tp = (target_column & appearance).sum()
        fp = appearance.sum() - tp
        # Parameters for each credibility measure. Contributions are computed at the same time.
        credibility_parameters = {
            "coverage" : {"tp": tp, "fp": fp, "TP": self._TP, "FP": self._FP},
            "odds_ratio" : {"tp": tp, "fp": fp, "TP": self._TP, "FP": self._FP},
            "p_value" : {"tp": tp, "fp": fp, "TP": self._TP, "FP": self._FP},
            "contributions" : {"pattern": pattern, "target_appearance": target_column, "selector_appearances": self._selector_appearances, "odds_ratio_definition": "statistic"},
        }
        # If the credibility measure does not meet the threshold, we do not compute the rest of the credibility measures.
        # We store the credibility values in a dictionary and initialize them as the worst possible values.
        credibility_values = {
            "coverage": -inf,
            "odds_ratio": -inf,
            "p_value": inf,
            "absolute_contribution": -inf,
            "contribution_ratio": inf
        }
        for cred in credibility_parameters:
            if cred != "contributions":
                measure_value = getattr(self,"_" + cred + "_measure").compute(credibility_parameters[cred])
                credibility_values[cred] = measure_value
                # If the credibility measure does not meet the threshold, we do not need to compute the rest of the credibility measures.
                # This is because the rank is computed as the number of consecutive True values in the credibility list.
                if not IDSD._credibility_criterions[cred](credibility_values[cred],self._thresholds[cred]):
                    break
            # Contribution measures are computed both at the same time and at the last iteration.
            else:
                absolute_contribution, contribution_ratio = self._selector_contribution_measure.compute(credibility_parameters[cred])
                credibility_values["absolute_contribution"] = absolute_contribution
                credibility_values["contribution_ratio"] = contribution_ratio
        # The credibility of a patterns is represented as a list of booleans,
        # where each element is True if the credibility measure meets the threshold and False otherwise.
        credibility = []
        for cred in IDSD._credibility_criterions:
            # The credibility_criterions dictionary contains the function to compare the credibility measure with the threshold.
            # The dictionaries credibility_values, thresholds and credibility_criterions have the same keys (the credibility measures).
            credibility.append(IDSD._credibility_criterions[cred](credibility_values[cred],self._thresholds[cred]))
        # We compute the numerical rank of the pattern given its credibility.
        rank = self._compute_rank(credibility)
        # We update the top-k subgroups
        self._top_k_update(pattern,credibility_values,rank)
    
    def _compute_rank(self,credibility: list) -> int:
        """Method to compute the rank of a pattern.

        :param credibility: the list of booleans representing the pattern's credibility.
        :return: the rank of the pattern.
        """
        rank = 0
        # We iterate over the credibility list to find the first False value.
        # The rank is the number of True values before the first False value (or the end of the list if there is no False value).
        for i in range(len(credibility)):
            if not credibility[i]:
                return rank
            rank = i+1
        return rank
    
    def _redundant(self,p1: Pattern, p2: Pattern) -> bool:
        """Check if two patterns are redundant.

        :param p1: the first pattern.
        :param p2: the second pattern.
        :return: True if the patterns are redundant, False otherwise.
        """
        # Since we are only using nominal attributes, we only need to check if one pattern is a refinement of the other. We consider a pattern to be a refinement of itself.
        return p1.is_refinement(p2,True) or p2.is_refinement(p1,True)
    
    def _top_k_update(self, new_pattern: Pattern, credibility_values: dict, rank: int) -> None:
        """ Method to select the top-k subgroups for each complexity.
        :param: new_pattern: the new pattern to potentially add to the top-k subgroups.
        :param: credibility_values: the credibility values of the new pattern.
        :param: rank: the rank of the new pattern according to its credibility.
        """
        # If the list is full and the candidate is worse than the worst subgroup in the top-k subgroups, we do not add it.
        if len(self._top_k_subgroups) == self._num_subgroups:
            worse_rank = self._top_k_subgroups[-1][1]
            worse_or = self._top_k_subgroups[-1][2]
            if rank < worse_rank or (rank == worse_rank and credibility_values["odds_ratio"] < worse_or):
                return
        # Have we replaced a top_k subgroup?
        removed = False
        # Is the subgroup redundant with respect to the top-k subgroups?
        redundant = False
        # List of subgroups to remove from the top-k subgroups.
        subgroupsToRemove = []
        # We iterate over the list of top-k subgroups to look for redundancies.
        for s in self._top_k_subgroups:
            if self._redundant(s[0],new_pattern):
                # If the new pattern is redundant with a top-k subgroup, we check if it has a better rank.
                if rank > s[1] or (rank == s[1] and credibility_values["odds_ratio"] > s[2]):
                    # If the new pattern has a better rank, we replace the redundant subgroup with the current one.
                    subgroupsToRemove.append(s)
                    removed = True # Since we have replaced a subgroup, we will add the new pattern no matter other redundancies.
                else:
                    # There is a redundancy with a worse top-k subgroup, we won't add the new pattern if the new pattern
                    # does not improve the rank of some other top-k subgroup.
                    redundant = True
        # We remove the redundant subgroups from the top-k subgroups.
        for s in subgroupsToRemove:
            self._top_k_subgroups.remove(s)

        # If we have replaced a subgroup or the new pattern is not redundant, we add the new pattern to the top-k subgroups.
        if removed or not redundant:
            self._top_k_subgroups.append((new_pattern,rank,credibility_values["odds_ratio"], credibility_values))
            # Sort the top_k_subgroups by rank in descending order by their rank and odds-ratio
            self._top_k_subgroups.sort(key=lambda x: (x[1], x[2]), reverse=True)
            # If the list is full, we remove the subgroup with the worst rank.
            if len(self._top_k_subgroups) > self._num_subgroups:
                self._top_k_subgroups.pop()
    
    def _grow_tree(self,df : DataFrame,tuple_target_attribute_value: tuple,selectors: list[Selector],complexity: int, pattern:Pattern, pattern_appearance: Series) -> None:
        """ Recurssive method to grow the tree of patterns.
        :param df: the dataset.
        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        :param selectors: the list of candidate selectors for the current iteration.
        :param complexity: the maximum complexity of the patterns that we want to generate.
        :param top_k_subgroups: the list of best subgroups for the current complexity.
        :param pattern: the current pattern (node of the tree).
        :param pattern_appearance: the appearance of the current pattern.
        """
        
        # We count the number of unique visited subgroups only if the current complexity is the maximum complexity so we don't count the same subgroup twice.
        if len(pattern) == complexity:
            self._visited_subgroups += 1
        # We count the number of non-unique visited subgroups.
        self._non_unique_visited_subgroups += 1
        # We compute the coverage of the pattern to apply pruning.
        n = pattern_appearance.sum()
        # Since coverage = (tp+fp)/(TP+FP) we can avoid computing tp and fp and use the number of rows that satisfy the pattern (n).
        coverage = self._coverage_measure.compute({"tp": n, "fp" : 0, "TP": self._TP, "FP": self._FP})
        # If the pattern does not appear in the database (coverage = 0), we prune this branch.
        if coverage == 0:
            # Update the counter of pruned subgroups only in the last iteration to avoid counting the same pruned subgroup multiple times.
            if complexity == self._max_complexity:
                self._pruned_subgroups += 1
            return
        # We check if the pattern meets the minimum coverage threshold.
        meets_coverage_threshold = coverage >= self._thresholds["coverage"]
        # Since the coverage is antimonotonic, we can prune the branch if the rank of this pattern is 0, the rank of the
        # worse subgroup in the top_k_subgroups is higher than 0, and the list is full.
        if len(self._top_k_subgroups) == self._num_subgroups and \
            self._top_k_subgroups[-1][1] > 0 and \
            not meets_coverage_threshold:
            # Update the counter of pruned subgroups only in the last iteration to avoid counting the same pruned subgroup multiple times.
            if complexity == self._max_complexity:
                self._pruned_subgroups += 1
            return
        if len(pattern) == complexity:
            # If the pattern has the maximum complexity, we compute the credibility measures and update the top-k subgroups.
            self._handle_individual_result(df[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1], pattern, pattern_appearance)
            # In this case, we do not continue growing the tree.
            return
        # If we have not pruned the branch and we have not reached the maximum depth, we continue growing the tree.
        for i in range(len(selectors)):
            # Pattern with the new selector.
            new_pattern = pattern.copy()
            new_pattern.add_selector(selectors[i])
            # The new pattern appearance is the intersection of the appearance of the current pattern and the appearance of the new selector.
            new_pattern_appearance = pattern_appearance & self._selector_appearances[selectors[i]]
            # We do not use the full list of patterns in each call to avoid repeating the same patterns.
            self._grow_tree(df, tuple_target_attribute_value, selectors[i+1:], complexity, new_pattern, new_pattern_appearance)

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
        if tuple_target_attribute_value[0] not in pandas_dataframe.columns:
            raise ValueError("The target attribute must be in the dataset.")
        if tuple_target_attribute_value[1] not in pandas_dataframe[tuple_target_attribute_value[0]].unique():
            raise ValueError("The target value must be in the target attribute.")
        # We compute TP, FP and N for this dataset and target
        self._TP = (pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]).sum()
        self._FP = len(pandas_dataframe) - self._TP
        self._N = len(pandas_dataframe)
        # We copy the DataFrame to avoid modifying the original when dealing with "other" values.
        df = pandas_dataframe.copy()
        # We reduce the number of categories per column according to 'cats' and generate the list of selectors.
        self._reduce_categories(df, tuple_target_attribute_value)
        # We initialize the entry template for performance reasons.
        self._entry_template = Series(True, index = df.index)
        selectors = self._generate_selectors(df, tuple_target_attribute_value)
        # List of global best subgroups (Pattern, rank, effect_size, credibility_values)
        self._top_k_subgroups = []
        # We iterate over the possible complexities to select the best subgroups.
        max_complexity = self._max_complexity
        # If we have not set the maximum complexity, we take the number of attributes (we do not count the target attribute)
        if max_complexity == -1:
            max_complexity = len(df.columns) - 1
        # Iterate over the maximum size of the patterns to perform the iterative deepening search.
        for complexity in range(1,max_complexity+1):
            self._grow_tree(df, tuple_target_attribute_value, selectors, complexity, Pattern([]), self._entry_template)
        if self._file_path is not None:
            self._to_file(tuple_target_attribute_value)


    def _to_file(self,tuple_target_attribute_value: tuple) -> None:
        """ Method to write the results to a file.

        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        """
        file = open(self._file_path,"w")
        for pat, rank, _, cred_values in self._top_k_subgroups:
            sb = Subgroup(pat, Selector(tuple_target_attribute_value[0],Operator.EQUAL,tuple_target_attribute_value[1]))
            file.write(str(sb) + " ; ")
            file.write("Rank : " + str(rank) + " ; ")
            for cred in cred_values:
                file.write(cred + " : " + str(cred_values[cred]) + " ; ")
            file.write("\n")
        file.close()
