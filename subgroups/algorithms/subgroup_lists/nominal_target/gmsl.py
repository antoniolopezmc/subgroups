# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the GMSL algorithm.
"""

from subgroups.algorithms.algorithm import Algorithm
from subgroups.data_structures import SubgroupList
from pandas import DataFrame, unique
from subgroups.utils.mdl import universal_code_for_integer, log2_multinomial_with_recurrence
from numpy import log2
from math import comb
from subgroups.core import Operator, Selector, Pattern, Subgroup
from bitarray import bitarray
from pandas.api.types import is_string_dtype
from subgroups.exceptions import DatasetAttributeTypeError
from re import compile
from re import Pattern as rePattern

# Python annotations.
from typing import ClassVar, List, Union

class GMSL(Algorithm):
    """This class represents the GMSL algorithm.
    
    :param input_file_path: path of the file from which the subgroups and their bitarrays will be read.
    :param max_sl: maximum number of subgroups lists to generate.
    :param beta: level of normalization of the compression gain.
    :param output_file_path: path of the file in which the results will be written.
    """
    
    _selector_regex_pattern : ClassVar[str] = "[&,\\.<>/=A-Za-z0-9_-]+ = ([&,\\.<>/=A-Za-z0-9_-]+|'[&,\\.<>/=A-Za-z0-9_-]+')"
    _pattern_regex_pattern : ClassVar[str] = "\\[" + _selector_regex_pattern + "(, " + _selector_regex_pattern + ")*\\]"
    INPUT_LINE_REGEX_PATTERN : ClassVar[str] = "^(?P<subgroup>Description: " + _pattern_regex_pattern + ", Target: " + _selector_regex_pattern + ")" +\
                                               " ; (?P<positive_bitarray>[01]+) ; (?P<negative_bitarray>[01]+)$"
    _input_line_regex_object : ClassVar[rePattern] = compile(INPUT_LINE_REGEX_PATTERN)

    __slots__ = ("_input_file_path", "_max_sl", "_beta", "_output_file_path", "_output_file")

    def __init__(self, input_file_path : str, max_sl : int, beta : float, output_file_path : str) -> None:
        if type(input_file_path) is not str:
            raise TypeError("The type of the parameter 'input_file_path' must be 'str'.")
        if type(max_sl) is not int:
            raise TypeError("The type of the parameter 'max_sl' must be 'int'.")
        if (max_sl <= 0):
            raise ValueError("The parameter 'max_sl' is not greater than 0.")
        if (type(beta) is not int) and (type(beta) is not float):
            raise TypeError("The type of the parameter 'beta' must be 'int' or 'float'.")
        if (beta < 0.0) or (beta > 1.0):
            raise ValueError("The parameter 'beta' is not between 0.0 and 1.0 (both included).")
        if type(output_file_path) is not str:
            raise TypeError("The type of the parameter 'output_file_path' must be 'str'.")
        self._input_file_path = input_file_path
        self._max_sl = max_sl
        self._beta = beta
        self._output_file_path = output_file_path
        self._output_file = None
    
    def _get_input_file_path(self) -> str:
        return self._input_file_path

    def _get_max_sl(self) -> int:
        return self._max_sl

    def _get_beta(self) -> Union[int, float]:
        return self._beta

    def _get_output_file_path(self) -> str:
        return self._output_file_path

    input_file_path = property(_get_input_file_path, None, None, "Path of the file from which the subgroups and their bitarrays will be read.")
    max_sl = property(_get_max_sl, None, None, "Maximum number of subgroups lists to generate.")
    beta = property(_get_beta, None, None, "Level of normalization of the compression gain.")
    output_file_path = property(_get_output_file_path, None, None, "Path of the file in which the results will be written.")

    @staticmethod
    def _compute_delta_data_model_candidate(pandas_dataframe : DataFrame, subgroup_list : SubgroupList, subgroup : Subgroup, subgroup_bitarray_of_positives : bitarray, subgroup_bitarray_of_negatives : bitarray) -> tuple[float, int]:
        """Private static method to compute the compression gain considering the data, the model and the candidate.

        :param pandas_dataframe: the DataFrame from which the subgroups were extracted.
        :param subgroup_list: subgroup list model. IMPORTANT: the model is not modified after the execution of this method.
        :param subgroup: individual subgroup candidate which is added to the model.
        :param bitarray_of_positives: the bitarray of the dataset instances (considering the complete dataset) which are covered by the subgroup description and by the subgroup target.
        :param bitarray_of_negatives: the bitarray of the dataset instances (considering the complete dataset) which are covered by the subgroup description, but not by the subgroup target.
        :return: a 2-tuple with (1) the compression gain considering the data, model and the candidate; and (2) the number of rows covered by the candidate (considering its position in the subgroup list).
        """
        # Number of rows of the dataset.
        dataset_number_of_rows = subgroup_list.dataset_number_of_positives + subgroup_list.dataset_number_of_negatives
        # Default rule before adding the candidate.
        defrule_number_of_positives = subgroup_list.default_rule_bitarray_of_positives.count(1)
        defrule_number_of_negatives = subgroup_list.default_rule_bitarray_of_negatives.count(1)
        defrule_before_candidate = - defrule_number_of_positives * log2(subgroup_list.dataset_number_of_positives/dataset_number_of_rows) \
                                - defrule_number_of_negatives * log2(subgroup_list.dataset_number_of_negatives/dataset_number_of_rows)
        # Add temporary the candidate to the model.
        subgroup_list.add_subgroup(subgroup, subgroup_bitarray_of_positives, subgroup_bitarray_of_negatives)
        # Default rule after adding the candidate.
        defrule_number_of_positives = subgroup_list.default_rule_bitarray_of_positives.count(1)
        defrule_number_of_negatives = subgroup_list.default_rule_bitarray_of_negatives.count(1)
        defrule_after_candidate = - defrule_number_of_positives * log2(subgroup_list.dataset_number_of_positives/dataset_number_of_rows) \
                                - defrule_number_of_negatives * log2(subgroup_list.dataset_number_of_negatives/dataset_number_of_rows)
        # Candidate (considering its position in the subgroup list).
        candidate_number_of_positives = subgroup_list.get_subgroup_bitarray_of_positives(-1).count(1) # -1 -> Last subgroup (i.e., the candidate).
        candidate_number_of_negatives = subgroup_list.get_subgroup_bitarray_of_negatives(-1).count(1) # -1 -> Last subgroup (i.e., the candidate).
        candidate_number_of_rows = candidate_number_of_positives + candidate_number_of_negatives
        if candidate_number_of_rows == 0:
            candidate_value = 0
        elif candidate_number_of_positives == 0:
            candidate_value = - candidate_number_of_negatives * log2(candidate_number_of_negatives/candidate_number_of_rows) \
                            + log2_multinomial_with_recurrence(2, candidate_number_of_rows)
        elif candidate_number_of_negatives == 0:
            candidate_value = - candidate_number_of_positives * log2(candidate_number_of_positives/candidate_number_of_rows) \
                            + log2_multinomial_with_recurrence(2, candidate_number_of_rows)
        else:
            candidate_value = - candidate_number_of_positives * log2(candidate_number_of_positives/candidate_number_of_rows) \
                            - candidate_number_of_negatives * log2(candidate_number_of_negatives/candidate_number_of_rows) \
                            + log2_multinomial_with_recurrence(2, candidate_number_of_rows)
        # Delete the candidate from the model.
        subgroup_list.delete_last_subgroup()
        # Return the result.
        return (defrule_before_candidate - defrule_after_candidate - candidate_value, candidate_number_of_rows)

    @staticmethod
    def _compute_delta_model_candidate(pandas_dataframe : DataFrame, subgroup_list : SubgroupList, subgroup : Subgroup) -> float:
        """Private static method to compute the compression gain considering the model and the candidate.

        :param pandas_dataframe: the DataFrame from which the subgroups were extracted.
        :param subgroup_list: subgroup list model. IMPORTANT: the model is not modified after the execution of this method.
        :param subgroup: individual subgroup candidate which is added to the model.
        :return: the compression gain considering the model and the candidate.
        """
        # LN (number of subgroups in the model before adding the candidate) - LN (number of subgroups in the model after adding the candidate)
        result = universal_code_for_integer(len(subgroup_list)) - universal_code_for_integer(len(subgroup_list)+1)
        # - LN (candidate description length)
        result = result - universal_code_for_integer(len(subgroup.description))
        # - log2 (comb (number of attributes from the dataset without considering the target, candidate description length))
        result = result - log2(comb(len(pandas_dataframe.columns)-1, len(subgroup.description)))
        for selector in subgroup.description:
            selector_attribute_name = selector.attribute_name
            # - log2 (number of uniques values from the attribute)
            result = result - log2(len(unique(pandas_dataframe[selector_attribute_name])))
        return result

    def _handle_individual_result(self, individual_result : SubgroupList) -> None:
        """Private method to handle each individual result generated by the VLSD algorithm.
        
        :param individual_result: the individual result which is handled. In this case, it is a subgroup list.
        """
        self._output_file.write(str(individual_result) + "\n")
    
    def _load_candidates(self, number_of_dataset_instances : int) -> tuple[List[Subgroup], List[bitarray], List[bitarray]]:
        """Private method to load the candidates.

        :param number_of_dataset_instances: number of instances of the dataset from which the subgroups were extracted.
        :return: a tuple with 3 lists representing the subgroups, their positive bitsets (considering the complete dataset) and their negative bitsets (considering the complete dataset).
        """
        list_of_subgroups = []
        list_of_bitarrays_of_positives = []
        list_of_bitarrays_of_negatives = []
        # Open the input file and read line by line.
        self._output_file.write("Reading input file.\n")
        line_number = 1
        read_subgroups = 0
        with open(self._input_file_path, "r") as input_file:
            for line in input_file: # Read line by line.
                match_object = GMSL._input_line_regex_object.fullmatch(line.rstrip("\n"))
                if match_object:
                    subgroup = Subgroup.generate_from_str( match_object.group("subgroup") )
                    positive_bitarray = bitarray( match_object.group("positive_bitarray"), endian="big")
                    negative_bitarray = bitarray( match_object.group("negative_bitarray"), endian="big")
                    error_in_bitarays = False
                    if (len(positive_bitarray) != number_of_dataset_instances):
                        self._output_file.write("ERROR: subgroup in line " + str(line_number) + " from input file was not loaded.\n")
                        self._output_file.write("\t- The length of the positive bitarray is not equal to 'number_of_dataset_instances'.\n")
                        error_in_bitarays = True
                    if (len(negative_bitarray) != number_of_dataset_instances):
                        self._output_file.write("ERROR: subgroup in line " + str(line_number) + " from input file was not loaded.\n")
                        self._output_file.write("\t- The length of the negative bitarray is not equal to 'number_of_dataset_instances'.\n")
                        error_in_bitarays = True
                    if not error_in_bitarays:
                        read_subgroups = read_subgroups + 1
                        list_of_subgroups.append(subgroup)
                        list_of_bitarrays_of_positives.append(positive_bitarray)
                        list_of_bitarrays_of_negatives.append(negative_bitarray)
                else:
                    self._output_file.write("ERROR: subgroup in line " + str(line_number) + " from input file was not loaded.\n")
                    self._output_file.write("\t- Format not valid.\n")
                line_number = line_number + 1
        self._output_file.write("Read subgroups: " + str(read_subgroups) + ".\n")
        self._output_file.write("Input file read.\n\n\n")
        return (list_of_subgroups, list_of_bitarrays_of_positives, list_of_bitarrays_of_negatives)

    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """Main method to run the GMSL algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported.
        
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'DataFrame'.")
        # Get the dataset size (number of instances).
        number_of_dataset_instances = len(pandas_dataframe)
        if number_of_dataset_instances == 0:
            raise ValueError("The number of instances of 'pandas_dataframe' is not greater than 0.")
        if type(target) is not tuple:
            raise TypeError("The type of the parameter 'target' must be 'tuple'.")
        # IMPORTANT: this algorithm only supports nominal attributes (i.e., type 'str').
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise DatasetAttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
        # Check the values from the target attribute and get a mask.
        mask = (pandas_dataframe[target[0]] == target[1])
        # Create a list with empty subgroup lists.
        sl_list = []
        for _ in range(self._max_sl):
            sl_list.append(SubgroupList(bitarray(mask.tolist(), endian = "big"), bitarray((~mask).tolist(), endian = "big"), number_of_dataset_instances))
        # Open the output file.
        self._output_file = open(self._output_file_path, "w")
        # Write some dataset info in the output file.
        self._output_file.write("Dataset information:\n")
        self._output_file.write("\t- Number of instances: " + str(number_of_dataset_instances) + ".\n")
        self._output_file.write("\t- Number of positive instances: " + str(sum(mask)) + ".\n")
        self._output_file.write("\t- Number of negative instances: " + str(len(mask) - sum(mask)) + ".\n")
        self._output_file.write("\t- Total number of attributes (including the target): " + str(len(pandas_dataframe.columns)) + ".\n\n\n")
        # Load the candidates from the input file.
        subgroups, bitarrays_of_positives, bitarrays_of_negatives = self._load_candidates(number_of_dataset_instances)
        # Iterate through the subgroup lists.
        for current_sl in sl_list:
            # We use the empty subgroup only to be able to enter to the loop the first time, becase Python does not have do-while statement.
            best_subgroup = Subgroup(Pattern([]), Selector("", Operator.EQUAL, ""))
            # While it is possible to add a new candidate to the subgroups list.
            while (best_subgroup is not None):
                # Initially, there is not best candidate.
                best_subgroup = None
                best_subgroup_comp_gain = 0.0
                best_subgroup_index = -1
                # Iterate through the candidates.
                for current_index in range(len(subgroups)):
                    current_subgroup = subgroups[current_index]
                    # IMPORTANT: we replace a candidate by None, but not delete it from the list.
                    # We do this to reduce the execution time, because when deleting an element from a python list, the rest to its right are shift to the left.
                    # This means that a candidate from the list could be None.
                    if current_subgroup is not None:
                        current_bitarray_of_positives = bitarrays_of_positives[current_index]
                        current_bitarray_of_negatives = bitarrays_of_negatives[current_index]
                        delta_model_candidate = GMSL._compute_delta_model_candidate(pandas_dataframe, current_sl, current_subgroup)
                        delta_data_model_candidate, candidate_number_of_rows = GMSL._compute_delta_data_model_candidate(pandas_dataframe, current_sl, current_subgroup, current_bitarray_of_positives, current_bitarray_of_negatives)
                        if candidate_number_of_rows == 0:
                            current_subgroup_compression_gain = 0.0
                        else:
                            current_subgroup_compression_gain = (delta_model_candidate+delta_data_model_candidate) / (candidate_number_of_rows**self._beta)
                        if current_subgroup_compression_gain > best_subgroup_comp_gain:
                            best_subgroup = current_subgroup
                            best_subgroup_comp_gain = current_subgroup_compression_gain
                            best_subgroup_index = current_index
                if best_subgroup is not None:
                    # Add the best subgroup candidate to the model.
                    current_sl.add_subgroup(best_subgroup, bitarrays_of_positives[best_subgroup_index], bitarrays_of_negatives[best_subgroup_index])
                    # Delete the best subgroup candidate.
                    subgroups[best_subgroup_index] = None
                    bitarrays_of_positives[best_subgroup_index] = None
                    bitarrays_of_negatives[best_subgroup_index] = None
                    # Delete all refinements of the best subgroup candidate.
                    for deletion_index in range(len(subgroups)):
                        if (subgroups[deletion_index] is not None) and (best_subgroup.is_refinement(subgroups[deletion_index], refinement_of_itself=False)): # refinement_of_itself=False -> in this case, the value does not matter, since the original subgroup was already deleted (i.e., both subgroups will not be equals).
                            subgroups[deletion_index] = None
                            bitarrays_of_positives[deletion_index] = None
                            bitarrays_of_negatives[deletion_index] = None
            self._handle_individual_result(current_sl)
        # Close the output file.
        self._output_file.close()
