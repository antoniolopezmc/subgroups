# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the SDMap algorithm.
"""

from pandas import DataFrame
from pandas.api.types import is_string_dtype
from subgroups.algorithms._base import Algorithm
from subgroups.quality_measures._base import QualityMeasure
from subgroups.exceptions import ParametersError, AttributeTypeError
from subgroups.data_structures.fp_tree_for_sdmap import FPTreeForSDMap
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from numpy import sum

def _generate_all_combinations(list_of_selectors):
    """Private method to generate all the combinations (including the empty list) of the list of selectors passed by parameter.
    
    :type list_of_selectors: list[Selector]
    :param list_of_selectors: the list of selectors which is used.
    """
    if list_of_selectors == []:
        return [[]]
    x = _generate_all_combinations(list_of_selectors[1:])
    return x + [[list_of_selectors[0]] + y for y in x]

class SDMap(Algorithm):
    """This class represents the SDMap algorithm. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
    
    :type quality_measure: QualityMeasure
    :param quality_measure: the quality measure which is used.
    :type minimum_quality_measure_value: int or float
    :param minimum_quality_measure_value: the minimum quality measure value threshold.
    :type minimum_tp: int
    :param minimum_tp: the minimum true positives (tp) threshold.
    :type minimum_fp: int
    :param minimum_fp: the minimum false positives (fp) threshold.
    :type minimum_n: int
    :param minimum_n: the minimum subgroup description size (n) threshold.
    """
    
    __slots__ = "_quality_measure", "_minimum_quality_measure_value", "_minimum_tp", "_minimum_fp", "_minimum_n", "_visited_nodes", "_pruned_nodes"
    
    def __init__(self, quality_measure, minimum_quality_measure_value, minimum_tp=None, minimum_fp=None, minimum_n=None):
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("The parameter 'quality_measure' must be a subclass of QualityMeasure.")
        if (type(minimum_quality_measure_value) is not int) and (type(minimum_quality_measure_value) is not float):
            raise TypeError("The type of the parameter 'minimum_quality_measure_value' must be 'int' or 'float'.")
        if (type(minimum_tp) is not int) and (minimum_tp is not None):
            raise TypeError("The type of the parameter 'minimum_tp' must be 'int' or 'NoneType'.")
        if (type(minimum_fp) is not int) and (minimum_fp is not None):
            raise TypeError("The type of the parameter 'minimum_fp' must be 'int' or 'NoneType'.")
        if (type(minimum_n) is not int) and (minimum_n is not None):
            raise TypeError("The type of the parameter 'minimum_n' must be 'int' or 'NoneType'.")
        # Depending on the values of the parameters 'minimum_tp', 'minimum_fp' and 'minimum_n' ...
        if ( (minimum_tp is not None) and (minimum_fp is not None) and (minimum_n is None) ) or \
            ( (minimum_tp is None) and (minimum_fp is None) and (minimum_n is not None) ):
            self._quality_measure = quality_measure
            self._minimum_quality_measure_value = minimum_quality_measure_value
            self._minimum_tp = minimum_tp
            self._minimum_fp = minimum_fp
            self._minimum_n = minimum_n
            self._visited_nodes = 0
            self._pruned_nodes = 0
        else:
            raise ParametersError("If 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.")
    
    def _get_quality_measure(self):
        return self._quality_measure
    
    def _get_minimum_quality_measure_value(self):
        return self._minimum_quality_measure_value
    
    def _get_minimum_tp(self):
        return self._minimum_tp
    
    def _get_minimum_fp(self):
        return self._minimum_fp
    
    def _get_minimum_n(self):
        return self._minimum_n
    
    quality_measure = property(_get_quality_measure, None, None, "The quality measure which is used.")
    minimum_quality_measure_value = property(_get_minimum_quality_measure_value, None, None, "The minimum quality measure value threshold.")
    minimum_tp = property(_get_minimum_tp, None, None, "The minimum true positives (tp) threshold.")
    minimum_fp = property(_get_minimum_fp, None, None, "The minimum false positives (fp) threshold.")
    minimum_n = property(_get_minimum_n, None, None, "The minimum subgroup description size (n) threshold.")
    
    def _get_visited_nodes(self):
        return self._visited_nodes
    
    def _get_pruned_nodes(self):
        return self._pruned_nodes
    
    visited_nodes = property(_get_visited_nodes, None, None, "The visited nodes after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")
    pruned_nodes = property(_get_pruned_nodes, None, None, "The pruned nodes after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")
    
    def _fpgrowth(self, fptree, alpha):
        """Private method to run the adapted FPGrowth algorithm in order to generate frequent patterns.
        
        :type fptree: FPTreeForSDMap
        :param fptree: the current FPTree. At the beginning, it is the FPTreeForSDMap generated from the complete dataset. Although, it will change between recursive calls to this method.
        :type alpha: list[Selector]
        :param alpha: a list of selectors.
        :rtype: list[tuple[Pattern, list[int, int]]]
        :return: a list of tuples in which each element has a frequent pattern (Pattern) and a list with its true positives (tp) and its false positives (fp).
        """
        # Check if fptree contains a single path.
        if fptree.there_is_a_single_path():
            # Generate all the combinations of the selectors in the single path.
            all_combinations = _generate_all_combinations(fptree._sorted_header_table)
            # Remove the empty list.
            all_combinations.remove([])
            # Variable to store the final result: it will be a LIST OF TUPLES in which each tuple is of the form: (frequent pattern, list of the form [tp,fp])
            final_result = []
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
                # Add it to the final result.
                final_result.append( (pattern, [tp, fp]) )
            # Return the result.
            return final_result
        else:
            # Variable to store the final result: it will be a LIST OF TUPLES in which each tuple is of the form: (frequent pattern, list of the form [tp,fp])
            final_result = []
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
                # Add it to the final result.
                final_result.append( (beta_as_Pattern, [tp,fp]) )
                # Build the conditional FPTree.
                conditional_fp_tree = fptree.generate_conditional_fp_tree(beta_as_list, minimum_tp=self.minimum_tp, minimum_fp=self.minimum_fp, minimum_n=self.minimum_n)
                # Recursive call.
                if not conditional_fp_tree.is_empty():
                    final_result = final_result + self._fpgrowth(conditional_fp_tree, beta_as_list)
            # Return the result.
            return final_result
    
    def fit(self, pandas_dataframe, target):
        """Method to run the SDMap algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        
        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :type target: tuple[str, str]
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :rtype: list[tuple[Subgroup, int]] or list[tuple[Subgroup, float]]
        :return: a list of tuples in which each element has a subgroup and its quality measures value.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("The type of the parameter 'pandas_dataframe' must be 'DataFrame'.")
        if type(target) is not tuple:
            raise TypeError("The type of the parameter 'target' must be 'tuple'.")
        # IMPORTANT: this algorithm only supports nominal attributes (i.e., type 'str').
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise AttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
        # Create an empty FPTreeForSDMap.
        fptree = FPTreeForSDMap()
        # Generate the set of frequent selectors.
        set_of_frequent_selectors = fptree.generate_set_of_frequent_selectors(pandas_dataframe, target, minimum_tp=self.minimum_tp, minimum_fp=self.minimum_fp, minimum_n=self.minimum_n)
        # Build the FPTree.
        fptree.build_tree(pandas_dataframe, set_of_frequent_selectors, target)
        # Only if the fptree is not empty ...
        if not fptree.is_empty():
            # Variable to store the final result.
            final_result = []
            # Call to the adapated FPGrowth algorithm in order to obtain frequent patterns.
            frequent_patterns = self._fpgrowth(fptree, None)
            # Obtain TP and FP of the dataset.
            TP = sum(pandas_dataframe[target[0]] == target[1])
            FP = len(pandas_dataframe.index) - TP
            # Iterate throughout the frequent pattern (Patterns) obtained with the adapted fpgrowth algorithm.
            for elem in frequent_patterns:
                # Generate a subgroup.
                subgroup = Subgroup(elem[0], Selector(target[0], Operator.EQUAL, target[1]))
                # Compute the quality measure.
                quality_measure_value = self._quality_measure.compute({QualityMeasure.SUBGROUP_PARAMETER_tp : elem[1][0], QualityMeasure.SUBGROUP_PARAMETER_fp : elem[1][1], QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP})
                # Add the subgroup only if the quality measure value is greater or equal than the threshold.
                if quality_measure_value >= self._minimum_quality_measure_value:
                    final_result.append( (subgroup, quality_measure_value) )
                    self._visited_nodes = self._visited_nodes + 1
                else:
                    self._pruned_nodes = self._pruned_nodes + 1
            return final_result
        else:
            return []
