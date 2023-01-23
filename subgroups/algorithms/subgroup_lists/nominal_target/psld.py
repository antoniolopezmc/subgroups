# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the PSLD algorithm.
"""

from subgroups.algorithms.subgroup_lists.nominal_target.gmsl import GMSL
from subgroups.data_structures import SubgroupList
from pandas import DataFrame
from subgroups.utils.mdl import log2_multinomial_with_recurrence
from numpy import log2
from subgroups.core import Operator, Selector, Pattern, Subgroup
from bitarray import bitarray
from pandas.api.types import is_string_dtype
from subgroups.exceptions import DatasetAttributeTypeError

class PSLD(GMSL):
    """This class represents the PSLD algorithm.
    
    :param input_file_path: path of the file from which the subgroups and their bitarrays will be read.
    :param max_sl: maximum number of subgroups lists to generate.
    :param sl_max_size: maximum number of subgroups that each subgroup list will contain.
    :param beta: level of normalization of the compression gain.
    :param output_file_path: path of the file in which the results will be written.
    """
    
    __slots__ = ("_sl_max_size")
    
    def __init__(self, input_file_path : str, max_sl : int, sl_max_size : int, beta : float, output_file_path : str) -> None:
        if type(sl_max_size) is not int:
            raise TypeError("The type of the parameter 'sl_max_size' must be 'int'.")
        if (sl_max_size <= 0):
            raise ValueError("The parameter 'sl_max_size' is not greater than 0.")
        super().__init__(input_file_path, max_sl, beta, output_file_path)
        self._sl_max_size = sl_max_size
    
    def _get_sl_max_size(self) -> int:
        return self._sl_max_size
    
    sl_max_size = property(_get_sl_max_size, None, None, "Maximum number of subgroups that each subgroup list will contain.")
    
    @staticmethod
    def _compute_delta_data_model_candidate(pandas_dataframe : DataFrame, subgroup_list : SubgroupList, subgroup : Subgroup, subgroup_bitarray_of_positives : bitarray, subgroup_bitarray_of_negatives : bitarray) -> tuple[float, int, int]:
        """Private static method to compute the compression gain considering the data, the model and the candidate.
        
        :param pandas_dataframe: the DataFrame from which the subgroups were extracted.
        :param subgroup_list: subgroup list model. IMPORTANT: the model is not modified after the execution of this method.
        :param subgroup: individual subgroup candidate which is added to the model.
        :param bitarray_of_positives: the bitarray of the dataset instances (considering the complete dataset) which are covered by the subgroup description and by the subgroup target.
        :param bitarray_of_negatives: the bitarray of the dataset instances (considering the complete dataset) which are covered by the subgroup description, but not by the subgroup target.
        :return: a 3-tuple with (1) the compression gain considering the data, the model and the candidate; (2) the number of positive instances covered by the candidate (considering its position in the subgroup list); and (3) the number of negative instances covered by the candidate (considering its position in the subgroup list).
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
        return (defrule_before_candidate - defrule_after_candidate - candidate_value, candidate_number_of_positives, candidate_number_of_negatives)
    
    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """Main method to run the PSLD algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported.
        
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
            # We use the empty subgroup only to be able to enter to the loop the first time, because Python does not have do-while statement.
            best_subgroup = Subgroup(Pattern([]), Selector("", Operator.EQUAL, ""))
            # While it is possible to add a new candidate to the subgroups list AND subgroup list size is less than the maximum permitted.
            while (best_subgroup is not None) and (len(current_sl) < self.sl_max_size):
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
                        delta_data_model_candidate, candidate_number_of_positives, candidate_number_of_negatives = PSLD._compute_delta_data_model_candidate(pandas_dataframe, current_sl, current_subgroup, current_bitarray_of_positives, current_bitarray_of_negatives)
                        candidate_number_of_rows = candidate_number_of_positives + candidate_number_of_negatives
                        if candidate_number_of_rows == 0:
                            current_subgroup_compression_gain = 0.0
                        else:
                            delta_model_candidate = PSLD._compute_delta_model_candidate(pandas_dataframe, current_sl, current_subgroup)
                            current_subgroup_compression_gain = (delta_model_candidate+delta_data_model_candidate) / (candidate_number_of_rows**self._beta)
                        if (current_subgroup_compression_gain > best_subgroup_comp_gain) and (candidate_number_of_positives > 0):
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
                        # refinement_of_itself=False -> in this case, the value does not matter, since the original subgroup was already deleted (i.e., both subgroups will not be equals).
                        if (subgroups[deletion_index] is not None) and ( (best_subgroup.is_refinement(subgroups[deletion_index], refinement_of_itself=False)) or (subgroups[deletion_index].is_refinement(best_subgroup, refinement_of_itself=False)) ):
                            subgroups[deletion_index] = None
                            bitarrays_of_positives[deletion_index] = None
                            bitarrays_of_negatives[deletion_index] = None
            self._handle_individual_result(current_sl)
        # Close the output file.
        self._output_file.close()
