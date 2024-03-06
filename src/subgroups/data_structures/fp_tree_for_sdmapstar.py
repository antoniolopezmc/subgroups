# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the FPTree data structure used in the SDMapStar algorithm.
"""

from subgroups.data_structures.fp_tree_node import FPTreeNode
from subgroups.core.selector import Selector
from subgroups.core.operator import Operator
from pandas import DataFrame
from numpy import size, sum
from subgroups.exceptions import InconsistentMethodParametersError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.quality_measures.quality_measure import QualityMeasure

# Python annotations.
from typing import Union

class FPTreeForSDMapStar(FPTreeForSDMap):
    """This class represents the FPTree data structure used in the SDMapStar algorithm.
    """

    __slots__ = ("_TP", "_FP")

    def __init__(self,TP:int,FP:int) -> None:
        """Method to initialize the FPTreeForSDMapStar
        :param TP: The number of true positives in the dataset.
        :param FP: The number of false positives in the dataset.
        """
        super().__init__()
        if (type(TP) is not int ):
            raise TypeError("The TP parameter must be an integer.")
        if (type(FP) is not int ):
            raise TypeError("The FP parameter must be an integer.")
        self._TP = TP
        self._FP = FP

    def generate_conditional_fp_tree_star(self, list_of_selectors: list[Selector], min_optimistic_estimate:int, optimistic_estimate : QualityMeasure , additional_parameters : dict = dict() , minimum_tp: Union[int, None] = None, minimum_fp: Union[int, None] = None, minimum_n: Union[int, None] = None, ) -> tuple['FPTreeForSDMapStar',int]:
        """Method to get the conditional FPTree with a list of selectors. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
        
        :param list_of_selectors: the list of selectors which is used. IMPORTANT: we assume that the list of selectors only contains selectors.
        :param min_optimistic_estimate: the minimum optimistic estimate threshold.
        :param optimistic_estimate: the optimistic estimate quality measure.
        :param additional_parameters: the additional parameters for the optimistic estimate quality measure.
        :param minimum_tp: the minimum true positives (tp) threshold.
        :param minimum_fp: the minimum false positives (fp) threshold.
        :param minimum_n: the minimum subgroup description size (n) threshold.
        :return: the generated conditional FPTree and the number of pruned branches.
        """
        if type(list_of_selectors) is not list:
            raise TypeError("The type of the parameter 'list_of_selectors' must be 'list'.")
        if (type(minimum_tp) is not int) and (minimum_tp is not None):
            raise TypeError("The type of the parameter 'minimum_tp' must be 'int' or 'NoneType'.")
        if (type(minimum_fp) is not int) and (minimum_fp is not None):
            raise TypeError("The type of the parameter 'minimum_fp' must be 'int' or 'NoneType'.")
        if (type(minimum_n) is not int) and (minimum_n is not None):
            raise TypeError("The type of the parameter 'minimum_n' must be 'int' or 'NoneType'.")
        # Depending on the values of the parameters 'minimum_tp', 'minimum_fp' and 'minimum_n' ...
        if (minimum_tp is not None) and (minimum_fp is not None) and (minimum_n is None):
            use_tp_and_fp = True
        elif (minimum_tp is None) and (minimum_fp is None) and (minimum_n is not None):
            use_tp_and_fp = False
        else:
            raise InconsistentMethodParametersError("If 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.")
        # We only use the first selector in the list in the creation process (the selector at the left side).
        first_selector = list_of_selectors[0]
        # We initialize the final result.
        final_conditional_fp_tree = FPTreeForSDMapStar(self._TP,self._FP)
        ### 1. Generate the conditional pattern base and a dict of frequent selectors with their selectors. ###
        conditional_pattern_base = [] # list[list[ element 1 -> list[Selector], element 2 -> int, element 3 -> int ]]
        # If the first selector is not in the header table, return the current conditional FPTree.
        if first_selector not in self._header_table:
            return final_conditional_fp_tree
        # Dictionary with all the frequent selectors (before pruning).
        dict_of_all_frequent_selectors = dict() # dict[str, tuple[Selector, list[int], int]]
        # Get the first node in the corresponding horizontal list.
        current_node_in_the_horizontal_list = self._header_table[first_selector][1]
        # Iterate through the horizontal list.
        insertion_order = 0 # The insertion order is necessary later in order to sort the elements which have the same 'n' in a same path.
        pruned_branches = 0
        while(current_node_in_the_horizontal_list is not None):
            # SDMapStar pruning. We only use the nodes which have an optimistic estimate greater than the minimum optimistic estimate threshold.
            # Calculate the optimistic estimate.
            current_node_tp = current_node_in_the_horizontal_list.counters[0]
            current_node_fp = current_node_in_the_horizontal_list.counters[1]
            dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : current_node_tp, QualityMeasure.FALSE_POSITIVES : current_node_fp, QualityMeasure.TRUE_POPULATION : self._TP, QualityMeasure.FALSE_POPULATION : self._FP}
            dict_of_parameters.update(additional_parameters)
            oe = optimistic_estimate.compute(dict_of_parameters)
            if oe < min_optimistic_estimate:
                current_node_in_the_horizontal_list = current_node_in_the_horizontal_list._node_link
                pruned_branches = pruned_branches + 1 # We increase the number of pruned branches.
                continue
            # Path from the root node to to the current node in the corresponding horizontal list.
            current_path = []
            # Go up in the tree until the root node.
            current_node_in_the_path = current_node_in_the_horizontal_list._parent # We start from the parent.
            while (current_node_in_the_path != self._root_node):
                current_selector = current_node_in_the_path._selector
                # Add the selector to 'dict_of_all_frequent_selectors'.
                # IMPORTANT: the true positives tp and the false positives fp of all the nodes in the path are those of the current node in the horizontal list.
                try:
                    dict_of_all_frequent_selectors[current_selector.attribute_name+repr(current_selector.value)][1][0] = \
                        dict_of_all_frequent_selectors[current_selector.attribute_name+repr(current_selector.value)][1][0] + current_node_in_the_horizontal_list._counters[0]
                    dict_of_all_frequent_selectors[current_selector.attribute_name+repr(current_selector.value)][1][1] = \
                        dict_of_all_frequent_selectors[current_selector.attribute_name+repr(current_selector.value)][1][1] + current_node_in_the_horizontal_list._counters[1]
                except KeyError: # Try to access to the entry and if it does not exist, create a new one.
                    dict_of_all_frequent_selectors[current_selector.attribute_name+repr(current_selector.value)] = \
                        (current_selector, [current_node_in_the_horizontal_list._counters[0], current_node_in_the_horizontal_list._counters[1]], insertion_order)
                    insertion_order = insertion_order - 1 # IMPORTANT: in this case, the insertion order decreases (we use negative numbers) because, when we create the conditional pattern base, we iterate from the bottom to the top in the FPTree.
                # Insert the selector at the beginning of the current path.
                current_path.insert(0, current_selector)
                # Go up.
                current_node_in_the_path = current_node_in_the_path._parent
            # If the path is not empty.
            if current_path:
                # Append to 'conditional_pattern_base'.
                conditional_pattern_base.append( [ current_path, current_node_in_the_horizontal_list._counters[0], current_node_in_the_horizontal_list._counters[1] ] )
            # Finally, go the the next node in the horizontal list.
            current_node_in_the_horizontal_list = current_node_in_the_horizontal_list._node_link
        ### 2. Prune the dict of frequent selectors (depending on the values of the parameters 'minimum_tp', 'minimum_fp' and 'minimum_n'). ###
        dict_of_frequent_selectors = dict() # dict[str, tuple[Selector, list[int], int]]
        if use_tp_and_fp:
            for key in dict_of_all_frequent_selectors:
                if (dict_of_all_frequent_selectors[key][1][0] >= minimum_tp) and (dict_of_all_frequent_selectors[key][1][1] >= minimum_fp):
                    dict_of_frequent_selectors[key] = (dict_of_all_frequent_selectors[key][0], [dict_of_all_frequent_selectors[key][1][0], dict_of_all_frequent_selectors[key][1][1]], dict_of_all_frequent_selectors[key][2])
        else:
            for key in dict_of_all_frequent_selectors:
                if ( (dict_of_all_frequent_selectors[key][1][0]+dict_of_all_frequent_selectors[key][1][1]) >= minimum_n):
                    dict_of_frequent_selectors[key] = (dict_of_all_frequent_selectors[key][0], [dict_of_all_frequent_selectors[key][1][0], dict_of_all_frequent_selectors[key][1][1]], dict_of_all_frequent_selectors[key][2]) 
        ### 3. Insert all the paths of the conditional pattern base in the tree. ###
        for elem in conditional_pattern_base:
            path = elem[0]
            tp = elem[1]
            fp = elem[2]
            valid_selectors_in_this_path = [] # Only the valid selectors after pruning.
            # Iterate through the selectors in the path.
            for selector in path:
                # Add the selector to 'valid_selectors_in_this_path'.
                # ===> IMPORTANT: the selector might not exist because it was pruned. In this case, a KeyError exception is raised.
                try:
                    # IMPORTANT: we use 'repr' in order to add simple quotes to the values of type str, but not to the values of numeric types.
                    valid_selectors_in_this_path.append( dict_of_frequent_selectors[selector.attribute_name+repr(selector.value)][0] )
                except KeyError:
                    pass # If the exception is raised, we do nothing.
            # We sort 'valid_selectors_in_this_path' according to the value of 'n' (tp+fp) in the set of frequent selectors (CRITERION EXTRACTED FROM VIKAMINE).
            # - In case of tie, we NEED TO MAINTAIN the order of the selectors according to the order in the set of frequent selectors. For this reason, it is necessary to sort twice.
            # IMPORTANT: we use 'repr' in order to add simple quotes to the values of type str, but not to the values of numeric types.
            valid_selectors_in_this_path = sorted(valid_selectors_in_this_path, key = lambda x : dict_of_frequent_selectors[x.attribute_name+repr(x.value)][2], reverse=False) # key -> [2] : the insertion order in the dictionary.
            valid_selectors_in_this_path = sorted(valid_selectors_in_this_path, key = lambda x : (dict_of_frequent_selectors[x.attribute_name+repr(x.value)][1][0]+dict_of_frequent_selectors[x.attribute_name+repr(x.value)][1][1]), reverse=True) # key -> 'n' : sum of tp and fp.
            # Insert.
            final_conditional_fp_tree._insert_in_conditional_fp_tree(valid_selectors_in_this_path, final_conditional_fp_tree._root_node, tp, fp)
        # Finally, we create the sorted header table.
        final_conditional_fp_tree._sorted_header_table = []
        for key in final_conditional_fp_tree._header_table:
            final_conditional_fp_tree._sorted_header_table.append( key )
        # IMPORTANT: THIS CRITERION HAS BEEN EXTRACTED FROM THE ORIGINAL IMPLEMENTATION OF THE SDMAP ALGORITHM (IN VIKAMINE).
        # We have to sort the selectors according to the summation of 'n' (i.e., summation of tp + summation of fp).
        # - In case of tie, we maintain the insertion order in the dictionary 'header_table'.
        final_conditional_fp_tree._sorted_header_table.sort(reverse=False, key=lambda x : (final_conditional_fp_tree._header_table[x][0][0] + final_conditional_fp_tree._header_table[x][0][1])) # Ascending order.
        # Return the final conditional FPTree.
        return final_conditional_fp_tree, pruned_branches
