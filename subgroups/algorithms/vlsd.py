# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the VLSD algorithm.
"""

from pandas import DataFrame
from pandas.api.types import is_string_dtype
from pandas import Index
from subgroups.algorithms._base import Algorithm
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
            # - The property 'groups' is a dictionary in which the key is the tuple "(column, target_attribute_as_a_mask)" and the value is a sequence of registers in which that combination appears.
            values_and_target_grouped = pandas_dataframe.groupby([column, target_attribute_as_a_mask]).groups
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
                        registers_tp = Index([]) # Empty sequence.
                    # Registers which do not have the target.
                    try:
                        registers_fp = values_and_target_grouped[(value,False)]
                    except KeyError:
                        registers_fp = Index([]) # Empty sequence.
                    # Compute the upper bound.
                    dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_tp : len(registers_tp), QualityMeasure.SUBGROUP_PARAMETER_fp : len(registers_fp), QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
                    dict_of_parameters.update(self._additional_parameters_for_the_upper_bound)
                    upper_bound_value = self._upper_bound.compute(dict_of_parameters)
                    # Pruning: add the Vertical List only if the upper bound value is greater or equal than the threshold.
                    if upper_bound_value >= self._minimum_threshold:
                        # Create the Vertical List.
                        vl = VerticalList([Selector(column, Operator.EQUAL, value)], registers_tp, registers_fp, upper_bound_value)
                        # Add it to the final list.
                        result.append(vl)
                    # Finally, add the value to 'processed_values'.
                    processed_values.add(value)
            # Sort descending by quality value.
            result.sort(reverse=True, key=lambda x : x.quality_value)
            # Return the list.
            return result
    
    def _search(self, vl, P, M, TP, FP):
        """ Private search method.
        
        :type vl: VerticalList
        :param vl: a vertical list.
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
        # Iterate through the vertical lists in P.
        for index_x in range(len(P)):
            Px = P[index_x]
            # If the quality of the current element is greater or equal than the threshold, add to the final result.
            if Px.quality_value >= self._minimum_threshold:
                F.append(Px)
            # Get the last selector of Px.
            ea = Px.list_of_selectors[-1]
            # If Px is not the last element in the list P and ((vl.quality + M[ea][ea]) >= threshold), then ...
            vl_quality_value = 0
            if vl is not None:
                vl_quality_value = vl.quality_value
            if (Px != P[-1]) and ((vl_quality_value + M[ea][ea]) >= self._minimum_threshold):
                V = []
                # Iterate through the vertical lists in P whose index is greater than 'index_x'.
                for index_y in range(index_x+1, len(P)): # IMPORTANT: x < y
                    Py = P[index_y]
                    # Get the last selector of Py.
                    eb = Py.list_of_selectors[-1]
                    # If (M[ea][eb] >= threshold), then ...
                    # --> IMPORTANT: M[ea][eb] or M[ea][eb]. It is the same.
                    try:
                        M_ea_eb = M[ea][eb]
                    except KeyError:
                        # --> IMPORTANT: If the parameter n of the union was 0, there is no entry in the dictionary.
                        try:
                            M_ea_eb = M[eb][ea]
                        except KeyError:
                            M_ea_eb = None
                    if (M_ea_eb is not None) and (M_ea_eb >= self._minimum_threshold):
                        # In this case, it is not necessary to include the tp and fp parameters (because they will be included in the union).
                        dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
                        dict_of_parameters.update(self._additional_parameters_for_the_upper_bound)
                        # Make the union.
                        new_vl_union = Px.union(Py, self._upper_bound, dict_of_parameters, return_None_if_n_is_0=True)
                        # Add the new vertical list to the list V.
                        if new_vl_union is not None:
                            V.append(new_vl_union)
                # Check whether the list V is not empty.
                if V:
                    # If V is not empty, recursive call.
                    F = F + self._search(Px, V, M, TP, FP)
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
                vl_xy_sequence_of_instances_tp = vl_x._sequence_of_instances_tp.intersection(vl_y._sequence_of_instances_tp, sort=False)
                vl_xy_sequence_of_instances_fp = vl_x._sequence_of_instances_fp.intersection(vl_y._sequence_of_instances_fp, sort=False)
                tp = len(vl_xy_sequence_of_instances_tp)
                fp = len(vl_xy_sequence_of_instances_fp)
                vl_xy_dict_of_parameters = {QualityMeasure.SUBGROUP_PARAMETER_tp : tp, QualityMeasure.SUBGROUP_PARAMETER_fp : fp, QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP}
                vl_xy_dict_of_parameters.update(self._additional_parameters_for_the_upper_bound)
                # Check whether n (i.e., tp+fp) is 0 or greater than 0.
                if (tp + fp) > 0:
                    # Add to the dictionary.
                    M[ea] = dict()
                    # ---> IMPORTANT: M[ea][eb] is equal to M[eb][ea], but only one entry is added (to save memory). This will have to be kept in mind later.
                    M[ea][eb] = self._upper_bound.compute(vl_xy_dict_of_parameters)
        # Call to the search method.
        F = self._search(None, P, M, TP, FP)
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
        # Return the result.
        return R