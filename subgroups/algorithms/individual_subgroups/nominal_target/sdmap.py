# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the SDMap algorithm.
"""

from pandas import DataFrame
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from numpy import sum

# Python annotations.
from typing import Union

def _generate_all_combinations(list_of_selectors : list[Selector]):
    """Private method to generate all the combinations (including the empty list) of the list of selectors passed by parameter.
    
    :param list_of_selectors: the list of selectors which is used.
    :return: all combinations (including the empty list) of the list of selectors passed by parameter.
    """
    if list_of_selectors == []:
        return [[]]
    x = _generate_all_combinations(list_of_selectors[1:])
    return x + [[list_of_selectors[0]] + y for y in x]

def _delete_subgroup_parameters_from_a_dictionary(dict_of_parameters : dict[str, Union[int, float]]):
    """Private method to delete the subgroup parameters (i.e., tp, fp, TP and FP) from a dictionary of parameters. IMPORTANT: this method modifies the parameter, does not return a new dictionary.
    
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

class SDMap(Algorithm):
    """This class represents the SDMap algorithm. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
    
    :param quality_measure: the quality measure which is used.
    :param minimum_quality_measure_value: the minimum quality measure value threshold.
    :param minimum_tp: the minimum true positives (tp) threshold.
    :param minimum_fp: the minimum false positives (fp) threshold.
    :param minimum_n: the minimum subgroup description size (n) threshold.
    :param additional_parameters_for_the_quality_measure: if the quality measure passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """
    
    __slots__ = ("_quality_measure", "_minimum_quality_measure_value", "_minimum_tp", "_minimum_fp", "_minimum_n", "_additional_parameters_for_the_quality_measure", "_unselected_subgroups", "_selected_subgroups", "_file_path", "_file")
    
    def __init__(self, quality_measure : QualityMeasure, minimum_quality_measure_value : Union[int, float], minimum_tp : Union[int, None] = None, minimum_fp : Union[int, None] = None, minimum_n : Union[int, None] = None, additional_parameters_for_the_quality_measure : dict[str, Union[int, float]] = dict(), write_results_in_file : bool = False, file_path : Union[str, None] = None) -> None:
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be an instance of a subclass of the 'QualityMeasure' class.")
        if (type(minimum_quality_measure_value) is not int) and (type(minimum_quality_measure_value) is not float):
            raise TypeError("The type of the parameter 'minimum_quality_measure_value' must be 'int' or 'float'.")
        if (type(minimum_tp) is not int) and (minimum_tp is not None):
            raise TypeError("The type of the parameter 'minimum_tp' must be 'int' or 'NoneType'.")
        if (type(minimum_fp) is not int) and (minimum_fp is not None):
            raise TypeError("The type of the parameter 'minimum_fp' must be 'int' or 'NoneType'.")
        if (type(minimum_n) is not int) and (minimum_n is not None):
            raise TypeError("The type of the parameter 'minimum_n' must be 'int' or 'NoneType'.")
        if (type(additional_parameters_for_the_quality_measure) is not dict):
            raise TypeError("The type of the parameter 'additional_parameters_for_the_quality_measure' must be 'dict'")
        if (type(write_results_in_file) is not bool):
            raise TypeError("The type of the parameter 'write_results_in_file' must be 'bool'")
        if ((type(file_path) is not str) and (file_path is not None)):
            raise TypeError("The type of the parameter 'file_path' must be 'str' or 'NoneType'.")
        # If 'write_results_in_file' is True, 'file_path' must not be None.
        if (write_results_in_file) and (file_path is None):
            raise ValueError("If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        # Depending on the values of the parameters 'minimum_tp', 'minimum_fp' and 'minimum_n' ...
        if ( (minimum_tp is not None) and (minimum_fp is not None) and (minimum_n is None) ) or \
            ( (minimum_tp is None) and (minimum_fp is None) and (minimum_n is not None) ):
            self._quality_measure = quality_measure
            self._minimum_quality_measure_value = minimum_quality_measure_value
            self._minimum_tp = minimum_tp
            self._minimum_fp = minimum_fp
            self._minimum_n = minimum_n
            self._unselected_subgroups = 0
            self._selected_subgroups = 0
            self._additional_parameters_for_the_quality_measure = additional_parameters_for_the_quality_measure.copy()
            _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_quality_measure)
            if (write_results_in_file):
                self._file_path = file_path
            else:
                self._file_path = None
            self._file = None
        else:
            raise InconsistentMethodParametersError("If 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.")
    
    def _get_quality_measure(self) -> QualityMeasure:
        return self._quality_measure
    
    def _get_minimum_quality_measure_value(self) -> Union[int, float]:
        return self._minimum_quality_measure_value
    
    def _get_minimum_tp(self) -> Union[int, None]:
        return self._minimum_tp
    
    def _get_minimum_fp(self) -> Union[int, None]:
        return self._minimum_fp
    
    def _get_minimum_n(self) -> Union[int, None]:
        return self._minimum_n
    
    def _get_additional_parameters_for_the_quality_measure(self) -> dict[str, Union[int, float]]:
        return self._additional_parameters_for_the_quality_measure
    
    quality_measure = property(_get_quality_measure, None, None, "The quality measure which is used.")
    minimum_quality_measure_value = property(_get_minimum_quality_measure_value, None, None, "The minimum quality measure value threshold.")
    minimum_tp = property(_get_minimum_tp, None, None, "The minimum true positives (tp) threshold.")
    minimum_fp = property(_get_minimum_fp, None, None, "The minimum false positives (fp) threshold.")
    minimum_n = property(_get_minimum_n, None, None, "The minimum subgroup description size (n) threshold.")
    additional_parameters_for_the_quality_measure = property(_get_additional_parameters_for_the_quality_measure, None, None, "The additional needed parameters with which to compute the quality measure.")
    
    def _get_unselected_subgroups(self) -> int:
        return self._unselected_subgroups

    def _get_selected_subgroups(self) -> int:
        return self._selected_subgroups

    def _get_visited_nodes(self) -> int:
        return self._unselected_subgroups + self._selected_subgroups

    unselected_subgroups = property(_get_unselected_subgroups, None, None, "Number of unselected subgroups after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")
    selected_subgroups = property(_get_selected_subgroups, None, None, "Number of selected subgroups after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")
    visited_nodes = property(_get_visited_nodes, None, None, "Number of visited nodes after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")

    def _handle_individual_result(self, individual_result : tuple[Pattern, tuple[str, str], int, int, int, int]) -> None:
        """Private method to handle each individual result generated by the SDMap algorithm.
        
        :param individual_result: the individual result which is handled. In this case, it is a subgroup description, a target as a tuple and the subgroup parameters tp, fp, TP and FP.
        """
        # Get the subgroup parameters.
        tp = individual_result[2]
        fp = individual_result[3]
        TP = individual_result[4]
        FP = individual_result[5]
        # Compute the quality measure of the frequent pattern along with the target (i.e., the quality measure of the subgroup).
        dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : tp, QualityMeasure.FALSE_POSITIVES : fp, QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP}
        dict_of_parameters.update(self._additional_parameters_for_the_quality_measure)
        quality_measure_value = self._quality_measure.compute(dict_of_parameters)
        # Add the subgroup only if the quality measure value is greater or equal than the threshold.
        if quality_measure_value >= self._minimum_quality_measure_value:
            # If applicable, write in the file defined in the __init__ method.
            if self._file_path is not None:
                # Get the description and the target.
                subgroup_description = individual_result[0]
                target_as_tuple = individual_result[1] # Attribute name -> target_as_tuple[0], Attribute value -> target_as_tuple[1]
                # Create the subgroup.
                subgroup = Subgroup(subgroup_description, Selector(target_as_tuple[0], Operator.EQUAL, target_as_tuple[1]))
                # Write.
                self._file.write(str(subgroup) + " ; ")
                self._file.write("Quality Measure " + self._quality_measure.get_name() + " = " + str(quality_measure_value) + " ; ")
                self._file.write("tp = " + str(tp) + " ; ")
                self._file.write("fp = " + str(fp) + " ; ")
                self._file.write("TP = " + str(TP) + " ; ")
                self._file.write("FP = " + str(FP) + "\n")
            # Increment the number of selected subgroups.
            self._selected_subgroups = self._selected_subgroups + 1
        else: # If the quality measure is not greater or equal, increment the number of unselected subgroups.
            self._unselected_subgroups = self._unselected_subgroups + 1
    
    def _fpgrowth(self, fptree : FPTreeForSDMap, alpha : Union[list[Selector], None], target : tuple[str, str], TP : int, FP : int) -> None:
        """Private method to run the adapted FPGrowth algorithm in order to generate frequent patterns.
        
        :param fptree: the current FPTree. At the beginning, it is the FPTreeForSDMap generated from the complete dataset. Although, it will change between recursive calls to this method.
        :param alpha: a list of selectors (or None, in the first call to this method).
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :param TP: the true population of the dataset (i.e., the number of instances in which the target appears).
        :param FP: the false population of the dataset (i.e., the number of instances in which the target does not appear).
        """
        # Check if fptree contains a single path.
        if fptree.there_is_a_single_path():
            # Generate all the combinations of the selectors in the single path.
            all_combinations = _generate_all_combinations(fptree._sorted_header_table)
            # Remove the empty list.
            all_combinations.remove([])
            # Iterate throughout the combinations.
            for beta in all_combinations:
                # Generate the patter 'beta U alpha'.
                # IMPORTANT: in this case, we can use the class Pattern for the frequent patterns because each frequent pattern will be the description of a final subgroup.
                if alpha:
                    pattern = Pattern(beta + alpha)
                else:
                    pattern = Pattern(beta)
                # The values of the counters tp and fp of 'pattern' will be those of the selector in beta with the less values of the counters tp and fp in the fptree (in the header table of the fptree).
                most_unfrequent_selector = None
                index = 0
                # IMPORTANT: this is not an infinite loop because ALL the selectors in beta are always also in the header table (because all the combinations had generated from the header table).
                while (most_unfrequent_selector is None):
                    if (fptree._sorted_header_table[index] in beta): # This comparison has been extracted from the SDMap implementation in Vikamine.
                        most_unfrequent_selector = fptree._sorted_header_table[index]
                    index = index + 1
                tp = fptree.header_table[most_unfrequent_selector][0][0]
                fp = fptree.header_table[most_unfrequent_selector][0][1]
                # Handle this result.
                self._handle_individual_result( (pattern, target, tp, fp, TP, FP) )
        else:
            # Iterate throughout the selectors in the sorted header table of the fptree.
            for ai in fptree._sorted_header_table:
                # Generate the pattern 'beta = ai U a'.
                #  -> As list in order to build the conditional FPTree and as Pattern in order to add it to the final result.
                # IMPORTANT: in this case, we can use the class Pattern for the frequent patterns because each frequent pattern will be the description of a final subgroup.
                if alpha:
                    beta_as_list = [ai] + alpha
                    beta_as_Pattern = Pattern(beta_as_list)
                else:
                    beta_as_list = [ai]
                    beta_as_Pattern = Pattern(beta_as_list)
                # The values of the counters tp and fp of 'beta' will be those of the selector ai in the header table.
                tp = fptree.header_table[ai][0][0]
                fp = fptree.header_table[ai][0][1]
                # Handle this result.
                self._handle_individual_result( (beta_as_Pattern, target, tp, fp, TP, FP) )
                # Build the conditional FPTree.
                conditional_fp_tree = fptree.generate_conditional_fp_tree(beta_as_list, minimum_tp=self.minimum_tp, minimum_fp=self.minimum_fp, minimum_n=self.minimum_n)
                # Recursive call.
                if not conditional_fp_tree.is_empty():
                    self._fpgrowth(conditional_fp_tree, beta_as_list, target, TP, FP)
    
    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """Main method to run the SDMap algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
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
        # Create an empty FPTreeForSDMap.
        fptree = FPTreeForSDMap()
        # Generate the set of frequent selectors.
        set_of_frequent_selectors = fptree.generate_set_of_frequent_selectors(pandas_dataframe, target, minimum_tp=self.minimum_tp, minimum_fp=self.minimum_fp, minimum_n=self.minimum_n)
        # Build the FPTree.
        fptree.build_tree(pandas_dataframe, set_of_frequent_selectors, target)
        # Only if the fptree is not empty ...
        if not fptree.is_empty():
            # Obtain TP and FP of the dataset.
            TP = sum(pandas_dataframe[target[0]] == target[1])
            FP = len(pandas_dataframe.index) - TP
            # Call to the adapated FPGrowth algorithm in order to obtain frequent patterns. In this point, we also open and close the file.
            if (self._file_path is not None):
                self._file = open(self._file_path, "w")
            self._fpgrowth(fptree, None, target, TP, FP)
            if (self._file_path is not None):
                self._file.close()
                self._file = None
