# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the FPTree data structure used in the SDMap algorithm.
"""

from subgroups.data_structures.fp_tree_node import FPTreeNode
from subgroups.core.selector import Selector
from subgroups.core.operator import Operator
from pandas import DataFrame
from numpy import size, sum
from subgroups.exceptions import InconsistentMethodParametersError

# Python annotations.
from typing import Union, Any

class FPTreeForSDMap(object):
    """This class represents the FPTree data structure used in the SDMap algorithm.
    """
    
    __slots__ = ("_root_node", "_header_table", "_sorted_header_table")
    
    def __init__(self) -> None:
        # The root of the tree. In this case, in each node, we have two counter: the true positives tp of the selector of the node and the false positives fp of the selector of the node.
        self._root_node = FPTreeNode(Selector("None", Operator.EQUAL, "None"), [-1, -1], None)
        # The header table is represented with a python dictionary, in which the key is a selector and the value is a list with 3 elements:
        # - The first element is a list with 2 elements:
        #   * The summation of the true positives tp of all the nodes with that selector.
        #   * The summation of the false positives fp of all the nodes with that selector.
        # - The second element is a FPTreeNode. It is the FIRST FPTreeNode of the horizontal list (the list with all the FPTreeNode with the same selector).
        # - The third element is a FPTreeNode. It is the LAST FPTreeNode of the horizontal list (the list with all the FPTreeNode with the same selector).
        self._header_table = dict()
        # IMPORTANT: THIS CRITERION HAS BEEN EXTRACTED FROM THE ORIGINAL IMPLEMENTATION OF THE SDMAP ALGORITHM (IN VIKAMINE).
        # We have to sort the selectors of the header table according to the summation of 'n' (i.e., summation of tp + summation of fp).
        # - We store them in a list.
        self._sorted_header_table = []
    
    def _get_root_node(self) -> FPTreeNode:
        return self._root_node
    
    def _get_header_table(self) -> dict[Selector, list[Any]]:
        return self._header_table
    
    def _get_sorted_header_table(self) -> list:
        return self._sorted_header_table
    
    root_node = property(_get_root_node, None, None, "The root of the tree.")
    header_table = property(_get_header_table, None, None, "The header table.")
    sorted_header_table = property(_get_sorted_header_table, None, None, "A list with the selectors of the header table sorted according to the summation of the 'n' (summation of the true positives tp + summation of the false positives fp).")
    
    def is_empty(self) -> bool:
        """Method to check whether the FPTree only has the root node.
        
        :return: whether the FPTree only has the root node.
        """
        return (self._root_node.number_of_children == 0)
    
    def there_is_a_single_path(self) -> bool:
        """Method to check whether all internal nodes only have 1 child.
        
        :return: whether all internal nodes only have 1 child.
        """
        # Go down while the current node has only one child.
        current_node = self._root_node
        while (current_node.number_of_children == 1):
            current_node = list(current_node._childs.values())[0] # Get the unique child node.
        # Check the number of children of the current node.
        # - If the number of children is 0, we are at the end of the tree and there is a single path.
        # - If the number of children is greater than 1, there is not a single path.
        return (current_node.number_of_children == 0)
    
    def tree_as_str(self) -> str:
        """Method to print as str the complete FPTree from the root node.
        
        :return: the printed FPTree.
        """
        return self._root_node.tree_as_str(current_depth=0)
    
    def header_table_as_str(self, follow_node_links : bool = True) -> str:
        """Method to print all the entries of the FPTree header table.
        
        :param follow_node_links: whether print all the FPTreeNode ids in the horizontal list or only the first one. By default, True.
        :return: the printed header table.
        """
        if type(follow_node_links) is not bool:
            raise TypeError("The type of the parameter 'follow_node_links' must be 'bool'.")
        result = ""
        for key in self._header_table:
            current_entry = self._header_table[key]
            result = result + "{selector: " + str(key) + ", "
            result = result + "summations: " + str(current_entry[0]) + "} -> " + str(current_entry[1])
            if follow_node_links:
                current_node_in_the_horizontal_list = current_entry[1]
                while (current_node_in_the_horizontal_list is not None):
                    current_node_in_the_horizontal_list = current_node_in_the_horizontal_list.node_link
                    result = result + " -> " + str(current_node_in_the_horizontal_list)
            result = result + "\n"
        return result
    
    # IMPORTANT: in the original implementation of the SDMap algorithm (in Vikamine), they check 'n' (true positives + false positives) in order to prune the frequent selectors. In our implementation, we use two threshold types: (1) the true positives (tp) and the false positives (fp) separately or (2) the subgroup description size (n).
    def generate_set_of_frequent_selectors(self, pandas_dataframe : DataFrame, target : tuple[str, Union[int, float, str]], minimum_tp : Union[int, None] = None, minimum_fp : Union[int, None] = None, minimum_n : Union[int, None] = None) -> dict[str, tuple[Selector, list[int], int]]:
        """Method to scan the pandas DataFrame in order to generate the set of frequent selectors. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None. IMPORTANT: missing values are not supported yet.
        
        :param pandas_dataframe: the DataFrame which is scanned. IMPORTANT: missing values are not supported yet.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :param minimum_tp: the minimum true positives (tp) threshold.
        :param minimum_fp: the minimum false positives (fp) threshold.
        :param minimum_n: the minimum subgroup description size (n) threshold.
        :return: a dictionary in which the keys are strings (the concatenation of the selector attribute name and the selector value) and the values are tuples with 3 elements: (1) the selector, (2) a list with 2 elements: the true positives tp of it and the false positives fp of it, and (3) a number indicating the insertion order in this dictionary (starting from 0).
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'DataFrame'.")
        if type(target) is not tuple:
            raise TypeError("The type of the parameter 'target' must be 'tuple'.")
        if (type(minimum_tp) is not int) and (minimum_tp is not None):
            raise TypeError("The type of the parameter 'minimum_tp' must be 'int' or 'NoneType'.")
        if (type(minimum_fp) is not int) and (minimum_fp is not None):
            raise TypeError("The type of the parameter 'minimum_fp' must be 'int' or 'NoneType'.")
        if (type(minimum_n) is not int) and (minimum_n is not None):
            raise TypeError("The type of the parameter 'minimum_n' must be 'int' or 'NoneType'.")
        # Depending on the values of the parameters 'minimum_tp', 'minimum_fp' and 'minimum_n' ...
        if (minimum_tp is not None) and (minimum_fp is not None) and (minimum_n is None):
            # Get the target column as a mask: True if the value is equal to the target value and False otherwise.
            target_attribute_as_a_mask = (pandas_dataframe[target[0]] == target[1])
            # Result.
            final_dict_of_frequent_selectors = dict()
            # Iterate through the columns (except the target).
            insertion_order = 0 # The insertion order is necessary later in order to sort the elements which have the same 'n' in a same row.
            for column in pandas_dataframe.columns.drop(target[0]):
                current_Series = pandas_dataframe[column]
                # Use the 'groupby' method in order to obtain, for each value, the true positives tp and the false positives fp.
                tp_and_fp_for_each_value = target_attribute_as_a_mask.groupby(current_Series).aggregate([size, sum]) # tp -> sum; fp -> size - sum; n -> size.
                # Filter the results according to 'minimum_tp' and 'minimum_fp'.
                filtered = tp_and_fp_for_each_value[(tp_and_fp_for_each_value["sum"] >= minimum_tp) & ((tp_and_fp_for_each_value["size"] - tp_and_fp_for_each_value["sum"]) >= minimum_fp)]
                # The corresponding values are the indexes of the DataFrame 'filtered'.
                values = filtered.index
                # We create the selectors and we add them to the final dictionary.
                for i in values:
                    # IMPORTANT: we use 'repr' in order to add simple quotes to the values of type str, but not to the values of numeric types.
                    final_dict_of_frequent_selectors[column+repr(i)] = (Selector(column, Operator.EQUAL, i), [ filtered.loc[i,"sum"], (filtered.loc[i,"size"] - filtered.loc[i,"sum"]) ], insertion_order)
                    insertion_order = insertion_order + 1
            # Finally, we return the results.
            return final_dict_of_frequent_selectors
        elif (minimum_tp is None) and (minimum_fp is None) and (minimum_n is not None):
            # Get the target column as a mask: True if the value is equal to the target value and False otherwise.
            target_attribute_as_a_mask = (pandas_dataframe[target[0]] == target[1])
            # Result.
            final_dict_of_frequent_selectors = dict()
            # Iterate through the columns (except the target).
            insertion_order = 0 # The insertion order is necessary later in order to sort the elements which have the same 'n' in a same row.
            for column in pandas_dataframe.columns.drop(target[0]):
                current_Series = pandas_dataframe[column]
                # Use the 'groupby' method in order to obtain, for each value, the true positives tp and the false positives fp.
                tp_and_fp_for_each_value = target_attribute_as_a_mask.groupby(current_Series).aggregate([size, sum]) # tp -> sum; fp -> size - sum; n -> size.
                # Filter the results according to 'minimum_tp' and 'minimum_fp'.
                filtered = tp_and_fp_for_each_value[tp_and_fp_for_each_value["size"] >= minimum_n]
                # The corresponding values are the indexes of the DataFrame 'filtered'.
                values = filtered.index
                # We create the selectors and we add them to the final dictionary.
                for i in values:
                    # IMPORTANT: we use 'repr' in order to add simple quotes to the values of type str, but not to the values of numeric types.
                    final_dict_of_frequent_selectors[column+repr(i)] = (Selector(column, Operator.EQUAL, i), [ filtered.loc[i,"sum"], (filtered.loc[i,"size"] - filtered.loc[i,"sum"]) ], insertion_order)
                    insertion_order = insertion_order + 1
            # Finally, we return the results.
            return final_dict_of_frequent_selectors
        else:
            raise InconsistentMethodParametersError("If 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.")
    
    # IMPORTANT: in the original paper, this method is recursive. In our implementation, the method is iterative.
    def _insert_tree(self, list_of_selectors : list[Selector], parent_node : FPTreeNode, target_match : bool) -> None:
        """Private method to insert a list of selectors from a parent node.
        
        :param list_of_selectors: the list of selectors which is inserted in the tree. IMPORTANT: we assume that the list of selectors only contains selectors.
        :param parent_node: the parent node from which to start the insertion.
        :param target_match: whether we consider that the target attribute match.
        """
        current_parent_node = parent_node
        for selector in list_of_selectors:
            # Get the child node with the current selector or None if it does not exist.
            child_node_with_this_selector = current_parent_node.get_child_by_selector(selector)
            # Check if the node exists or not and if the parameter 'target_match' is True or False.
            if (target_match) and (child_node_with_this_selector is not None):
                # Increase the true positives tp in the node.
                child_node_with_this_selector.counters[0] = child_node_with_this_selector._counters[0] + 1
                # Increase the total number of true positives tp in the header table.
                self._header_table[selector][0][0] = self._header_table[selector][0][0] + 1
                # Go down in the tree (the current node will be the current parent node in the next iteration).
                current_parent_node = child_node_with_this_selector
            elif (not target_match) and (child_node_with_this_selector is not None):
                # Increase the false positives fp in the node.
                child_node_with_this_selector.counters[1] = child_node_with_this_selector._counters[1] + 1
                # Increase the total number of false positives fp in the header table.
                self._header_table[selector][0][1] = self._header_table[selector][0][1] + 1
                # Go down in the tree (the current node will be the current parent node in the next iteration).
                current_parent_node = child_node_with_this_selector
            elif (target_match) and (child_node_with_this_selector is None):
                # Create a new FPTree Node.
                new_fptreenode = FPTreeNode(selector, [1, 0], None)
                # Add it as a child of the current parent node.
                current_parent_node.add_child(new_fptreenode)
                # Check if the current selector is in the header table.
                if selector in self._header_table:
                    # If it is in the header table, add the new node at the end of the horizontal list and increase the summation of true positives tp in the header table.
                    self._header_table[selector][2]._node_link = new_fptreenode
                    self._header_table[selector][2] = new_fptreenode
                    self._header_table[selector][0][0] = self._header_table[selector][0][0] + 1
                else: # If not, create the entry and add it.
                    self._header_table[selector] = [ [1, 0], new_fptreenode, new_fptreenode ]
                # Go down in the tree (the current node will be the current parent node in the next iteration).
                current_parent_node = new_fptreenode
            elif (not target_match) and (child_node_with_this_selector is None):
                # Create a new FPTree Node.
                new_fptreenode = FPTreeNode(selector, [0, 1], None)
                # Add it as a child of the current parent node.
                current_parent_node.add_child(new_fptreenode)
                # Check if the current selector is in the header table.
                if selector in self._header_table:
                    # If it is in the header table, add the new node at the end of the horizontal list and increase the summation of false positives fp in the header table.
                    self._header_table[selector][2]._node_link = new_fptreenode
                    self._header_table[selector][2] = new_fptreenode
                    self._header_table[selector][0][1] = self._header_table[selector][0][1] + 1
                else: # If not, create the entry and add it.
                    self._header_table[selector] = [ [0, 1], new_fptreenode, new_fptreenode ]
                # Go down in the tree (the current node will be the current parent node in the next iteration).
                current_parent_node = new_fptreenode
    
    def build_tree(self, pandas_dataframe : DataFrame, set_of_frequent_selectors : dict[str, tuple[Selector, list[int], int]], target : tuple[str, Union[int, float, str]]) -> None:
        """Method to build the complete FPTree from a pandas DataFrame and using the set of frequent selectors. IMPORTANT: missing values are not supported yet.
        
        :param pandas_dataframe: the DataFrame which is scanned. IMPORTANT: missing values are not supported yet.
        :param set_of_frequent_selectors: the set of frequent selectors generated by the method 'generate_set_of_frequent_selectors'.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'DataFrame'.")
        if type(set_of_frequent_selectors) is not dict:
            raise TypeError("The type of the parameter 'set_of_frequent_selectors' must be 'dict'.")
        if type(target) is not tuple:
            raise TypeError("The type of the parameter 'target' must be 'tuple'.")
        # Iterate through the rows by index.
        for row in pandas_dataframe.index:
            target_value_in_the_current_row = pandas_dataframe.loc[row, target[0]]
            selectors_in_the_current_row = []
            # Iterate through the columns (except the target).
            for column in pandas_dataframe.columns.drop(target[0]):
                current_element = pandas_dataframe.loc[row, column]
                # Add the corresponding selector from 'set_of_frequent_selectors' to 'selectors_in_the_current_row'.
                # ===> IMPORTANT: the selector might not exist because it was pruned. In this case, a KeyError exception is raised.
                try:
                    # IMPORTANT: we use 'repr' in order to add simple quotes to the values of type str, but not to the values of numeric types.
                    selectors_in_the_current_row.append( set_of_frequent_selectors[column+repr(current_element)][0] )
                except KeyError:
                    pass # If the exception is raised, we do nothing.
            # We sort 'selectors_in_the_current_row' according to the value of 'n' (tp+fp) in the set of frequent selectors (CRITERION EXTRACTED FROM VIKAMINE).
            # - In case of tie, we NEED TO MAINTAIN the order of the selectors according to the order in the set of frequent selectors. For this reason, it is necessary to sort twice.
            # IMPORTANT: we use 'repr' in order to add simple quotes to the values of type str, but not to the values of numeric types.
            selectors_in_the_current_row = sorted(selectors_in_the_current_row, key = lambda x : set_of_frequent_selectors[x.attribute_name+repr(x.value)][2], reverse=False) # key -> [2] : the insertion order in the dictionary.
            selectors_in_the_current_row = sorted(selectors_in_the_current_row, key = lambda x : (set_of_frequent_selectors[x.attribute_name+repr(x.value)][1][0]+set_of_frequent_selectors[x.attribute_name+repr(x.value)][1][1]), reverse=True) # key -> 'n' : sum of tp and fp.
            # Insert.
            self._insert_tree(selectors_in_the_current_row, self._root_node, (target_value_in_the_current_row == target[1]))
        # Finally, we create the sorted header table.
        self._sorted_header_table = []
        for key in self._header_table:
            self._sorted_header_table.append( key )
        # IMPORTANT: THIS CRITERION HAS BEEN EXTRACTED FROM THE ORIGINAL IMPLEMENTATION OF THE SDMAP ALGORITHM (IN VIKAMINE).
        # We have to sort the selectors according to the summation of 'n' (i.e., summation of tp + summation of fp).
        # - In case of tie, we maintain the insertion order in the dictionary 'header_table'.
        self._sorted_header_table.sort(reverse=False, key=lambda x : (self._header_table[x][0][0] + self._header_table[x][0][1])) # Ascending order.
    
    def generate_conditional_fp_tree(self, list_of_selectors : list[Selector], minimum_tp : Union[int, None] = None, minimum_fp : Union[int, None] = None, minimum_n : Union[int, None] = None) -> 'FPTreeForSDMap':
        """Method to get the conditional FPTree with a list of selectors. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
        
        :param list_of_selectors: the list of selectors which is used. IMPORTANT: we assume that the list of selectors only contains selectors.
        :param minimum_tp: the minimum true positives (tp) threshold.
        :param minimum_fp: the minimum false positives (fp) threshold.
        :param minimum_n: the minimum subgroup description size (n) threshold.
        :return: the generated conditional FPTree.
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
        final_conditional_fp_tree = FPTreeForSDMap()
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
        while(current_node_in_the_horizontal_list is not None):
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
        return final_conditional_fp_tree
    
    def _insert_in_conditional_fp_tree(self, list_of_selectors : list[Selector], parent_node : FPTreeNode, fixed_tp : int, fixed_fp : int) -> None:
        """Private method to insert a list of selectors from a parent node.
        
        :param list_of_selectors: the list of selectors which is inserted in the conditional FPTree. IMPORTANT: we assume that the list of selectors only contains selectors.
        :param parent_node: the parent node from which to start the insertion.
        :param fixed_tp: the fixed number of true positives tp which is used in the insertions and in the increments.
        :param fixed_fp: the fixed number of false positives fp which is used in the insertions and in the increments.
        """
        current_parent_node = parent_node
        for selector in list_of_selectors:
            # Get the child node with the current selector or None if it does not exist.
            child_node_with_this_selector = current_parent_node.get_child_by_selector(selector) # type: ignore
            # Check if the node exists or not and if the parameter 'target_match' is True or False.
            if (child_node_with_this_selector is not None):
                # Increase the true positives tp and the false positives fp in the node.
                child_node_with_this_selector.counters[0] = child_node_with_this_selector._counters[0] + fixed_tp
                child_node_with_this_selector.counters[1] = child_node_with_this_selector._counters[1] + fixed_fp
                # Increase the total number of true positives tp and the total number of false positives fp in the header table.
                self._header_table[selector][0][0] = self._header_table[selector][0][0] + fixed_tp
                self._header_table[selector][0][1] = self._header_table[selector][0][1] + fixed_fp
                # Go down in the tree (the current node will be the current parent node in the next iteration).
                current_parent_node = child_node_with_this_selector
            elif (child_node_with_this_selector is None):
                # Create a new FPTree Node.
                new_fptreenode = FPTreeNode(selector, [fixed_tp, fixed_fp], None)
                # Add it as a child of the current parent node.
                current_parent_node.add_child(new_fptreenode) # type: ignore
                # Check if the current selector is in the header table.
                if selector in self._header_table:
                    # If it is in the header table, add the new node at the end of the horizontal list and increase the summation of tp and fp in the header table.
                    self._header_table[selector][2]._node_link = new_fptreenode
                    self._header_table[selector][2] = new_fptreenode
                    self._header_table[selector][0][0] = self._header_table[selector][0][0] + fixed_tp
                    self._header_table[selector][0][1] = self._header_table[selector][0][1] + fixed_fp
                else: # If not, create the entry and add it.
                    self._header_table[selector] = [ [fixed_tp, fixed_fp], new_fptreenode, new_fptreenode ]
                # Go down in the tree (the current node will be the current parent node in the next iteration).
                current_parent_node = new_fptreenode
