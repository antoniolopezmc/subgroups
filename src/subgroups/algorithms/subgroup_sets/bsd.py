# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles <fmora@um.es>

"""This file contains the implementation of the BSD algorithm.
"""

from pandas import DataFrame
from subgroups.algorithms.algorithm import Algorithm
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.data_structures.bitset_bsd import BitsetBSD, BitsetDictionary
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from bitarray import bitarray
from pandas.api.types import is_string_dtype
from subgroups.exceptions import DatasetAttributeTypeError

# Python annotations.
from typing import Union

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

class BSD(Algorithm):
    """This class represents the BSD algorithm.

    :param min_support: Minimum support threshold (NUMBER OF TIMES, NOT A PROPORTION).
    :param quality_measure: Specific quality measure to use for the final subgroups.
    :param optimistic_estimate: Optimistic estimate of the quality measure.
    :param num_subgroups: max of subgroups to calculate the prune threshold
    :param max_depth: max depth of search
    :param additional_parameters_for_the_quality_measure: if the quality measure passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param additional_parameters_for_the_optimistic_estimate: if the optimistic estimate passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """

    __slots__ = ('_maxDepth', '_min_support', '_quality_measure', '_optimistic_estimate', '_num_subgroups', '_k_subgroups', '_TP', '_FP', '_irrelevants', '_visited_subgroups', '_selected_subgroups', '_unselected_subgroups', '_pruned_subgroups', '_additional_parameters_for_the_quality_measure', '_additional_parameters_for_the_optimistic_estimate', '_bitset_pos', '_bitset_neg', '_file_path' , '_file')

    def __init__(self,min_support : Union[int,float] ,quality_measure : QualityMeasure , optimistic_estimate: QualityMeasure ,num_subgroups : int,max_depth: int, additional_parameters_for_the_quality_measure : dict[str, Union[int, float]] = dict(),additional_parameters_for_the_optimistic_estimate : dict[str, Union[int, float]] = dict(), write_results_in_file : bool = False, file_path : Union[str, None] = None) -> None: 
        """Method to initialize an object of type 'BSD'.
        """
        if not isinstance(quality_measure, QualityMeasure):
            raise TypeError("Parameter 'quality_measure' must be a subclass of QualityMeasure.")
        if type(num_subgroups) is not int:
            raise TypeError("Parameter 'num_subgroups' must be a int.")
        if type(max_depth) is not int:
            raise TypeError("Parameter 'max_depth' must be a int.")
        if (type(min_support) is not int) and (type(min_support) is not float):
            raise TypeError("Parameter 'min_support' must be a number.")
        if (type(additional_parameters_for_the_quality_measure) is not dict):
            raise TypeError("The type of the parameter 'additional_parameters_for_the_quality_measure' must be 'dict'")
        if (type(write_results_in_file) is not bool):
            raise TypeError("The type of the parameter 'write_results_in_file' must be 'bool'")
        if ((type(file_path) is not str) and (file_path is not None)):
            raise TypeError("The type of the parameter 'file_path' must be 'str' or 'NoneType'.")
        # If 'write_results_in_file' is True, 'file_path' must not be None.
        if (write_results_in_file) and (file_path is None):
            raise ValueError("If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        # We check whether 'optimistic_estimate' is an optimistic estimate of 'quality_measure'.
        if quality_measure.get_name() not in optimistic_estimate.optimistic_estimate_of():
            raise ValueError("The quality measure " + optimistic_estimate.get_name() + " is not an optimistic estimate of the quality measure " + quality_measure.get_name() + ".")
        self._maxDepth = max_depth
        self._min_support = min_support
        self._quality_measure = quality_measure
        self._optimistic_estimate = optimistic_estimate
        self._num_subgroups = num_subgroups
        # We initialize the list of subgroups with a dummy subgroup.
        #     (quality, subgroup, bits, optimistic_estimate, (tp,fp))
        self._k_subgroups = [(-99999,Pattern([]),bitarray(),-99999,(0,0))]
        self._TP = 0
        self._FP = 0
        self._irrelevants = []  #List of unselected subgroups.
        self._visited_subgroups = 0
        self._selected_subgroups = 0
        self._unselected_subgroups = 0
        self._pruned_subgroups = 0
        self._additional_parameters_for_the_quality_measure = additional_parameters_for_the_quality_measure.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_quality_measure)
        self._additional_parameters_for_the_optimistic_estimate = additional_parameters_for_the_optimistic_estimate.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_optimistic_estimate)
        # We only write the results in a file if the parameter 'write_results_in_file' is True.
        if (write_results_in_file):
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None

    def _get_minimum_support(self) -> Union[int,float]:
        return self._min_support

    def _get_quality_measure(self) -> QualityMeasure:
        return self._quality_measure
    
    def _get_num_subgroups(self) -> int:
        return self._num_subgroups
    
    def _get_max_depth(self) -> int:
        return self._maxDepth
    
    def _get_selected_subgroups(self) -> int:
        return self._selected_subgroups
    
    def _get_unselected_subgroups(self) -> int:
        return self._unselected_subgroups

    def _get_visited_subgroups(self) -> int:
        return self._visited_subgroups

    def _get_pruned_subgroups(self) -> int:
        return self._pruned_subgroups
    
    minimum_support = property(_get_minimum_support, None , None , "The minimum support threshold.")
    quality_measure = property(_get_quality_measure, None , None , "The quality measure used to evaluate the subgroups.")
    num_subgroups = property(_get_num_subgroups, None , None , "The maximum number of subgroups to calculate the prune threshold.")
    max_depth = property(_get_max_depth, None , None , "The maximum depth of the search.")
    unselected_subgroups = property(_get_unselected_subgroups, None , None , "The number of pruned subgroups.")
    selected_subgroups = property(_get_selected_subgroups, None , None , "The number of selected subgroups.")
    visited_subgroups = property(_get_visited_subgroups, None , None , "The number of visited subgroups.")
    pruned_subgroups = property(_get_pruned_subgroups, None , None , "The number of pruned subgroups.")

    def _handle_individual_result(self, individual_result: tuple) -> list:
        """Private method to handle each individual result generated by the algorithm.

        :param individual_result: The individual result generated by the algorithm. It consists of a tuple with the values (selCond, sCurr, oe, quality,CcondPos,CcondNeg, cCurrPos, cCurrNeg,newSelRel,tp,fp).
        :return: a list of relevant selectors to be evaluated with the current conditioned selectors (only used for next recursive calls).
        """
        self._visited_subgroups += 1
        selCond = individual_result[0]
        sCurr = individual_result[1]
        oe = individual_result[2]
        quality = individual_result[3]
        cCurrPos = individual_result[4]
        cCurrNeg = individual_result[5]
        newSelRel = individual_result[6]
        tp = individual_result[7]
        fp = individual_result[8]
        # if optimistic estimate > quality of worst subgroup or k-subgroups is not full
        if(oe > self._k_subgroups[0][0] or len(self._k_subgroups) < self.num_subgroups):
            # Add the current selector to the list of new selectors added to the conditional pattern
            newSelRel.append((oe, sCurr))
            #if quality > min or k-subgroups is not full
            if quality > self._k_subgroups[0][0] or len(self._k_subgroups) < self.num_subgroups:
                # sg = conditional pattern + current selector
                if selCond:
                    sg = selCond.copy()
                    sg.add_selector(sCurr)
                else:
                    sg = Pattern([sCurr])
                r= self._checkRel(self._k_subgroups, cCurrPos, cCurrNeg,quality,sg)
                # If the subgroup is relevant, we add it to the list of k-subgroups
                if r:
                    # (quality, subgroup, bits, optimistic_estimate, (tp,fp))
                    self._k_subgroups.append((quality, sg, cCurrPos + cCurrNeg,oe,(tp,fp)))
                    self._k_subgroups = sorted(self._k_subgroups, reverse=False, key=lambda x: x[0])
                    # Check if the subgroups in k_subgroups are still relevant
                    self._checkRelevancies(cCurrPos, cCurrNeg, sg)
                    # If k_subgroups is full, remove the subgroup with the lowest quality
                    if len(self._k_subgroups) > self.num_subgroups:
                        # Remove lowest quality subgroup
                        self._k_subgroups.pop(0)
                        self._unselected_subgroups += 1
                else:
                    self._unselected_subgroups += 1
            else:
                self._unselected_subgroups += 1
        # If the optimistic estimate is less than the quality of the worst subgroup, we prune the subgroup
        else:
            self._pruned_subgroups += 1
            self._unselected_subgroups +=1
        return newSelRel

    def _BSD(self,selCond : Pattern, selRel:list, CcondPos:bitarray, CcondNeg:bitarray, depth:int) -> list:
        """Private method to run the BSD algorithm and generate frequent patterns.

        :param selCond: string of conditioned selectors
        :param selRel: list of relevant selectors
        :param CcondPos: bitarray of positive instances bitarray of conditioned selectors
        :param CcondNeg: bitarray of negative instances bitarray of conditioned selectors
        :param depth: current search depth
        :return: a list of tuples where every element has a frequent patterns (list of selectors) and its support
        """
        if type(selCond) is not Pattern:
            raise TypeError("Parameter 'selCond' must be a Pattern.")
        if type(selRel) is not list:
            raise TypeError("Parameter 'selRel' must be a list.")
        if type(CcondPos) is not bitarray:
            raise TypeError("Parameter 'CcondPos' must be a bitarray.")
        if type(CcondNeg) is not bitarray:
            raise TypeError("Parameter 'CcondNeg' must be a bitarray.")
        if type(depth) is not int:
            raise TypeError("Parameter 'depth' must be a int.")
        #List of relevant selectors to be evaluated with the current conditioned selectors (only used for next recursive calls)
        newSelRel = []
        for sCurr in selRel:
            #if selCond is empty
            if not selCond: 
                cCurrPos = self._bitset_pos[sCurr]
                cCurrNeg = self._bitset_neg[sCurr]
            else:
                # Calculate cCurrPos and cCurrNeg as the intersection of the bitsets of the current conditioned selectors and the current selector
                cCurrPos = self._logicalAnd(CcondPos, self._bitset_pos[sCurr])
                cCurrNeg = self._logicalAnd(CcondNeg, self._bitset_neg[sCurr])
            # Calculate tp and fp
            tp = self._cardinality(cCurrPos)
            fp = self._cardinality(cCurrNeg)
            # If the pattern does not appear in the dataset, it is not evaluated
            if (tp + fp) == 0:
                self._unselected_subgroups += 1
                continue
            # Calculate optimistic estimate and quality measure to handle the current pattern
            dict_of_parameter_for_optimistic_estimate = {QualityMeasure.TRUE_POSITIVES : tp, QualityMeasure.FALSE_POSITIVES : fp, QualityMeasure.TRUE_POPULATION : self._TP, QualityMeasure.FALSE_POPULATION : self._FP}
            dict_of_parameter_for_optimistic_estimate.update(self._additional_parameters_for_the_optimistic_estimate)
            oe = self._optimistic_estimate.compute(dict_of_parameter_for_optimistic_estimate)
            dict_of_parameters_for_quality_measure = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.FALSE_POSITIVES: fp,QualityMeasure.TRUE_POPULATION: self._TP, QualityMeasure.FALSE_POPULATION: self._FP}
            dict_of_parameters_for_quality_measure.update(self._additional_parameters_for_the_quality_measure)
            quality = self._quality_measure.compute(dict_of_parameters_for_quality_measure)
            newSelRel = self._handle_individual_result((selCond, sCurr, oe, quality, cCurrPos, cCurrNeg,newSelRel,tp,fp))
        # Sort the selectors by their optimistic estimate
        newSelRel = sorted(newSelRel, reverse=True)
        # If the current depth is less than the maximum depth and we have more selectors, we continue the search
        if depth < self._maxDepth and newSelRel:
            oe, newSelRelAux = zip(*newSelRel)
            newSelRelAux = list(newSelRelAux)
            newSelRelAux = newSelRelAux.copy()
            for s in newSelRel:
                #if optimistic estimate > min
                if (s[0]> self._k_subgroups[0][0]):
                    if selCond:
                        selCondAux = selCond.copy()
                        selCondAux.add_selector(s[1])
                    else:
                        selCondAux = Pattern([s[1]])
                    # We remove the selector from the list of relevant selectors to avoid evaluating it again
                    newSelRelAux.remove(s[1])
                    cCurrPos = self._logicalAnd(CcondPos, self._bitset_pos[s[1]])
                    cCurrNeg = self._logicalAnd(CcondNeg, self._bitset_neg[s[1]])
                    self._BSD(selCondAux, newSelRelAux, cCurrPos, cCurrNeg, depth+1)
                # If the optimistic estimate is less than the quality of the worst subgroup, we prune the subgroup
                else:
                    self._pruned_subgroups += 1
                    self._unselected_subgroups +=1

    def _checkRelevancies(self,cCurrPos : bitarray, cCurrNeg : bitarray ,sg : Pattern) -> None:
        """Internal method to check relevacies in _k_subgroups after the addition of a new subgroups sg.

        :param cCurrPos: bitarray of positive instances
        :param cCurrNeg: bitarray of negative instances
        :param sg: Pattern in _k_subgroups used to check relevancies
        """
        if type(cCurrPos) is not bitarray:
            raise TypeError("Parameter 'cCurrPos' must be a bitarray.")
        if type(cCurrNeg) is not bitarray:
            raise TypeError("Parameter 'cCurrNeg' must be a bitarray.")
        if type(sg) is not Pattern:
            raise TypeError("Parameter 'sg' must be a Pattern.")
        # Eliminate the dummy subgroup
        if len(self._k_subgroups[0][1]) == 0:
            self._k_subgroups.pop(0)
        # New list of k_subgroups
        aux =[]
        FPSg = self._cardinality(cCurrNeg)
        for tuple in self._k_subgroups:
            # Current subgroup is the same as the new subgroup
            if tuple[1] == sg:
                # tuple is relevant
                aux.append(tuple)
                continue
            #Calculate tp of tuple
            TPTuple = self._cardinality(tuple[2][:len(cCurrPos)])
            #Calculate tp tuple and sg
            TPAnd = self._cardinality(self._logicalAnd(cCurrPos, tuple[2][:len(cCurrPos)]))
            # If positive instances of the tuple are not included in the new subgroup, the tuple is relevant
            if TPTuple > TPAnd:
                #tuple is relevant
                aux.append(tuple)
                continue
            FPAnd = self._cardinality(self._logicalAnd(cCurrNeg,tuple[2][-len(cCurrNeg):]))
            # If negative instances of the new subgroup are included in the tuple (and positives of the tuple are included in the new subgroup),
            # the tuple is irrelevant
            if FPAnd == FPSg:
                #tuple is irrelevant
                self._unselected_subgroups += 1
                self._irrelevants.append((tuple[1], tuple[0], tuple[2]))
            else:
                # tuple is relevant
                aux.append(tuple)
        self._k_subgroups = aux

    def _checkRel(self,res:list,ccurrPos:bitarray,ccurrNeg:bitarray,quality:float, sCurr:Pattern) -> bool:
        """Internal method to check if sCurr is relevant in res.

        :param res: list of tuples
        :param ccurrPos: bitarray of positive instances
        :param ccurrNeg: bitarray of negative instances
        :param quality: sCurr quality
        :param sCurr: Pattern of the subgroup found
        :return: check if ccurrPos + ccurrNeg is relevant in res
        """
        if type(res) is not list:
            raise TypeError("Parameter 'res' must be a list.")
        if type(ccurrPos) is not bitarray:
            raise TypeError("Parameter 'ccurrPos' must be a bitarray.")
        if type(ccurrNeg) is not bitarray:
            raise TypeError("Parameter 'ccurrNeg' must be a bitarray.")
        if type(quality) is not float:
            raise TypeError("Parameter 'quality' must be a float.")
        if type(sCurr) is not Pattern:
            raise TypeError("Parameter 'sCurr' must be a Pattern.")
        #if is empty
        if not res[0][1]:
            return True
        bits = ccurrPos + ccurrNeg
        #tp of scurr
        TPSCurr = self._cardinality(ccurrPos)
        for tuple in res:
            #tp of Scurr AND tuple
            TPAnd = self._cardinality(self._logicalAnd(ccurrPos,tuple[2][:len(ccurrPos)]))
            # If positives instances of sCurr are not included in the tuple, sCurr is relevant
            if TPAnd < TPSCurr:
                #Scurr is relevant for tuple
                continue
            #fp of tuple
            FPTuple = self._cardinality(tuple[2][-len(ccurrNeg):])
            #fp of Scurr AND tuple
            FPAnd = self._cardinality(self._logicalAnd(ccurrNeg,tuple[2][-len(ccurrNeg):]))
            # If positives instances of sCurr are included in the tuple and negatives instances of the tuple are included in sCurr,
            # sCurr is irrelevant
            if FPAnd == FPTuple:
                self._irrelevants.append((sCurr, quality, bits))
                return False
        return True

    def _cardinality(self,bitarr1 : bitarray) -> int:
        """Internal method to count the True valors of a bitarr1.

        :param bitarr1: bitarr1 of boolean
        :return: tp of the bitarr1
        """
        if type(bitarr1) is not bitarray:
            raise TypeError("Parameter 'bitarr1' must be a bitarray.")
        #n = 0
        #for b in bitarr1:
        #    if b:
        #        n = n +1
        #return n
        return bitarr1.count(1)

    def _logicalAnd(self,bitarr1 : bitarray,bitarr2 :bitarray) -> bitarray:
        """Internal method to  calculate the logical and of two bitarrays.

        :param bitarr1: bitarray of boolean
        :param bitarr2: bitarray of boolean
        :return: bitarray (bitarr1 and bitarr2)
        """
        if type(bitarr1) is not bitarray:
            raise TypeError("Parameter 'bitarr1' must be a bitarray.")
        if type(bitarr2) is not bitarray:
            raise TypeError("Parameter 'bitarr2' must be a bitarray.")
        if len(bitarr1) != len(bitarr2):
            raise TypeError("Lists must be the same length")
        #rv = bitarray()
        #i = 0
        #while i < len(bitarr1):
        #    rv.append(bitarr1[i] and bitarr2[i])
        #    i = i + 1
        #return rv
        return bitarr1 & bitarr2

    def fit(self, pandas_dataframe, tuple_target_attribute_value):
        """Method to run the BSD algorithm and generate subgroups.

        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :type tuple_target_attribute_value: tuple
        :param tuple_target_attribute_value: Tuple with the name of the target attribute (first element) and with the value of this attribute (second element). EXAMPLE1: ("age", 25). EXAMPLE2: ("class", "Setosa"). It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset,
          (3) it is VERY IMPORTANT to respect the types of the attributes: the value in the tuple (second element) MUST BE comparable with the values of the corresponding attribute in the dataset,
          (4) the value of the target attribute MUST exist in the dataset.
        :rtype: list
        :return: a list of tuples with the best subgroups and its quality measures.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if (type(tuple_target_attribute_value) is not tuple):
            raise TypeError("Parameter 'tuple_target_attribute_value' must be a tuple.")
        if (len(tuple_target_attribute_value) != 2):
            raise ValueError("Parameter 'tuple_target_attribute_value' must be of length 2.")
        if type(tuple_target_attribute_value[0]) is not str:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') must be a string.")
        # IMPORTANT: this algorithm only supports nominal attributes (i.e., type 'str').
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise DatasetAttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
        # Obtain TP and FP of the dataset.
        TP = sum(pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1])
        FP = pandas_dataframe.shape[0] - TP
        self._TP = TP
        self._FP = FP
        # Create an empty BitsetBSD.
        bitset = BitsetBSD()
        #generate frequent selector
        set_of_frequent_selectors = bitset.generate_set_of_frequent_selectors(pandas_dataframe, tuple_target_attribute_value, self._min_support)
        #build bitsets
        bitset.build_bitset(pandas_dataframe,set_of_frequent_selectors, tuple_target_attribute_value)
        self._bitset_pos = bitset.bitset_pos
        self._bitset_neg = bitset.bitset_neg
        #call BSD algorithm
        self._BSD(Pattern([]), set_of_frequent_selectors, bitset.all_true_positives(), bitset.all_true_negatives(), 0)
        # We do not count the initial subgroup.
        if self._k_subgroups[0][0] == -99999:
            self._selected_subgroups = len(self._k_subgroups) - 1
        else:
            self._selected_subgroups = len(self._k_subgroups)
        if (self._file_path is not None):
            self._file = open(self._file_path, "w")
            self._to_file(tuple_target_attribute_value)
            self._file.close()
            self._file = None
    
    def _to_file(self, tuple_target_attribute_value):
        """Internal method to write the result of the BSD algorithm to a text file.
        """
        for element in self._k_subgroups:
            #Skip the initial subgroup if it is in the list.
            if element[0]==-99999:
                continue
            #Create the subgroup.
            pat = element[1]
            subgroup = Subgroup(pat, Selector(tuple_target_attribute_value[0],Operator.EQUAL,tuple_target_attribute_value[1]))
            #Get the description of the subgroup.
            tp = element[4][0]
            fp = element[4][1]
            quality = element[0]
            self._file.write(str(subgroup) + " ; ")
            self._file.write("Quality Measure " + self._quality_measure.get_name() + " = " + str(quality) + " ; ")
            self._file.write("tp = " + str(tp) + " ; ")
            self._file.write("fp = " + str(fp) + " ; ")
            self._file.write("TP = " + str(self._TP) + " ; ")
            self._file.write("FP = " + str(self._FP) + "\n")