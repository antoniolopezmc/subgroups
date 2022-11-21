# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the PWSLM algorithm.
"""

from subgroups.algorithms.subgroup_lists.nominal_target.psld import PSLD
from subgroups.data_structures import SubgroupList
from pandas import DataFrame
from subgroups.core import Operator, Selector, Pattern, Subgroup
from bitarray import bitarray
from pandas.api.types import is_string_dtype
from subgroups.exceptions import DatasetAttributeTypeError

class PWSLM(PSLD):
    """This class represents the PWSLM algorithm.
    
    :param input_file_path: path of the file from which the subgroups and their bitarrays will be read.
    :param max_sl: maximum number of subgroups lists to generate.
    :param sl_max_size: maximum number of subgroups that each subgroup list will contain.
    :param beta: level of normalization of the compression gain.
    :param maximum_positive_overlap: maximum positive overlap factor permitted to add a subgroup candidate to the subgroup list (i.e., a subgroup candidate will be added to the subgroup list only if its positive overlap factor is less or equal than maximum_positive_overlap). Values close to 0 are stricter and allow candidates with less overlap, while values close to 1 allow candidates with more overlap.
    :param maximum_negative_overlap: maximum negative overlap factor permitted to add a subgroup candidate to the subgroup list (i.e., a subgroup candidate will be added to the subgroup list only if its negative overlap factor is less or equal than maximum_negative_overlap). Values close to 0 are stricter and allow candidates with less overlap, while values close to 1 allow candidates with more overlap.
    :param output_file_path: path of the file in which the results will be written.
    """
    
    __slots__ = ("_maximum_positive_overlap", "_maximum_negative_overlap")
    
    def __init__(self, input_file_path : str, max_sl : int, sl_max_size : int, beta : float, maximum_positive_overlap : float, maximum_negative_overlap : float, output_file_path : str) -> None:
        if type(maximum_positive_overlap) is not float:
            raise TypeError("The type of the parameter 'maximum_positive_overlap' must be 'float'.")
        if type(maximum_negative_overlap) is not float:
            raise TypeError("The type of the parameter 'maximum_negative_overlap' must be 'float'.")
        super().__init__(input_file_path, max_sl, sl_max_size, beta, output_file_path)
        self._maximum_positive_overlap = maximum_positive_overlap
        self._maximum_negative_overlap = maximum_negative_overlap
    
    def _get_maximum_positive_overlap(self) -> float:
        return self._maximum_positive_overlap
    
    def _get_maximum_negative_overlap(self) -> float:
        return self._maximum_negative_overlap
    
    maximum_positive_overlap = property(_get_maximum_positive_overlap, None, None, "Maximum positive overlap factor permitted to add a subgroup candidate to the subgroup list (i.e., a subgroup candidate will be added to the subgroup list only if its positive overlap factor is less or equal than maximum_positive_overlap). Values close to 0 are stricter and allow candidates with less overlap, while values close to 1 allow candidates with more overlap.")
    maximum_negative_overlap = property(_get_maximum_negative_overlap, None, None, "Maximum negative overlap factor permitted to add a subgroup candidate to the subgroup list (i.e., a subgroup candidate will be added to the subgroup list only if its negative overlap factor is less or equal than maximum_negative_overlap). Values close to 0 are stricter and allow candidates with less overlap, while values close to 1 allow candidates with more overlap.")
    
    @staticmethod
    def _compute_positive_overlap_factor(subgroup : Subgroup, bitarray_of_positives : bitarray, positive_counter_of_subgroups : list) -> float:
        """Private static method to compute the positive overlap factor of a subgroup. This factor indicates how much the subgroup overlaps (considering only the positive instances) with the previous subgroups (again, considering only the positive instances) in a subgroup list (represented by positive_counter_of_subgroups). Values close to 0 indicate low overlap, while values close 1 indicates high overlap.
        
        :param subgroup: individual subgroup candidate which is evaluated.
        :param bitarray_of_positives: the positive bitarray (i.e., instances covered by the description and the target) of the subgroup, considering it individually (i.e., with respect to the complete dataset).
        :param positive_counter_of_subgroups: the number of subgroups that cover each positive instance (starting with 1). In this case, negative instances always have the initial value.
        :return: the positive overlap factor of the subgroup.
        """
        # IMPORTANT: if the subgroup does not cover any positive instance, we consider that the overlap value is 1 (i.e., the maximum possible value).
        # - This is because subgroups that do not cover positive instances are useless for us.
        if (bitarray_of_positives.count(1) == 0):
            return 1.0
        total_sum = 0
        subgroup_sum = 0
        for index in range(len(positive_counter_of_subgroups)):
            current_counter_value = positive_counter_of_subgroups[index]
            total_sum = total_sum + current_counter_value
            if bitarray_of_positives[index]:
                subgroup_sum = subgroup_sum + current_counter_value
        if total_sum == 0:
            return 0.0
        return subgroup_sum/total_sum
    
    @staticmethod
    def _compute_negative_overlap_factor(subgroup : Subgroup, bitarray_of_negatives : bitarray, negative_counter_of_subgroups : list) -> float:
        """Private static method to compute the negative overlap factor of a subgroup. This factor indicates how much the subgroup overlaps (considering only the negative instances) with the previous subgroups (again, considering only the negative instances) in a subgroup list (represented by negative_counter_of_subgroups). Values close to 0 indicate low overlap, while values close 1 indicates high overlap.
        
        :param subgroup: individual subgroup candidate which is evaluated.
        :param bitarray_of_negatives: the negative bitarray (i.e., instances covered by the description, but not by the target) of the subgroup, considering it individually (i.e., with respect to the complete dataset).
        :param negative_counter_of_subgroups: the number of subgroups that cover each negative instance (starting with 1). In this case, positive instances always have the initial value.
        :return: the negative overlap factor of the subgroup.
        """
        # IMPORTANT: if the subgroup does not cover any negative instance, we consider that the overlap value is 0 (i.e., the minimum possible value).
        # - This is because we do not care if subgroups do not cover negative instances.
        if (bitarray_of_negatives.count(1) == 0):
            return 0.0
        total_sum = 0
        subgroup_sum = 0
        for index in range(len(negative_counter_of_subgroups)):
            current_counter_value = negative_counter_of_subgroups[index]
            total_sum = total_sum + current_counter_value
            if bitarray_of_negatives[index]:
                subgroup_sum = subgroup_sum + current_counter_value
        if total_sum == 0:
            return 0.0
        return subgroup_sum/total_sum
    
    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """Main method to run the PWSLM algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported.
        
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
            # Positive counter of subgroups (i.e., the number of subgroups that cover each positive instance).
            # - The list is initialized with 0s.
            positive_counter_of_subgroups = [0] * number_of_dataset_instances
            # Negative counter of subgroups (i.e., the number of subgroups that cover each negative instance).
            # - The list is initialized with 0s
            negative_counter_of_subgroups = [0] * number_of_dataset_instances
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
                        delta_data_model_candidate, candidate_number_of_positives, candidate_number_of_negatives = PWSLM._compute_delta_data_model_candidate(pandas_dataframe, current_sl, current_subgroup, current_bitarray_of_positives, current_bitarray_of_negatives)
                        candidate_number_of_rows = candidate_number_of_positives + candidate_number_of_negatives
                        if candidate_number_of_rows == 0:
                            current_subgroup_compression_gain = 0.0
                            current_subgroup_positive_overlap_factor = 1.0
                            current_subgroup_negative_overlap_factor = 1.0
                        else:
                            delta_model_candidate = PWSLM._compute_delta_model_candidate(pandas_dataframe, current_sl, current_subgroup)
                            current_subgroup_positive_overlap_factor = PWSLM._compute_positive_overlap_factor(current_subgroup, current_bitarray_of_positives, positive_counter_of_subgroups)
                            current_subgroup_negative_overlap_factor = PWSLM._compute_negative_overlap_factor(current_subgroup, current_bitarray_of_negatives, negative_counter_of_subgroups)
                            ############################################
                            # EXTREMELY IMPORTANT: "1 - ", because we want to penalize the most overlapping subgroups (i.e., the more overlapping, the value closer to 0).
                            ############################################
                            current_subgroup_compression_gain = ( (delta_model_candidate+delta_data_model_candidate) / (candidate_number_of_rows**self._beta) ) * (1.0 - current_subgroup_positive_overlap_factor) * (1.0 - current_subgroup_negative_overlap_factor)
                        if (current_subgroup_compression_gain > best_subgroup_comp_gain) and (candidate_number_of_positives > 0) and (current_subgroup_positive_overlap_factor <= self.maximum_positive_overlap) and (current_subgroup_negative_overlap_factor <= self.maximum_negative_overlap):
                            best_subgroup = current_subgroup
                            best_subgroup_comp_gain = current_subgroup_compression_gain
                            best_subgroup_index = current_index
                if best_subgroup is not None:
                    # Update 'positive_counter_of_subgroups' and 'negative_counter_of_subgroups' according to best_candidate.
                    for index in range(number_of_dataset_instances):
                        if bitarrays_of_positives[best_subgroup_index][index]:
                            positive_counter_of_subgroups[index] = positive_counter_of_subgroups[index] + 1
                        if bitarrays_of_negatives[best_subgroup_index][index]:
                            negative_counter_of_subgroups[index] = negative_counter_of_subgroups[index] + 1
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