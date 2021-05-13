# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the VLSD algorithm.
"""

from pandas import DataFrame
from pandas.api.types import is_string_dtype
from subgroups.algorithms._base import Algorithm
from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import DatasetAttributeTypeError
from subgroups.data_structures.vertical_list import VerticalList
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup

def _delete_subgroup_parameters_from_a_dictionary(dict_of_parameters):
    """Private method to delete the subgroup parameters (i.e., tp, fp, TP and FP) from a dictionary of parameters.
    
    :type dict_of_parameters: dict[str, int or float]
    :param dict_of_parameters: the dictionary of parameters which is modified.
    """
    try:
        del dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_tp]
    except KeyError:
        pass
    try:
        del dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_fp]
    except KeyError:
        pass
    try:
        del dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_TP]
    except KeyError:
        pass
    try:
        del dict_of_parameters[QualityMeasure.SUBGROUP_PARAMETER_FP]
    except KeyError:
        pass

class VLSD(Algorithm):
    """This class represents the VLSD algorithm.
    
    :type quality_measure: QualityMeasure
    :param quality_measure: the quality measure which is used.
    :type upper_bound: QualityMeasure
    :param upper_bound: the Upper Bound (a.k.a. Optimistic Estimate) of the quality measure which is used.
    :type minimum_threshold: int or float
    :param minimum_threshold: the minimum quality threshold.
    :type additional_parameters_for_the_quality_measure: dict[str, int or float]
    :param additional_parameters_for_the_quality_measure: if the quality measure passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :type additional_parameters_for_the_upper_bound: dict[str, int or float]
    :param additional_parameters_for_the_upper_bound: if the upper bound passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    """
    
    __slots__ = "_quality_measure", "_upper_bound", "_minimum_threshold", "_additional_parameters_for_the_quality_measure", "_additional_parameters_for_the_upper_bound", "_visited_nodes", "_pruned_nodes"
    
    def __init__(self, quality_measure, upper_bound, minimum_threshold, additional_parameters_for_the_quality_measure=dict(), additional_parameters_for_the_upper_bound=dict()):
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be a subclass of QualityMeasure.")
        if not isinstance(upper_bound, QualityMeasure):
            raise TypeError("The parameter 'upper_bound' must be a subclass of QualityMeasure.")
        # We check whether 'upper_bound' is an upper bound of 'quality_measure'.
        if quality_measure.get_name() not in upper_bound.upper_bound_of():
            raise ValueError("The quality measure " + upper_bound.get_name() + " is not an upper bound of the quality measure " + quality_measure.get_name() + ".")
        if (type(minimum_threshold) is not int) and (type(minimum_threshold) is not float):
            raise TypeError("The type of the parameter 'minimum_threshold' must be 'int' or 'float'.")
        if (type(additional_parameters_for_the_quality_measure) is not dict):
            raise TypeError("The type of the parameter 'additional_parameters_for_the_quality_measure' must be 'dict'")
        if (type(additional_parameters_for_the_upper_bound) is not dict):
            raise TypeError("The type of the parameter 'additional_parameters_for_the_upper_bound' must be 'dict'")
        self._quality_measure = quality_measure
        self._upper_bound = upper_bound
        self._minimum_threshold = minimum_threshold
        self._additional_parameters_for_the_quality_measure = additional_parameters_for_the_quality_measure.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_quality_measure)
        self._additional_parameters_for_the_upper_bound = additional_parameters_for_the_upper_bound.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_upper_bound)
        self._visited_nodes = 0
        self._pruned_nodes = 0
    
    def _get_quality_measure(self):
        return self._quality_measure
    
    def _get_upper_bound(self):
        return self._upper_bound
    
    def _get_minimum_threshold(self):
        return self._minimum_threshold
    
    def _get_additional_parameters_for_the_quality_measure(self):
        return self._additional_parameters_for_the_quality_measure
    
    def _get_additional_parameters_for_the_upper_bound(self):
        return self._additional_parameters_for_the_upper_bound
    
    quality_measure = property(_get_quality_measure, None, None, "The quality measure which is used.")
    upper_bound = property(_get_upper_bound, None, None, "The Upper Bound (a.k.a. Optimistic Estimate) of the quality measure which is used.")
    minimum_threshold = property(_get_minimum_threshold, None, None, "The minimum quality threshold.")
    additional_parameters_for_the_quality_measure = property(_get_additional_parameters_for_the_quality_measure, None, None, "The additional needed parameters with which to compute the quality measure.")
    additional_parameters_for_the_upper_bound = property(_get_additional_parameters_for_the_upper_bound, None, None, "The additional needed parameters with which to compute the upper bound.")
    
    def _get_visited_nodes(self):
        return self._visited_nodes
    
    def _get_pruned_nodes(self):
        return self._pruned_nodes
    
    visited_nodes = property(_get_visited_nodes, None, None, "The visited nodes after executing the VLSD algorithm (before executing the 'fit' method, this attribute is 0).")
    pruned_nodes = property(_get_pruned_nodes, None, None, "The pruned nodes after executing the VLSD algorithm (before executing the 'fit' method, this attribute is 0).")
    
    # IMPORTANT: although the subgroup parameters TP and FP can be computed from 'pandas_dataframe', we also pass them by parameter in this method to avoid computing them twice (in the 'fit' method and in this method).
    def _generate_initial_list_of_vertical_lists(self, pandas_dataframe, TP, FP, target):
        """Private method to generate the initial list of vertical lists, prune it and sort it.
        
        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str') without missing values.
        :type TP: int
        :param TP: the True Positives of the dataset. IMPORTANT: although it can be computed from 'pandas_dataframe', we pass it by parameter to avoid computing it twice (in the 'fit' method and in this method).
        :type FP: int
        :param FP: the False Positives of the dataset. IMPORTANT: although it can be computed from 'pandas_dataframe', we pass it by parameter to avoid computing it twice (in the 'fit' method and in this method).
        :type target: tuple[str, str]
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :rtype: list[VerticalList]
        :return: a list in which each element is a Vertical List which represents a single selector (i.e., it only has one selector in its list of selectors). The list is pruned according to the threshold and sorted descending by the quality value of each Vertical List according to the 'upper_bound' attribute.
        """
        # Get the target column as a mask: True if the value is equal to the target value and False otherwise.
        target_attribute_as_a_mask = (pandas_dataframe[target[0]] == target[1])
        # Result.
        result = []
        # Iterate through the columns (except the target).
        for column in pandas_dataframe.columns.drop(target[0]):
            # Use the 'groupby' method in order to group each value depending on whether appears with the target or not.
            # - The property 'groups' is a dictionary in which the key is the tuple "(column, target_attribute_as_a_mask)" and the value is a sequence of register indices in which that combination appears.
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
                    # Compute the upper bound.
                    dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_tp : len(registers_tp), QualityMeasure.SUBGROUP_PARAMETER_fp : len(registers_fp), QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
                    dict_of_parameters.update(self._additional_parameters_for_the_upper_bound)
                    upper_bound_value = self._upper_bound.compute(dict_of_parameters)
                    # Pruning: add the Vertical List only if the upper bound value is greater or equal than the threshold.
                    if upper_bound_value >= self._minimum_threshold:
                        # Create the Vertical List.
                        vl = VerticalList([Selector(column, Operator.EQUAL, value)], registers_tp, registers_fp, TP+FP, upper_bound_value)
                        # Add it to the final list.
                        result.append(vl)
                    # Finally, add the value to 'processed_values'.
                    processed_values.add(value)
        # Sort descending by quality value.
        result.sort(reverse=True, key=lambda x : x.quality_value)
        # Return the list.
        return result
    
    def _search(self, P, M, TP, FP):
        """ Private search method.
        
        :type P: list[VerticalList]
        :param P: a list of vertical lists.
        :type M: dict[VerticalList, dict[VerticalList, int or float]]
        :param M: the 2-dimensional matrix M (in this case, it is a python dictionary).
        :type TP: int
        :param TP: the True Positives of the dataset.
        :type FP: int
        :param FP: the False Positives of the dataset.
        :rtype: list[tuple[VerticalList, int or float]]
        :return: a list of tuples in which each element has a Vertical List and its upper bound (a.k.a. optimistic estimate) value according to 'upper_bound' attribute.
        """
        # Final result.
        F = []
        # Initial variables.
        depth = 0
        s = [-1] * len(P)
        svl = [None] * len(P)
        # Main loop
        while(depth > -1):
            if (depth == 0):
                if s[depth] == -1:
                    s[depth] = 0
                else:
                    s[depth] = s[depth] + 1
                current_vl = P[s[depth]]
            else:
                if s[depth] == -1:
                    s[depth] = s[depth-1] + 1
                else:
                    s[depth] = s[depth] + 1
                parent = svl[depth-1]
                Pi = P[s[depth]]
                oe_dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
                oe_dict_of_parameters.update(self._additional_parameters_for_the_upper_bound)
                current_vl = parent.union(Pi, self._upper_bound, oe_dict_of_parameters, return_None_if_n_is_0 = True)
            svl[depth] = current_vl
            # IMPORTANT: current_vl equal to None means that (current_vl.tp+current_vl.fp) is 0.
            if (current_vl is not None) and (current_vl.quality_value >= self._minimum_threshold):
                F.append(current_vl)
            #print("#############################################################")
            #print("Depth: " + str(depth))
            #print("s: " + str(s))
            #svl_as_string = ""
            #for vl in svl:
            #    if vl is not None:
            #        svl_as_string = svl_as_string + str(vl.list_of_selectors) + "(" + str(vl.n) + "), "
            #    else:
            #        svl_as_string = svl_as_string + "None, "
            #print(svl_as_string)
            # IMPORTANT: current_vl equal to None means that (current_vl.tp+current_vl.fp) is 0.
            if (current_vl is not None) and (depth < (len(P)-1)) and (s[depth] < (len(P)-1)):
                depth = depth + 1
            else:
                while (not (s[depth] < (len(P)-1))) and (depth > -1):
                    svl[depth] = None
                    s[depth] = -1
                    depth = depth - 1
        # Return the result.
        return F
    
    def fit(self, pandas_dataframe, target):
        """Method to run the VLSD algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        
        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :type target: tuple[str, str]
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :rtype: list[tuple[Subgroup, int or float, int or float]]
        :return: a list of tuples in which each element has a subgroup, its quality measures value according to 'quality_measure' attribute and its upper bound (a.k.a. optimistic estimate) value according to 'upper_bound' attribute.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'DataFrame'.")
        if type(target) is not tuple:
            raise TypeError("The type of the parameter 'target' must be 'tuple'.")
        # IMPORTANT: this algorithm only supports nominal attributes (i.e., type 'str').
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise DatasetAttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
        # Result.
        R = []
        # Obtain TP and FP of the dataset.
        TP = sum(pandas_dataframe[target[0]] == target[1])
        FP = len(pandas_dataframe.index) - TP
        # Get the initial list of vertical lists.
        P = self._generate_initial_list_of_vertical_lists(pandas_dataframe, TP, FP, target)
        # Create 2-dimensional empty matrix M (in this case, it is a python dictionary).
        M = dict()
        # Double iteration through P.
        for index_x in range(len(P)):
            vl_x = P[index_x]
            for index_y in range(index_x, len(P)): # IMPORTANT: x <= y
                vl_y = P[index_y]
                # Get the last selector of vl_x. In this point, there is only one.
                ea = vl_x.list_of_selectors[-1]
                # Get the last selector of vl_y. In this point, there is only one.
                eb = vl_y.list_of_selectors[-1]
                # Get the quality value of the union of vl_x and vl_y.
                # --> IMPORTANT: we only need the quality value and, therefore, it is not necessary to create a new vertical list object.
                # ----> REMEMBER: in a vertical list, the sequences are bitarrays.
                vl_xy_sequence_of_instances_tp = vl_x._sequence_of_instances_tp & vl_y._sequence_of_instances_tp
                vl_xy_sequence_of_instances_fp = vl_x._sequence_of_instances_fp & vl_y._sequence_of_instances_fp
                tp = vl_xy_sequence_of_instances_tp.count(1)
                fp = vl_xy_sequence_of_instances_fp.count(1)
                vl_xy_dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_tp : tp, QualityMeasure.SUBGROUP_PARAMETER_fp : fp, QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
                vl_xy_dict_of_parameters.update(self._additional_parameters_for_the_upper_bound)
                # Check whether n (i.e., tp+fp) is 0 or greater than 0.
                if (tp + fp) > 0:
                    # Add to the dictionary.
                    if ea not in M:
                        M[ea] = dict()
                    # ---> IMPORTANT: M[ea][eb] is equal to M[eb][ea], but only one entry is added (to save memory). This will have to be kept in mind later.
                    M[ea][eb] = self._upper_bound.compute(vl_xy_dict_of_parameters)
        # Call to the search method.
        F = self._search(P, M, TP, FP)
        # Iterate through the result (list F).
        for vl in F:
            # Compute the quality meaasure q ('quality_measure' attribute).
            q_dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_tp : vl.tp, QualityMeasure.SUBGROUP_PARAMETER_fp : vl.fp, QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
            q_dict_of_parameters.update(self._additional_parameters_for_the_quality_measure)
            q_value = self._quality_measure.compute(q_dict_of_parameters)
            # Check whether the value of q is greater or equal than the threshold.
            if (q_value >= self._minimum_threshold):
                # Create the subgroup.
                s = Subgroup(Pattern(vl.list_of_selectors), Selector(target[0], Operator.EQUAL, target[1]))
                # Get the upper bound.
                oe_value = vl.quality_value
                # Add the corresponding tuple to the list R.
                R.append( (s, q_value, oe_value) )
                # Increment the number of visited nodes.
                self._visited_nodes = self._visited_nodes + 1
            else: # If the quality measure is not greater or equal, increment the number of pruned nodes.
                self._pruned_nodes = self._pruned_nodes + 1
        # Return the result.
        return R
