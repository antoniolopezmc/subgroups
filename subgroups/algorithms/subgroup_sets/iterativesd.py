# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the Iterative Subgroup Discovery algorithm.
"""

from typing import Union
from pandas import DataFrame, Series
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
import operator
import statsmodels.api as sm
import numpy as np

class IterativeSD(Algorithm):
    """
    """

    _credibility_criterions = {
        "coverage" :  operator.ge,
        "odds_ratio" : operator.ge,
        "p_value" : operator.le,
        "absolute_contribution" : operator.ge,
        "contribution_ratio" : operator.le,
    }

    __slots__ = ['_num_subgroups', '_cats', '_max_complexity', '_delta', '_file', '_top_k_subgroups', '_visited_subgroups', '_selectors', '_thresholds']

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
        self._visited_subgroups = 0
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


    def _get_selected_subgroups(self) -> int:
        return len(self._top_k_subgroups)

    def _get_unselected_subgroups(self) -> int:
        return self._visited_subgroups - len(self._top_k_subgroups)

    def _get_visited_subgroups(self) -> int:
        return self._visited_subgroups

    def _get_top_patterns(self) -> list[Pattern]:
        return self._top_k_subgroups.copy()
    
    selected_subgroups = property(_get_selected_subgroups, None, None, "The number of selected subgroups.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "The number of unselected subgroups.")
    visited_subgroups = property(_get_visited_subgroups, None, None, "The number of visited subgroups.")
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
            if column != tuple_target_attribute_value[0]:
                for value in df[column].unique():
                    selectors.append(Selector(column,Operator.EQUAL,value))
        return selectors
    
    def _handle_individual_result(self, df: DataFrame, target_column: Series, pattern: Pattern) -> dict:
        """ Method to compute the credibility measures of a pattern
        
        :param df: the dataset.
        :param target_column: the target column of the dataset represented as a pandas Series of booleans (True if equal to the target value, False otherwise).
        :param pattern: the pattern to be evaluated.
        :return: a dictionary with the credibility measures of the pattern {measure_name: measure_value}.
        """

        # We obtain the rows that satisfy the pattern.
        appearance = Series(True, index = df.index)
        for selector in pattern:
                appearance = appearance & (df[selector.attribute_name] == selector.value)
        # Most credibility measures are computed using a logistic regression model.
        linear_model = sm.GLM(target_column, appearance, family=sm.families.Binomial()).fit()
        odds_ratio = np.exp(linear_model.params.iloc[0])
        p_value = linear_model.pvalues.iloc[0]
        coverage = appearance.sum() / len(appearance)
        # If the pattern only has one selector, the absolute contribution and the contribution ratio are 1.
        if len(pattern) == 1:
                minimum_absolute_contribution = 1
                maximum_absolute_contribution = 1
        else:
            # We compute the contribution of each selector as the odds ratio of
            # the pattern without the selector divided by the odds ratio of the pattern.
            minimum_absolute_contribution = 1
            maximum_absolute_contribution = 0
            for selector in pattern:
                pattern_without_selector = pattern.copy()
                pattern_without_selector.remove_selector(selector)
                appearance_without_selector = Series(True, index = df.index)
                for s in pattern_without_selector:
                    appearance_without_selector = appearance_without_selector & (df[s.attribute_name] == s.value)
                linear_model = sm.GLM(target_column, appearance_without_selector, family=sm.families.Binomial()).fit()
                pattern_wo_selector_odds_ratio = np.exp(linear_model.params.iloc[0])
                contribution = odds_ratio / pattern_wo_selector_odds_ratio
                minimum_absolute_contribution = min(minimum_absolute_contribution, contribution)
                maximum_absolute_contribution = max(maximum_absolute_contribution, contribution)
        # The absolute contribution is the minimum contribution of the selectors.
        absolute_contribution = minimum_absolute_contribution
        # The contribution ratio is the maximum contribution divided by the minimum contribution.
        if absolute_contribution == 0:
            contribution_ratio = np.inf
        else:
            contribution_ratio = maximum_absolute_contribution / minimum_absolute_contribution
        # The credibility measures are returned as a dictionary {measure_name: measure_value}.
        credibility = {
            "coverage": coverage,
            "odds_ratio": odds_ratio,
            "p_value": p_value,
            "absolute_contribution": absolute_contribution,
            "contribution_ratio": contribution_ratio,
        }
        return credibility
    
    def _compute_rank(self,credibility: list) -> int:
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
    
    def _redundant(self,p1: Pattern, p2: Pattern) -> bool:
        """Check if two patterns are redundant.

        :param p1: the first pattern.
        :param p2: the second pattern.
        :return: True if the patterns are redundant, False otherwise.
        """
        # Since we are only using nominal attributes, we only need to check if one pattern is a refinement of the other. We consider a pattern to be a refinement of itself.
        return p1.is_refinement(p2,True) or p2.is_refinement(p1,True)

    
    def top_k_selection(self):
        """ Method to select the top-k subgroups for each complexity.
        """
        for complexity in range(1,self._max_complexity+1):
            for g in self._top_k_subgroups_per_depth[complexity]:
                # Have we replaced a subgroup?
                removed = False
                # Is the subgroup redundant with respect to the top-k subgroups of the previous complexities?
                redundant = False
                for s in self._top_k_subgroups:
                    if self._redundant(s[0],g[0]):
                        if g[1] < s[1] or (g[1] == s[1] and g[2] > s[2]):
                            # We replace the redundant subgroup with the current one.
                            self._top_k_subgroups.remove(s)
                            removed = True
                        else:
                            redundant = True
                
                if removed or not redundant:
                    self._top_k_subgroups.append(g)
                    if len(self._top_k_subgroups) > self._num_subgroups:
                        # Sort the top_k_subgroups by rank in descending order and remove the last element.
                        self._top_k_subgroups.sort(key=lambda x: (x[1], x[2]), reverse=True)
                        self._top_k_subgroups.pop()

    
    def _grow_tree(self,df : DataFrame,tuple_target_attribute_value: tuple,selectors: list[Selector],complexity: int, pattern:Pattern) -> None:
        """ 
        :param df: the dataset.
        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        :param selectors: the list of candidate selectors for the current iteration.
        :param complexity: the maximum complexity of the patterns that we want to generate.
        :param top_k_subgroups: the list of best subgroups for the current complexity.
        :param pattern: the current pattern (node of the tree).
        """

        self._visited_subgroups += 1
        credibility_values = self._handle_individual_result(df, df[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1], pattern)
        # The credibility of a patterns is represented as a list of booleans,
        # where each element is True if the credibility measure meets the threshold and False otherwise.
        credibility = []
        for cred in IterativeSD._credibility_criterions:
            # The credibility_criterions dictionary contains the function to compare the credibility measure with the threshold.
            credibility.append(IterativeSD._credibility_criterions[cred](credibility_values[cred],self._thresholds[cred]))
        # We compute the numerical rank of the pattern given its credibility.
        rank = self._compute_rank(credibility)
        # If the pattern does not appear in the database (coverage = 0), we prune this branch.
        if credibility_values["coverage"] == 0:
            return
        # Since the coverage is antimonotonic, we can prune the branch if the rank of this pattern is 0, the rank of the
        # worse subgroup in the top_k_subgroups for this complexity is higher than 0, and this list is full.
        if len(self._top_k_subgroups_per_depth[complexity]) == self._num_subgroups and \
            self._top_k_subgroups_per_depth[complexity][-1][1] > 0 and \
            rank == 0:
            return
        if len(pattern) == complexity:
            if len(self._top_k_subgroups_per_depth[complexity]) < self._num_subgroups:
                self._top_k_subgroups_per_depth[complexity].append((pattern,rank,credibility_values["odds_ratio"], credibility_values))
                # Sort the top_k_subgroups by rank in descending order
                self._top_k_subgroups_per_depth[complexity].sort(key=lambda x: (x[1], x[2]), reverse=True)
            # If the list is full but the current pattern has a better rank than the worst subgroup in the list, we replace the worst subgroup with the current pattern.
            elif rank < self._top_k_subgroups_per_depth[complexity][-1][1] or \
                (rank == self._top_k_subgroups_per_depth[complexity][-1][1] and credibility_values["odds_ratio"] > self._top_k_subgroups_per_depth[complexity][-1][2]):
                self._top_k_subgroups_per_depth[complexity][-1] = (pattern,rank,credibility_values["odds_ratio"], credibility_values)
                # Sort the top_k_subgroups by rank in descending order
                self._top_k_subgroups_per_depth[complexity].sort(key=lambda x: (x[1], x[2]), reverse=True)
            return
        # If we have not pruned the branch, we continue growing the tree.
        # We do not use the full list of patterns in each call to avoid repeating the same patterns.
        for i in range(len(selectors)):
            new_pattern = pattern.copy()
            new_pattern.add_selector(selectors[i])
            self._grow_tree(df, tuple_target_attribute_value, selectors[i+1:], complexity, new_pattern)



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
        # We copy the DataFrame to avoid modifying the original when dealing with "other" values.
        df = pandas_dataframe.copy()
        # We reduce the number of categories per column according to 'cats' and generate the list of selectors.
        self._reduce_categories(df, tuple_target_attribute_value)
        selectors = self._generate_selectors(df, tuple_target_attribute_value)
        # List of global best subgroups (Pattern, rank, effect_size, credibility_values)
        self._top_k_subgroups = []
        # List of best subgroups for each complexity {complexity: [(Pattern, rank, effect_size, credibility_values)]}
        self._top_k_subgroups_per_depth = {}
        # Select the top-k subgroups for each complexity growing the tree until a certain depth.
        for complexity in range(1,self._max_complexity+1):
            self._top_k_subgroups_per_depth[complexity] = []
            self._grow_tree(df, tuple_target_attribute_value, selectors, complexity, Pattern([]))
        # Once we have the best subgroups for each complexity, we select the top-k subgroups.
        self.top_k_selection()
        if self._file_path is not None:
            self._to_file(tuple_target_attribute_value)


    def _to_file(self,tuple_target_attribute_value: tuple) -> None:
        """ Method to write the results to a file.

        :param tuple_target_attribute_value: the tuple which contains the target attribute name and the target attribute values.
        """
        file = open(self._file_path,"w")
        for pat, _, _, cred_values in self._top_k_subgroups:
            sb = Subgroup(pat, Selector(tuple_target_attribute_value[0],Operator.EQUAL,tuple_target_attribute_value[1]))
            file.write(str(sb) + " ; ")
            for cred in cred_values:
                file.write(cred + " : " + str(cred_values[cred]) + " ; ")
            file.write("\n")
        file.close()




