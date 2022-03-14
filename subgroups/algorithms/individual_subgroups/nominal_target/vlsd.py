# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the VLSD algorithm.
"""

from pandas import DataFrame
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import DatasetAttributeTypeError
from subgroups.data_structures.vertical_list import VerticalList
from subgroups.data_structures.vertical_list_with_bitsets import VerticalListWithBitsets
from subgroups.data_structures.vertical_list_with_sets import VerticalListWithSets
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup

# Python annotations.
from typing import Union, ClassVar

def _delete_subgroup_parameters_from_a_dictionary(dict_of_parameters : dict[str, Union[int, float]]):
    """Private method to delete the subgroup parameters (i.e., tp, fp, TP and FP) from a dictionary of parameters.
    
    :param dict_of_parameters: the dictionary of parameters which is modified.
    """
    try:
        del dict_of_parameters[QualityMeasure.TRUE_POSITIVES]
    except KeyError:
        pass
    try:
        del dict_of_parameters[QualityMeasure.FALSE_POSITIVES]
    except KeyError:
        pass
    try:
        del dict_of_parameters[QualityMeasure.TRUE_POPULATION]
    except KeyError:
        pass
    try:
        del dict_of_parameters[QualityMeasure.FALSE_POPULATION]
    except KeyError:
        pass

def _query_triangular_matrix(matrix : dict[Selector, dict[Selector, VerticalList]], index_a : Selector, index_b : Selector) -> Union[VerticalList, None]:
    """Private method to query a triangular matrix.
    
    :param matrix: the triangular matrix which is queried.
    :param index_a: the first index in the query.
    :param index_b: the second index in the query.
    :return: either the Vertical List contained in matrix[index_a][index_b], or the Vertical List contained in matrix[index_b][index_a] if the firt one was None, or None if they were both None.
    """
    try:
        return matrix[index_a][index_b]
    except KeyError:
        try:
            return matrix[index_b][index_a]
        except KeyError:
            return None

class VLSD(Algorithm):
    """This class represents the VLSD algorithm.
    
    :param quality_measure: the quality measure which is used.
    :param q_minimum_threshold: the minimum quality threshold for the quality measure.
    :param optimistic_estimate: the optimistic estimate of the quality measure which is used.
    :param oe_minimum_threshold: the minimum quality threshold for the optimistic estimate.
    :param additional_parameters_for_the_quality_measure: if the quality measure passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param additional_parameters_for_the_optimistic_estimate: if the optimistic estimate passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param sort_criterion_in_s1: the criterion to use in order to sort the Vertical Lists with only one selector. Three values are possible: "quality-ascending" (sort ascending by quality value), "quality-descending" (sort descending by quality value), and "no-order" (do not sort and maintain the generation order). By default, "no-order".
    :param sort_criterion_in_other_sizes: the criterion to use in order to sort the Vertical Lists with more than one selector. Three values are possible: "quality-ascending" (sort ascending by quality value), "quality-descending" (sort descending by quality value), and "no-order" (do not sort and maintain the generation order). By default, "no-order".
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """
    
    SORT_CRITERION_QUALITY_ASCENDING : ClassVar[str] = "quality-ascending"
    SORT_CRITERION_QUALITY_DESCENDING : ClassVar[str] = "quality-descending"
    SORT_CRITERION_NO_ORDER : ClassVar[str] = "no-order"
    SORT_CRITERION : ClassVar[list[str]] = [SORT_CRITERION_QUALITY_ASCENDING, SORT_CRITERION_QUALITY_DESCENDING, SORT_CRITERION_NO_ORDER]
    
    VERTICAL_LISTS_WITH_BITSETS : ClassVar[str] = "bitsets"
    VERTICAL_LISTS_WITH_SETS : ClassVar[str] = "sets"
    VERTICAL_LISTS_IMPLEMENTATION : ClassVar[list[str]] = [VERTICAL_LISTS_WITH_BITSETS, VERTICAL_LISTS_WITH_SETS]

    __slots__ = ("_quality_measure", "_q_minimum_threshold", "_optimistic_estimate", "_oe_minimum_threshold", "_additional_parameters_for_the_quality_measure", "_additional_parameters_for_the_optimistic_estimate", "_selected_subgroups", "_not_selected_subgroups", "_sort_criterion_in_s1", "_sort_criterion_in_other_sizes", "_vertical_lists_implementation", "_file_path", "_file")
    
    def __init__(self, quality_measure : QualityMeasure, q_minimum_threshold : Union[int, float], optimistic_estimate : QualityMeasure, oe_minimum_threshold : Union[int, float], additional_parameters_for_the_quality_measure : dict[str, Union[int, float]] = dict(), additional_parameters_for_the_optimistic_estimate : dict[str, Union[int, float]] = dict(), sort_criterion_in_s1 : str = SORT_CRITERION_NO_ORDER, sort_criterion_in_other_sizes : str = SORT_CRITERION_NO_ORDER, vertical_lists_implementation : str = VERTICAL_LISTS_WITH_BITSETS, write_results_in_file : bool = False, file_path : Union[str, None] = None) -> None:
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be an instance of a subclass of the 'QualityMeasure' class.")
        if (type(q_minimum_threshold) is not int) and (type(q_minimum_threshold) is not float):
            raise TypeError("The type of the parameter 'q_minimum_threshold' must be 'int' or 'float'.")
        if not isinstance(optimistic_estimate, QualityMeasure):
            raise TypeError("The parameter 'optimistic_estimate' must be an instance of a subclass of the 'QualityMeasure' class.")
        # We check whether 'optimistic_estimate' is an optimistic estimate of 'quality_measure'.
        if quality_measure.get_name() not in optimistic_estimate.optimistic_estimate_of():
            raise ValueError("The quality measure " + optimistic_estimate.get_name() + " is not an optimistic estimate of the quality measure " + quality_measure.get_name() + ".")
        if (type(oe_minimum_threshold) is not int) and (type(oe_minimum_threshold) is not float):
            raise TypeError("The type of the parameter 'oe_minimum_threshold' must be 'int' or 'float'.")
        if (type(additional_parameters_for_the_quality_measure) is not dict):
            raise TypeError("The type of the parameter 'additional_parameters_for_the_quality_measure' must be 'dict'")
        if (type(additional_parameters_for_the_optimistic_estimate) is not dict):
            raise TypeError("The type of the parameter 'additional_parameters_for_the_optimistic_estimate' must be 'dict'")
        if (sort_criterion_in_s1 not in VLSD.SORT_CRITERION):
            raise ValueError("The value of the parameter 'sort_criterion_in_s1' is not valid. See the documentation.")
        if (sort_criterion_in_other_sizes not in VLSD.SORT_CRITERION):
            raise ValueError("The value of the parameter 'sort_criterion_in_other_sizes' is not valid. See the documentation.")
        if (vertical_lists_implementation not in VLSD.VERTICAL_LISTS_IMPLEMENTATION):
            raise ValueError("The value of the parameter 'vertical_lists_implementation' is not valid. See the documentation.")
        if (type(write_results_in_file) is not bool):
            raise TypeError("The type of the parameter 'write_results_in_file' must be 'bool'")
        if ((type(file_path) is not str) and (file_path is not None)):
            raise TypeError("The type of the parameter 'file_path' must be 'str' or 'NoneType'.")
        # If 'write_results_in_file' is True, 'file_path' must not be None.
        if (write_results_in_file) and (file_path is None):
            raise ValueError("If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        self._quality_measure = quality_measure
        self._q_minimum_threshold = q_minimum_threshold
        self._optimistic_estimate = optimistic_estimate
        self._oe_minimum_threshold = oe_minimum_threshold
        self._additional_parameters_for_the_quality_measure = additional_parameters_for_the_quality_measure.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_quality_measure)
        self._additional_parameters_for_the_optimistic_estimate = additional_parameters_for_the_optimistic_estimate.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_optimistic_estimate)
        self._selected_subgroups = 0
        self._not_selected_subgroups = 0
        self._sort_criterion_in_s1 = sort_criterion_in_s1
        self._sort_criterion_in_other_sizes = sort_criterion_in_other_sizes
        self._vertical_lists_implementation = vertical_lists_implementation
        if (write_results_in_file):
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None
    
    def _get_quality_measure(self) -> QualityMeasure:
        return self._quality_measure
    
    def _get_q_minimum_threshold(self) -> Union[int, float]:
        return self._q_minimum_threshold
    
    def _get_optimistic_estimate(self) -> QualityMeasure:
        return self._optimistic_estimate
    
    def _get_oe_minimum_threshold(self) -> Union[int, float]:
        return self._oe_minimum_threshold
    
    def _get_additional_parameters_for_the_quality_measure(self) -> dict[str, Union[int, float]]:
        return self._additional_parameters_for_the_quality_measure
    
    def _get_additional_parameters_for_the_optimistic_estimate(self) -> dict[str, Union[int, float]]:
        return self._additional_parameters_for_the_optimistic_estimate
    
    quality_measure = property(_get_quality_measure, None, None, "The quality measure which is used.")
    q_minimum_threshold = property(_get_q_minimum_threshold, None, None, "The minimum quality threshold for the quality measure.")
    optimistic_estimate = property(_get_optimistic_estimate, None, None, "The optimistic estimate of the quality measure which is used.")
    oe_minimum_threshold = property(_get_oe_minimum_threshold, None, None, "The minimum quality threshold for the optimistic estimate.")
    additional_parameters_for_the_quality_measure = property(_get_additional_parameters_for_the_quality_measure, None, None, "The additional needed parameters with which to compute the quality measure.")
    additional_parameters_for_the_optimistic_estimate = property(_get_additional_parameters_for_the_optimistic_estimate, None, None, "The additional needed parameters with which to compute the optimistic estimate.")
    
    def _get_selected_subgroups(self) -> int:
        return self._selected_subgroups
    
    def _get_not_selected_subgroups(self) -> int:
        return self._not_selected_subgroups
    
    def _get_visited_nodes(self) -> int:
        return self._selected_subgroups + self._not_selected_subgroups

    selected_subgroups = property(_get_selected_subgroups, None, None, "Number of selected subgroups after executing the VLSD algorithm (before executing the 'fit' method, this attribute is 0).")
    not_selected_subgroups = property(_get_not_selected_subgroups, None, None, "Number of not selected subgroups after executing the VLSD algorithm (before executing the 'fit' method, this attribute is 0).")
    visited_nodes = property(_get_visited_nodes, None, None, "Number of visited nodes after executing the VLSD algorithm (before executing the 'fit' method, this attribute is 0).")

    def _get_sort_criterion_in_s1(self) -> str:
        return self._sort_criterion_in_s1
    
    def _get_sort_criterion_in_other_sizes(self) -> str:
        return self._sort_criterion_in_other_sizes
    
    sort_criterion_in_s1 = property(_get_sort_criterion_in_s1, None, None, "The criterion to use in order to sort the Vertical Lists with only one selector.")
    sort_criterion_in_other_sizes = property(_get_sort_criterion_in_other_sizes, None, None, "The criterion to use in order to sort the Vertical Lists with more than one selector.")
    
    def _handle_individual_result(self, individual_result : tuple[VerticalList, tuple[str, str], int, int]) -> None:
        """Private method to handle each individual result generated by the VLSD algorithm.
        
        :param individual_result: the individual result which is handled. In this case, it is a Vertical List, a target as a tuple and the subgroup parameters TP and FP.
        """
        # Get the subgroup parameters.
        tp = individual_result[0].tp
        fp = individual_result[0].fp
        TP = individual_result[2]
        FP = individual_result[3]
        # Compute the quality measure of the frequent pattern along with the target (i.e., the quality measure of the subgroup).
        dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : tp, QualityMeasure.FALSE_POSITIVES : fp, QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP}
        dict_of_parameters.update(self._additional_parameters_for_the_quality_measure)
        quality_measure_value = self._quality_measure.compute(dict_of_parameters)
        # Add the subgroup only if the quality measure value is greater or equal than the threshold.
        if quality_measure_value >= self._q_minimum_threshold:
            # If applicable, write in the file defined in the __init__ method.
            if self._file_path is not None:
                # Get the description and the target.
                subgroup_description = Pattern(individual_result[0].list_of_selectors)
                target_as_tuple = individual_result[1] # Attribute name -> target_as_tuple[0], Attribute value -> target_as_tuple[1]
                # Create the subgroup.
                subgroup = Subgroup(subgroup_description, Selector(target_as_tuple[0], Operator.EQUAL, target_as_tuple[1]))
                # Write.
                self._file.write(str(subgroup) + " ; ")
                self._file.write("Sequence of instances tp = " + str(individual_result[0].sequence_of_instances_tp) + " ; ")
                self._file.write("Sequence of instances fp = " + str(individual_result[0].sequence_of_instances_fp) + " ; ")
                self._file.write("Quality Measure " + self._quality_measure.get_name() + " = " + str(quality_measure_value) + " ; ")
                self._file.write("Optimistic Estimate " + self._optimistic_estimate.get_name() + " = " + str(individual_result[0].quality_value) + " ; ")
                self._file.write("tp = " + str(tp) + " ; ")
                self._file.write("fp = " + str(fp) + " ; ")
                self._file.write("TP = " + str(TP) + " ; ")
                self._file.write("FP = " + str(FP) + "\n")
            # Increment the number of selected subgroups.
            self._selected_subgroups = self._selected_subgroups + 1
        else: # If the quality measure is not greater or equal, increment the number of not selected subgroups.
            self._not_selected_subgroups = self._not_selected_subgroups + 1
    
    # IMPORTANT: although the subgroup parameters TP and FP can be computed from 'pandas_dataframe', we also pass them by parameter in this method to avoid computing them twice (in the 'fit' method and in this method).
    def _generate_subgroups_s1(self, pandas_dataframe : DataFrame, target : tuple[str, str], TP : int, FP : int) -> list[VerticalList]:
        """Private method to generate the list of Vertical Lists of size 1 (i.e., whose list of selectors has only one selector), prune it and sort it.
        
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str') without missing values.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :param TP: the true population of the dataset. IMPORTANT: although it can be computed from 'pandas_dataframe', we pass it by parameter to avoid computing it twice (in the 'fit' method and in this method).
        :param FP: the false population of the dataset. IMPORTANT: although it can be computed from 'pandas_dataframe', we pass it by parameter to avoid computing it twice (in the 'fit' method and in this method).
        :return: a list in which each element is a Vertical List of size 1 (i.e., it only has one selector in its list of selectors). The list is pruned according to the threshold and sorted according to 'sort_criterion_in_s1' attribute.
        """
        # Get the target column as a mask: True if the value is equal to the target value and False otherwise.
        target_attribute_as_a_mask = (pandas_dataframe[target[0]] == target[1])
        # Result.
        result = []
        # Iterate through the columns (except the target).
        for column in pandas_dataframe.columns.drop(target[0]):
            # Use the 'groupby' method in order to group each value depending on whether appears with the target or not.
            # - In this case, the property 'indices' is a dictionary in which the key is the tuple "(value, value)" and the
            #   value is a sequence of register indices in which that combination appears.
            values_and_target_grouped = pandas_dataframe.groupby([column, target_attribute_as_a_mask]).indices
            # Set of values which have been already processed.
            processed_values = set()
            # Iterate through the tuples returned by the groupby method.
            for value_target_tuple in values_and_target_grouped:
                value = value_target_tuple[0]
                # Process the tuple only if the value was not seen before.
                if value not in processed_values:
                    # Registers which have the target.
                    try:
                        registers_tp = values_and_target_grouped[(value,True)]
                    except KeyError:
                        registers_tp = [] # Empty sequence.
                    # Registers which do not have the target.
                    try:
                        registers_fp = values_and_target_grouped[(value,False)]
                    except KeyError:
                        registers_fp = [] # Empty sequence.
                    # Compute the optimistic estimate.
                    dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : len(registers_tp), QualityMeasure.FALSE_POSITIVES : len(registers_fp), QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP}
                    dict_of_parameters.update(self._additional_parameters_for_the_optimistic_estimate)
                    optimistic_estimate_value = self._optimistic_estimate.compute(dict_of_parameters)
                    # Pruning: add the Vertical List only if the optimistic estimate value is greater or equal than the threshold.
                    if optimistic_estimate_value >= self._oe_minimum_threshold:
                        # Create the Vertical List (depending on the specified implementation).
                        vl = None
                        if (self._vertical_lists_implementation == VLSD.VERTICAL_LISTS_WITH_BITSETS):
                            vl = VerticalListWithBitsets([Selector(column, Operator.EQUAL, value)], registers_tp, registers_fp, TP+FP, optimistic_estimate_value)
                        elif (self._vertical_lists_implementation == VLSD.VERTICAL_LISTS_WITH_SETS):
                            vl = VerticalListWithSets([Selector(column, Operator.EQUAL, value)], registers_tp, registers_fp, TP+FP, optimistic_estimate_value)
                        # Add it to the final list.
                        result.append(vl)
                    # Finally, add the value to 'processed_values'.
                    processed_values.add(value)
        # Sort by quality value (optimistic_estimate_value) according to 'sort_criterion_in_s1'.
        if (self._sort_criterion_in_s1 == VLSD.SORT_CRITERION_QUALITY_ASCENDING):
            result.sort(reverse=False, key=lambda x : x.quality_value)
        elif (self._sort_criterion_in_s1 == VLSD.SORT_CRITERION_QUALITY_DESCENDING):
            result.sort(reverse=True, key=lambda x : x.quality_value)
        # Return the list.
        return result
    
    def _search(self, P : list[VerticalList], M : dict[Selector, dict[Selector, VerticalList]], target : tuple[str, str], TP : int, FP : int) -> None:
        """Private search method.
        
        :param P: a list of Vertical Lists.
        :param M: the 2-dimensional matrix M (in this case, it is a python dictionary).
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :param TP: the true population of the dataset (i.e., the number of instances in which the target appears).
        :param FP: the false population of the dataset (i.e., the number of instances in which the target does not appear).
        """
        index_x = 0
        # Main loop: while P list is not completely processed (the last element is never processed).
        while (index_x < (len(P)-1)):
            s_x = P[index_x]
            # Simulate the "pop_first" method.
            # --> IMPORTANT: we set None instead of directly delete the first element, because deleting an element that is not the last
            #     in a python list is O(n), because all the elements at the right of the deleted element are moved one position to the left.
            P[index_x] = None
            index_x = index_x + 1
            # Get the last selector of s_x.
            s_x_last_selector = s_x.list_of_selectors[-1]
            # List in which the children will be stored.
            V = []
            # Join between s_x and each node to its right.
            for index_y in range(index_x, len(P)): # In this case, it is not index_x+1 because the index was already increased.
                s_y = P[index_y]
                # Get the last selector of s_y.
                s_y_last_selector = s_y.list_of_selectors[-1]
                # Query M.
                vertical_list_in_M = _query_triangular_matrix(M, s_x_last_selector, s_y_last_selector)
                if (vertical_list_in_M is not None) and (vertical_list_in_M.quality_value >= self.oe_minimum_threshold):
                    s_xy_dict_of_parameters = {QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP}
                    s_xy_dict_of_parameters.update(self._additional_parameters_for_the_optimistic_estimate)
                    s_xy = s_x.join(s_y, self._optimistic_estimate, s_xy_dict_of_parameters, return_None_if_n_is_0 = True)
                    if (s_xy is not None) and (s_xy.quality_value >= self.oe_minimum_threshold):
                        # Add s_xy to V list.
                        V.append(s_xy)
                        # Handle this result.
                        self._handle_individual_result( (s_xy, target, TP, FP) )
            # Check whether V is not empty.
            if V:
                # Sort by quality value (optimistic_estimate_value) according to 'sort_criterion_in_other_sizes'.
                if (self._sort_criterion_in_other_sizes == VLSD.SORT_CRITERION_QUALITY_ASCENDING):
                    V.sort(reverse=False, key=lambda x : x.quality_value)
                elif (self._sort_criterion_in_other_sizes == VLSD.SORT_CRITERION_QUALITY_DESCENDING):
                    V.sort(reverse=True, key=lambda x : x.quality_value)
                self._search(V, M, target, TP, FP)
    
    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """Main method to run the VLSD algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported.
        
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'DataFrame'.")
        if type(target) is not tuple:
            raise TypeError("The type of the parameter 'target' must be 'tuple'.")
        # IMPORTANT: this algorithm only supports nominal attributes (i.e., type 'str').
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise DatasetAttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
        # Open the file if the path is not None.
        if (self._file_path is not None):
            self._file = open(self._file_path, "w")
        # Obtain TP and FP of the dataset.
        TP = sum(pandas_dataframe[target[0]] == target[1])
        FP = len(pandas_dataframe.index) - TP
        # Get the list of Vertical Lists of size 1 (i.e., only one selector in their lists of selectors).
        S1 = self._generate_subgroups_s1(pandas_dataframe, target, TP, FP)
        # Handle each individual result.
        for s in S1:
            self._handle_individual_result( (s, target, TP, FP) )
        # Create 2-dimensional empty matrix M (in this case, it is a python dictionary).
        M = dict()
        # Double iteration through S1.
        for index_x in range(len(S1)): # From 0 to len(S1)-1.
            s_x = S1[index_x]
            # Get the last selector of s_x. In this point, there is only one.
            s_x_last_selector = s_x.list_of_selectors[-1]
            for index_y in range(index_x+1, len(S1)): # IMPORTANT: x < y ==> From x+1 to len(S1)-1.
                s_y = S1[index_y]
                # Get the last selector of s_y. In this point, there is only one.
                s_y_last_selector = s_y.list_of_selectors[-1]
                # Get the quality value of the join of s_x and s_y.
                s_xy_dict_of_parameters = {QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP}
                s_xy_dict_of_parameters.update(self._additional_parameters_for_the_optimistic_estimate)
                s_xy = s_x.join(s_y, self._optimistic_estimate, s_xy_dict_of_parameters, return_None_if_n_is_0 = True)
                # Check whether n (i.e., tp+fp) is 0 or greater than 0 (in this case, 's_xy' will be None) and whether 's_xy' has quality enough.
                if (s_xy is not None) and (s_xy.quality_value >= self._oe_minimum_threshold):
                    # Add to the dictionary.
                    if s_x_last_selector not in M:
                        M[s_x_last_selector] = dict()
                    # ---> IMPORTANT: M[s_x_last_selector][s_y_last_selector] is equal to M[s_y_last_selector][s_x_last_selector], but only one entry is added (to save memory). This will have to be kept in mind later.
                    M[s_x_last_selector][s_y_last_selector] = s_xy
        # Iterate through the Vertical Lists of size 2 and call to search method.
        for index in range(len(S1)-1): # From 0 to len(S1)-2.
            selector_i = S1[index].list_of_selectors[-1]
            if (selector_i in M):
                # Get all the values (in this case, Vertical Lists) from the corresponding dictionary.
                P = list(M[selector_i].values())
                # Sort by quality value (optimistic_estimate_value) according to 'sort_criterion_in_other_sizes'.
                if (self._sort_criterion_in_other_sizes == VLSD.SORT_CRITERION_QUALITY_ASCENDING):
                    P.sort(reverse=False, key=lambda x : x.quality_value)
                elif (self._sort_criterion_in_other_sizes == VLSD.SORT_CRITERION_QUALITY_DESCENDING):
                    P.sort(reverse=True, key=lambda x : x.quality_value)
                # Handle each individual result.
                for s in P:
                    self._handle_individual_result( (s, target, TP, FP) )
                self._search(P, M, target, TP, FP)
        # Close the file if it was opened before.
        if (self._file_path is not None):
            self._file.close()
            self._file = None
