# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the BSD algorithm.
"""

from pandas import DataFrame
from pandas.api.types import is_string_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.data_structures.bitset_bsd import BitSetBSD, BitsetDictionary
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from bitarray import bitarray

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


class AlgorithmBSD(Algorithm):
    """This class represents the algorithm BSD (algorithm for subgroup discovery).

    
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
                        #(quality, subgroup, bits)
        self._k_subgroups = [(-99999,Pattern([]),[])]
        self._TP = 0
        self._FP = 0
        self._result = []
        self._irrelevants = []
        self._visited_subgroups = 0
        self._unselected_subgroups = 0
        self._additional_parameters_for_the_quality_measure = additional_parameters_for_the_quality_measure.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_quality_measure)
        self._additional_parameters_for_the_optimistic_estimate = additional_parameters_for_the_optimistic_estimate.copy()
        _delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_optimistic_estimate)
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
    
    
    def _get_unselected_subgroups(self) -> int:
        return self._unselected_subgroups

    def _get_visited_subgroups(self) -> int:
        return self._visited_subgroups
    
    
    minimum_support = property(_get_minimum_support, None , None , "The minimum support threshold.")
    quality_measure = property(_get_quality_measure, None , None , "The quality measure used to evaluate the subgroups.")
    num_subgroups = property(_get_num_subgroups, None , None , "The maximum number of subgroups to calculate the prune threshold.")
    max_depth = property(_get_max_depth, None , None , "The maximum depth of the search.")
    unselected_subgroups = property(_get_unselected_subgroups, None , None , "The number of pruned subgroups.")
    visited_subgroups = property(_get_visited_subgroups, None , None , "The number of visited subgroups.")

    def _handle_individual_result(self, individual_result: tuple) -> tuple[BitsetDictionary,BitsetDictionary,list]:
        """Private method to handle each individual result generated by the algorithm.
        :param individual_result: The individual result generated by the algorithm. It consists of a tuple with the values (selCond, sCurr, oe, quality,CcondPos,CcondNeg, cCurrPos, cCurrNeg,newSelRel,tp,fp).
        
        """
        self._visited_subgroups += 1

        selCond = individual_result[0]
        sCurr = individual_result[1]
        oe = individual_result[2]
        quality = individual_result[3]
        CcondPos = individual_result[4]
        CcondNeg = individual_result[5]
        cCurrPos = individual_result[6]
        cCurrNeg = individual_result[7]
        newSelRel = individual_result[8]
        tp = individual_result[9]
        fp = individual_result[10]
        

        # if optimistic estimate > min or k-subgroups is not full
        if(oe > self.k_subgroups[0][0] or len(self.k_subgroups) < self.num_subgroups):
            newSelRel.append((oe, sCurr))
            CcondPos,CcondNeg = self._attach(cCurrPos, cCurrNeg, CcondPos, CcondNeg, sCurr, selCond)
            #if quality > min or k-subgroups is not full
            if quality > self.k_subgroups[0][0] or len(self.k_subgroups) < self.num_subgroups:
                if selCond:
                    sg = selCond.copy().add_selector(sCurr)
                else:
                    sg = Pattern(sCurr)
                r= self._checkRel(self.k_subgroups, cCurrPos, cCurrNeg,quality,sg)
                #r = True
                if r:

                                        # (quality, subgroup, bits)
                    self.k_subgroups.append((quality, sg, cCurrPos + cCurrNeg,oe,(tp,fp)))
                    self.k_subgroups = sorted(self.k_subgroups, reverse=False)
                    self._checkRelevancies(cCurrPos, cCurrNeg, sg)
                    if len(self.k_subgroups) > self.num_subgroups:
                        #remove lowest quality subgroup
                        self.k_subgroups.pop(0)
                        self._unselected_subgroups += 1
                else:
                    self._unselected_subgroups += 1
            else:
                self._unselected_subgroups += 1
        else:
            self._unselected_subgroups +=1
        
        return CcondPos,CcondNeg,newSelRel

    
    def _BSD(self,selCond : str, selRel:list, CcondPos:dict, CcondNeg:dict, depth:int) -> list:
        """Private method to run the algorithm BSD  and generate frequent patterns.

        :param selCond: string of conditioned selectors
        :param selRel: list of relevant selectors
        :param CcondPos: bitset of positive instances
        :param CcondNeg: bitset of negative instances
        :param depth: current search depth
        :return: a list of tuples where every element has a frequent patterns (list of selectors) and its support
        """
        if type(selCond) is not str:
            raise TypeError("Parameter 'selCond' must be a list.")
        if type(selRel) is not list:
            raise TypeError("Parameter 'selRel' must be a list.")
        if type(CcondPos) is not BitsetDictionary:
            raise TypeError("Parameter 'CcondPos' must be a BitsetDictionary.")
        if type(CcondNeg) is not BitsetDictionary:
            raise TypeError("Parameter 'CcondNeg' must be a BitsetDictionary.")
        if type(depth) is not int:
            raise TypeError("Parameter 'depth' must be a int.")

        newSelRel = []
        for sCurr in selRel:
            #if selCond is empty
            if not selCond: 
                cCurrPos = CcondPos[sCurr]
                cCurrNeg = CcondNeg[sCurr]
            else:
                cCurrPos = self._logicalAnd(CcondPos[sCurr], CcondPos[selCond])
                cCurrNeg = self._logicalAnd(CcondNeg[sCurr], CcondNeg[selCond])
            #calculate tp and fp
            tp = self._cardinality(cCurrPos)
            fp = self._cardinality(cCurrNeg)
            if (tp + fp) == 0:
                self.prunneds += 1
                continue

            
            dict_of_parameter_for_optimistic_estimate = {QualityMeasure.BasicMetric_tp : tp, QualityMeasure.BasicMetric_fp : fp, QualityMeasure.BasicMetric_TP : self._TP, QualityMeasure.BasicMetric_FP : self._FP}
            dict_of_parameter_for_optimistic_estimate.update(self._additional_parameters_for_the_optimistic_estimate)
            oe = self._optimistic_estimate.compute(dict_of_parameter_for_optimistic_estimate)

            dict_of_parameters_for_quality_measure = {QualityMeasure.BasicMetric_tp: tp, QualityMeasure.BasicMetric_fp: fp,QualityMeasure.BasicMetric_TP: self._TP, QualityMeasure.BasicMetric_FP: self._FP}
            dict_of_parameters_for_quality_measure.update(self._additional_parameters_for_the_quality_measure)
            quality = self._quality_measure.compute(dict_of_parameters_for_quality_measure)

            CcondPos,CcondNeg,newSelRel = self._handle_individual_result((selCond, sCurr, oe, quality,CcondPos,CcondNeg, cCurrPos, cCurrNeg,newSelRel,tp,fp))
            
        # sort the selector by their optimistic estimate
        newSelRel = sorted(newSelRel, reverse=True)
        if depth < self.maxDepth and newSelRel:
            oe, newSelRelAux = zip(*newSelRel)
            newSelRelAux = list(newSelRelAux)
            for s in newSelRel:
                #if optimistic estimate > min
                if (s[0]> self.k_subgroups[0][0]):
                    if selCond:
                        selCondAux = selCond.copy().add_selector(s[1])
                    else:
                        selCondAux = Pattern(s[1])

                    newSelRelAux.remove(s[1])
                    self._BSD(selCondAux, newSelRelAux, CcondPos, CcondNeg, depth+1)

    def _attach(self,ccurrPos:list,ccurrNeg:list,CcondPos:dict,CcondNeg:dict, sCurr:str, selCond:str) -> tuple[dict,dict]:
        """Internal method to update the bitsets with de conditioned selector.

        :param ccurrPos: bitarray of positive instances
        :param ccurrNeg: bitarray of negative instances
        :param CcondPos: BitsetDictionary of selectors
        :param CcondNeg: BitsetDictionary of selectors
        :param sCurr: Current selector to be added with the conditioned selectors to the bitsets
        :param selCond: pattern of conditioned selectors
        :return: the bitsets updated CcondPos and CcondNeg
        """
        if type(ccurrPos) is not bitarray:
            raise TypeError("Parameter 'ccurrPos' must be a bitarray.")
        if type(ccurrNeg) is not bitarray:
            raise TypeError("Parameter 'ccurrNeg' must be a bitarray.")
        if type(CcondPos) is not BitsetDictionary:
            raise TypeError("Parameter 'CcondPos' must be a BitsetDictionary.")
        if type(CcondNeg) is not BitsetDictionary:
            raise TypeError("Parameter 'CcondNeg' must be a BitsetDictionary.")
        if type(sCurr) is not Selector:
            raise TypeError("Parameter 'sCurr' must be a Selector.")
        if type(selCond) is not Pattern:
            raise TypeError("Parameter 'selCond' must be a Pattern.")

        if selCond:
            newSel = selCond.copy().add_selector(sCurr)
            #update bitsets
            CcondPos[newSel] = ccurrPos
            CcondNeg[newSel] = ccurrNeg

        return CcondPos, CcondNeg


    def _checkRelevancies(self,cCurrPos : bitarray, cCurrNeg : bitarray ,sg : str) -> None:
        """Internal method to check relevacies in k_subgroups.
        :param cCurrPos: bitarray of positive instances
        :param cCurrNeg: bitarray of negative instances
        :param sg: Pattern in k_subgroups used to check relevancies
        """

        if type(cCurrPos) is not bitarray:
            raise TypeError("Parameter 'cCurrPos' must be a bitarray.")
        if type(cCurrNeg) is not bitarray:
            raise TypeError("Parameter 'cCurrNeg' must be a bitarray.")
        if type(sg) is not Pattern:
            raise TypeError("Parameter 'sg' must be a Pattern.")

        if len(self.k_subgroups[0][2]) == 0:
            self.k_subgroups.pop(0)

        aux =[]
        FPSg = self._cardinality(cCurrNeg)
        for tuple in self.k_subgroups:

            if tuple[1] == sg:
                # tuple is relevant
                aux.append(tuple)
                continue
            #Calculate tp of tuple
            TPTuple = self._cardinality(tuple[2][:len(cCurrPos)])
            #Calculate tp tuple and sg
            TPAnd = self._cardinality(self._logicalAnd(cCurrPos, tuple[2][:len(cCurrPos)]))

            if TPTuple > TPAnd:
                #tuple is relevant
                aux.append(tuple)
                continue

            FPAnd = self._cardinality(self._logicalAnd(cCurrNeg,tuple[2][-len(cCurrNeg):]))

            if FPAnd == FPSg:
                #tuple is irrelevant
                self.unselected_subgroups += 1
                self._irrelevants.append((tuple[1], tuple[0], tuple[2]))
            else:
                # tuple is relevant
                aux.append(tuple)


        self.k_subgroups = aux


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

            if TPAnd < TPSCurr:
                #Scurr is relevant for tuple
                continue
            #fp of tuple
            FPTuple = self._cardinality(tuple[2][-len(ccurrNeg):])
            #fp of Scurr AND tuple
            FPAnd = self._cardinality(self._logicalAnd(ccurrNeg,tuple[2][-len(ccurrNeg):]))
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
        n = 0
        for b in bitarr1:
            if b:
                n = n +1
        return n

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
        rv = []
        i = 0
        while i < len(bitarr1):
            rv.append(bitarr1[i] and bitarr2[i])
            i = i + 1
        return rv

    def fit(self, pandas_dataframe, tuple_target_attribute_value):
        """Method to run the algorithm BSD and generate subgroups.

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
        if tuple_target_attribute_value[0] not in pandas_dataframe.columns:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') is not an attribute of the input dataset.")
        self.tuple_target_attribute_value = tuple_target_attribute_value
        # Obtain TP and FP of the dataset.
        TP = sum(pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1])
        FP = pandas_dataframe.shape[0] - TP
        self._TP = TP
        self._FP = FP
        # Create an empty BitsetBSD.
        bitset = BitSetBSD()
        #generate frequent selector
        set_of_frequent_selectors = bitset.generate_set_of_frequent_selectors(pandas_dataframe, tuple_target_attribute_value, self._min_support)
        #build bitsets
        bitset.build_bitset(pandas_dataframe,set_of_frequent_selectors, tuple_target_attribute_value)
        #call BSD algorithm
        self._BSD(Pattern([]), set_of_frequent_selectors, bitset.biteset_pos, bitset.biteset_neg, 0)
        if (self._file_path is not None):
            self._file = open(self._file_path, "w")
            self._to_file(tuple_target_attribute_value)
            self._file.close()

    
    def _to_file(self, tuple_target_attribute_value):
        """Internal method to write the result of the algorithm BSD to a text file.
        """
        for element in self._k_subgroups:
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

            



            

    def to_file(self,  columns, total, printIrrelevants=False, printOE=False, printRS=True, path="BSD_output.txt"):
        """Method to write the result of the algorithm BSD to a text file.
        :type columns: Index
        :param columns: Index with the columns.
        :type total: float
        :param total: time.
        :type printIrrelevants: bool
        :param printIrrelevants: print the Irrelevant Set.
        :type printOE: bool
        :param printOE: print the Optimistic Estimate.
        :type printRS: bool
        :param printRS: print the Result Set.
        :type path: str
        :param path: path of the file where results will be written.
        """

        if type(path) is not str:
            raise TypeError("Parameter 'path' must be a string (str).")
        if type(printIrrelevants) is not bool:
            raise TypeError("Parameter 'printIrrelevants' must be a bool.")
        if type(printOE) is not bool:
            raise TypeError("Parameter 'printOE' must be a bool.")
        if type(printRS) is not bool:
            raise TypeError("Parameter 'printRS' must be a bool.")
        if type(total) is not float:
            raise TypeError("Parameter 'total' must be a float.")

        path = "pruebasBSD/"+str(columns.size) + "_K" + str(self.numSubgroups) +"_"+ str(self.maxDepth) + "_" + path
        file = open(path, "w")
        file.write("Algoritmo=BSD, K=" +  str(self.numSubgroups) + ", Max.Depth=" + str(self.maxDepth) + ", Min.Supp=")
        file.write(str(self.min_support) + ", MedidaCalidad=" + str(self.qualityMeasure.getName()) + "\n")
        pos = str(columns).find("[")
        pos2 = str(columns).find("]")
        columnas = str(columns)[pos + 1:pos2].rstrip()
        columnas = columnas.replace("\n", "")
        file.write("Atributos: " + str(columns.size) + "\n" + columnas + "\n")
        file.write("Target: " + self.tuple_target_attribute_value[0] + " = " + self.tuple_target_attribute_value[1] + "\n")
        file.write("Time: " + str(total) + " s\n")
        file.write("Subgrupos visitados: " + str(self.hypothesis) + "\n")
        file.write("Subgrupos podados: "+ str(self.prunneds) + "\n" )
        file.write("Subgrupos resultado: " + str(len(self.k_subgroups)) + "\n")
        file.write("Subgrupos irrelevantes: " + str(len(self.irrelevants)) + "\n")

        #if flag is actived, print result set
        if printRS:
            file.write("\nRESULT SET\n")
            for sublist in self.k_subgroups:
                subgroup = sublist[1]

                qm = sublist[0]
                file.write("AND(" + str(subgroup) + "), ")
                file.write("QUALITY(" + self.qualityMeasure.getName() + " = " + str(qm) + ")")
                # if flag is actived, print optimistic estimate
                if printOE:
                    file.write(", Optimistic Estimate(" + str(sublist[3]) + ")\n")
                else:
                    file.write("\n")
        # if flag is actived, print irrelevants
        if printIrrelevants:
            file.write("\nIRRELEVANTS\n")
            for sub in self.irrelevants:
                file.write("AND(" + sub[0] + "), ")
                file.write("QUALITY(" + self.qualityMeasure.getName() + " = " + str(sub[1]) + ")\n")



        file.close()