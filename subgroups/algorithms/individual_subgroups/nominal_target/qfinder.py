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

def _generate_set_of_candidate_patterns(df : DataFrame, tuple_target_attribute_value: tuple, max_complexity : int ,cats : int = -1) -> list[Pattern]:
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
            top_values = value_counts.nlargest(cats-1).index
            for value in top_values:
                simple_patterns.append(Pattern([Selector(column, Operator.EQUAL, value)]))
            simple_patterns.append(Pattern([Selector(column, Operator.EQUAL, "other")]))
    
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
    """

    __slots__ = ['_cats', '_max_complexity', '_coverage_thld', '_or_thld', '_p_val_thld', '_abs_contribution_thld', '_contribution_thld', "_file", "_file_path"]

    def __init__(self, cats : int = -1, max_complexity: int = -1, coverage_thld: float = 0.1, or_thld: float = 1.2, p_val_thld: float = 0.05, abs_contribution_thld: float = 0.2, contribution_thld: float = 5, write_results_in_file: bool = False, file_path: Union[str,None] = None) -> None:
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
        if (write_results_in_file):
                self._file_path = file_path
        else:
            self._file_path = None
        self._file = None

    