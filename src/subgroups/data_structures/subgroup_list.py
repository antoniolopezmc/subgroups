# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the Subgroup List data structure.
"""

from bitarray import bitarray
from subgroups.core.subgroup import Subgroup

class SubgroupList(object):
    """This class represents a Subgroup List.
    
    :param bitarray_of_positives: the bitarray of the dataset instances which are covered by the target (its length must be equal to the number of instances of the dataset).
    :param bitarray_of_negatives: the bitarray of the dataset instances which are not covered by the target (its length must be equal to the number of instances of the dataset).
    :param number_of_dataset_instances: number of instances of the dataset.
    """

    __slots__ = ("_default_rule_bitarray_of_positives", "_default_rule_bitarray_of_negatives", "_dataset_target_distribution", "_list_of_subgroups", "_subgroups_bitarrays_of_positives", "_subgroups_bitarrays_of_negatives", "_subgroups_original_bitarrays_of_positives", "_subgroups_original_bitarrays_of_negatives")

    def __init__(self, dataset_target_bitarray_of_positives : bitarray, dataset_target_bitarray_of_negatives : bitarray, number_of_dataset_instances : int) -> None:
        if type(dataset_target_bitarray_of_positives) is not bitarray:
            raise TypeError("The type of the parameter 'dataset_target_bitarray_of_positives' must be 'bitarray'.")
        if type(dataset_target_bitarray_of_negatives) is not bitarray:
            raise TypeError("The type of the parameter 'dataset_target_bitarray_of_negatives' must be 'bitarray'.")
        if type(number_of_dataset_instances) is not int:
            raise TypeError("The type of the parameter 'number_of_dataset_instances' must be 'int'.")
        if number_of_dataset_instances != len(dataset_target_bitarray_of_positives):
            raise ValueError("The length of 'dataset_target_bitarray_of_positives' is not equal to 'number_of_dataset_instances'.")
        if number_of_dataset_instances != len(dataset_target_bitarray_of_negatives):
            raise ValueError("The length of 'dataset_target_bitarray_of_negatives' is not equal to 'number_of_dataset_instances'.")
        # Default rule.
        self._default_rule_bitarray_of_positives = dataset_target_bitarray_of_positives.copy() # We make a copy to avoid aliasing.
        self._default_rule_bitarray_of_negatives = dataset_target_bitarray_of_negatives.copy() # We make a copy to avoid aliasing.
        # Target distribution considering the complete dataset.
        # -> (number of positive instances, total number of instances)
        self._dataset_target_distribution = (dataset_target_bitarray_of_positives.count(1), number_of_dataset_instances)
        # List of individual subgroups.
        self._list_of_subgroups = []
        # Lists of bitarrays considering the position of the subgroup in the list.
        self._subgroups_bitarrays_of_positives = []
        self._subgroups_bitarrays_of_negatives = []
        # Lists of bitarrays considering the subgroup individually (i.e., with respect to the complete dataset).
        self._subgroups_original_bitarrays_of_positives = []
        self._subgroups_original_bitarrays_of_negatives = []

    def _get_default_rule_bitarray_of_positives(self) -> bitarray:
        return self._default_rule_bitarray_of_positives

    def _get_default_rule_bitarray_of_negatives(self) -> bitarray:
        return self._default_rule_bitarray_of_negatives

    def _get_dataset_target_distribution(self) -> float:
        return self._dataset_target_distribution[0] / self._dataset_target_distribution[1]

    def _get_dataset_number_of_positives(self) -> int:
        return self._dataset_target_distribution[0]

    def _get_dataset_number_of_negatives(self) -> int:
        return self._dataset_target_distribution[1] - self._dataset_target_distribution[0]

    def _get_number_of_dataset_instances(self) -> int:
        return self._dataset_target_distribution[1]

    default_rule_bitarray_of_positives = property(_get_default_rule_bitarray_of_positives, None, None, "The bitarray of the dataset instances which are covered by the target.")
    default_rule_bitarray_of_negatives = property(_get_default_rule_bitarray_of_negatives, None, None, "The bitarray of the dataset instances which are not covered by the target.")
    dataset_target_distribution = property(_get_dataset_target_distribution, None, None, "Target distribution considering the complete dataset.")
    dataset_number_of_positives = property(_get_dataset_number_of_positives, None, None, "Number of instances (considering the complete dataset) which are covered by the target.")
    dataset_number_of_negatives = property(_get_dataset_number_of_negatives, None, None, "Number of instances (considering the complete dataset) which are not covered by the target.")
    number_of_dataset_instances = property(_get_number_of_dataset_instances, None, None, "Number of instances of the dataset.")

    def is_empty(self) -> bool:
        return (len(self._list_of_subgroups) == 0)

    def add_subgroup(self, subgroup : Subgroup, bitarray_of_positives : bitarray, bitarray_of_negatives : bitarray) -> None:
        """Method to add an individual subgroup at the end of the subgroup list (and before the default rule).
        
        :param subgroup: subgroup which is added.
        :param bitarray_of_positives: the bitarray of the dataset instances (considering the complete dataset) which are covered by the subgroup description and by the subgroup target.
        :param bitarray_of_negatives: the bitarray of the dataset instances (considering the complete dataset) which are covered by the subgroup description, but not by the subgroup target.
        """
        if not isinstance(subgroup, Subgroup):
            raise TypeError("The type of the parameter 'subgroup' must be 'Subgroup'.")
        if type(bitarray_of_positives) is not bitarray:
            raise TypeError("The type of the parameter 'bitarray_of_positives' must be 'bitarray'.")
        if type(bitarray_of_negatives) is not bitarray:
            raise TypeError("The type of the parameter 'bitarray_of_negatives' must be 'bitarray'.")
        if self.number_of_dataset_instances != len(bitarray_of_positives):
            raise ValueError("The length of 'bitarray_of_positives' is not equal to the dataset size.")
        if self.number_of_dataset_instances != len(bitarray_of_negatives):
            raise ValueError("The length of 'bitarray_of_negatives' is not equal to the dataset size.")
        # First, we make a copy of both bitarrays to avoid aliasing and store these bitarrays.
        self._subgroups_original_bitarrays_of_positives.append(bitarray_of_positives.copy())
        self._subgroups_original_bitarrays_of_negatives.append(bitarray_of_negatives.copy())
        # Next, we make again a copy of both bitarrays to avoid aliasing.
        bitarray_of_positives_copy = bitarray_of_positives.copy()
        bitarray_of_negatives_copy = bitarray_of_negatives.copy()
        ## IMPORTANT: the bitsets passed by parameters consider the complete dataset.
        ##   - However, when adding a new subgroup, we only have to consider the rows that are not covered yet.
        ##   - Moreover, the rows covered by the default rule also change (we have to delete the rows covered by the new subgroup added).
        # Transform the initial bitsets (i.e., to consider only the rows that are not covered yet). For this, we use an AND operation.
        bitarray_of_positives_copy &= self._default_rule_bitarray_of_positives # Inplace operation (modify the current bitset, instead of creating a new one).
        bitarray_of_negatives_copy &= self._default_rule_bitarray_of_negatives # Inplace operation (modify the current bitset, instead of creating a new one).
        # Update the default rule (after adding the new subgroup, it covers less rows).
        self._default_rule_bitarray_of_positives &= (~bitarray_of_positives_copy)
        self._default_rule_bitarray_of_negatives &= (~bitarray_of_negatives_copy)
        # Finally, we add the subgroup and the bitsets to the subgroup list.
        self._list_of_subgroups.append(subgroup.copy()) # We make a copy to avoid aliasing.
        self._subgroups_bitarrays_of_positives.append(bitarray_of_positives_copy)
        self._subgroups_bitarrays_of_negatives.append(bitarray_of_negatives_copy)

    def delete_last_subgroup(self) -> None:
        """Method to delete the last individual subgroup from the subgroup list. If the subgroup list is empty, this method does nothing.
        """
        if (len(self._list_of_subgroups) > 0):
            # Delete the last element of the 5 lists.
            self._list_of_subgroups.pop()
            subgroup_positives = self._subgroups_bitarrays_of_positives.pop()
            subgroup_negatives = self._subgroups_bitarrays_of_negatives.pop()
            self._subgroups_original_bitarrays_of_positives.pop()
            self._subgroups_original_bitarrays_of_negatives.pop()
            # Update the default rule (after deleting the last subgroup, it covers more rows).
            self._default_rule_bitarray_of_positives |= subgroup_positives
            self._default_rule_bitarray_of_negatives |= subgroup_negatives

    def get_subgroup(self, index : int) -> Subgroup:
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._list_of_subgroups[index]

    def get_subgroup_bitarray_of_positives(self, index : int) -> bitarray:
        """Get the bitarray of positives of the subgroup in the position 'index'. This bitarray depends on the position of the subgroup in the list (i.e., it DOES NOT consider the complete dataset).
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._subgroups_bitarrays_of_positives[index]
    
    def get_subgroup_bitarray_of_negatives(self, index : int) -> bitarray:
        """Get the bitarray of negatives of the subgroup in the position 'index'. This bitarray depends on the position of the subgroup in the list (i.e., it DOES NOT consider the complete dataset).
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._subgroups_bitarrays_of_negatives[index]
    
    def get_subgroup_original_bitarray_of_positives(self, index : int) -> bitarray:
        """Get the original bitarray of positives of the subgroup in the position 'index'. This bitarray considers the subgroup individually (i.e., with respect to the complete dataset).
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._subgroups_original_bitarrays_of_positives[index]
    
    def get_subgroup_original_bitarray_of_negatives(self, index : int) -> bitarray:
        """Get the original bitarray of negatives of the subgroup in the position 'index'. This bitarray considers the subgroup individually (i.e., with respect to the complete dataset).
        """
        if type(index) is not int:
            raise TypeError("The type of the parameter 'index' must be 'int'.")
        return self._subgroups_original_bitarrays_of_negatives[index]
    
    def __len__(self) -> int:
        return len(self._list_of_subgroups)

    def __str__(self) -> str:
        number_of_subgroups = len(self._list_of_subgroups)
        if number_of_subgroups == 1:
            result = "## Subgroup list (1 subgroup) ##\n"
        else:
            result = "## Subgroup list (" + str(number_of_subgroups) + " subgroups) ##\n"
        for index in range(len(self._list_of_subgroups)):
            positive_instances_covered = self._subgroups_bitarrays_of_positives[index].count(1)
            negative_instances_covered = self._subgroups_bitarrays_of_negatives[index].count(1)
            original_positive_instances_covered = self._subgroups_original_bitarrays_of_positives[index].count(1)
            original_negative_instances_covered = self._subgroups_original_bitarrays_of_negatives[index].count(1)
            result = result + "s" + str(index+1) + ": " + str(self._list_of_subgroups[index]) + "\n" + \
                              "\tConsidering its position in the list:\n" + \
                              "\t- positive instances covered: " + str(positive_instances_covered) + "\n" + \
                              "\t- negative instances covered: " + str(negative_instances_covered) + "\n" + \
                              "\t- total instances covered: " + str(positive_instances_covered + negative_instances_covered) + "\n" + \
                              "\tConsidering it individually:\n" + \
                              "\t- positive instances covered: " + str(original_positive_instances_covered) + "\n" + \
                              "\t- negative instances covered: " + str(original_negative_instances_covered) + "\n" + \
                              "\t- total instances covered: " + str(original_positive_instances_covered + original_negative_instances_covered) + "\n"
        positive_instances_covered = self._default_rule_bitarray_of_positives.count(1)
        negative_instances_covered = self._default_rule_bitarray_of_negatives.count(1)
        result = result + "default rule:\n" + \
                          "\tpositive instances covered: " + str(positive_instances_covered) + "\n" + \
                          "\tnegative instances covered: " + str(negative_instances_covered) + "\n" + \
                          "\ttotal instances covered: " + str(positive_instances_covered + negative_instances_covered) + "\n"
        return result
