# -*- coding: utf-8 -*-

# Contributors:
#    Álvaro Riquelme Tornel <alvaroriquelmetornel@gmail.com>

"""This file contains the implementation of the SD algorithm.
"""
import numpy as np
import pandas
from pandas import DataFrame

from typing import Union
from pandas.api.types import is_string_dtype, is_float_dtype, is_integer_dtype
from subgroups.algorithms.algorithm import Algorithm
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.quality_measures.qg import Qg

from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.quality_measures.support import Support

class SD(Algorithm):
    """This class represents the SD algorithm. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
    
    :param minimum_quality_measure_value: the minimum quality measure value threshold.
    :param min_support: Minimum support that need to have a subgroup to be considered. Value in form of PROPORTION (between 0 and 1).
    :param beam_width: Width of the beam.
    :param quality_measure: the quality measure which is used.
    :param additional_parameters_for_the_quality_measure: if the quality measure passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """

    __slots__ = ( "_g_parameter","_minimum_quality_measure_value", "_beam_width","_unselected_subgroups", "_selected_subgroups", "_file_path", "_file")
    
    def __init__(self,  minimum_quality_measure_value: Union[int,float], g_parameter: Union[int,float] = 1,  beam_width : int = 20 ,write_results_in_file : bool = False, file_path : Union[str, None] = None) -> None:
        """Method to initialize an object of type 'SD'.
        """
        if (type (g_parameter) is not int) and (type(g_parameter) is not float):
            raise TypeError("Parameter 'g_parameter' must be an integer (type 'int') or a float.")
        if (type(minimum_quality_measure_value) is not int) and (type(minimum_quality_measure_value) is not float):
            raise TypeError("Parameter 'minimum_quality_measure_value' must be an integer (type 'int') or a float.")
        if minimum_quality_measure_value < 0 or minimum_quality_measure_value > 1 :
            raise ValueError("Parameter minimum_quality_measure_value must be in range [0,1].")
        if type(beam_width) is not int:
            raise TypeError("Parameter 'beam_width' must be an integer (type 'int').")
        if not (beam_width > 0):
            raise ValueError("Width of the beam must be greater than 0.")
        if (write_results_in_file) and (file_path is None):
            raise ValueError(
                "If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        self._g_parameter = g_parameter
        self._minimum_quality_measure_value = minimum_quality_measure_value
        self._beam_width = beam_width
        self._unselected_subgroups = 0
        self._selected_subgroups = 0
        if write_results_in_file:
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None

    def _get_g_parameter(self) -> Union[int,float]:
        return self._g_parameter

    def _get_minimum_quality_measure_value(self) -> Union[int,float]:
        return self._minimum_quality_measure_value

    def _get_beam_width(self) -> int:
        return self._beam_width
    
    def _get_unselected_subgroups(self) -> int : 
        return self._unselected_subgroups

    def _get_selected_subgroups(self) -> int : 
        return self._selected_subgroups
    
    def _get_visited_nodes(self) -> int:
        return self._unselected_subgroups + self._selected_subgroups
    
    g_parameter = property(_get_g_parameter, None, None, "The g parameter used.")
    minimum_quality_measure_value = property(_get_minimum_quality_measure_value, None, None, "The minimum quality measure value threshold.")
    beam_width = property(_get_beam_width, None, None, "The beam width used.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "Number of unselected subgroups after executing the SD algorithm (before executing the 'fit' method, this attribute is 0).")
    selected_subgroups = property(_get_selected_subgroups, None, None, "Number of selected subgroups after executing the SD algorithm (before executing the 'fit' method, this attribute is 0).")
    visited_nodes = property(_get_visited_nodes, None, None, "Number of visited nodes after executing the SD algorithm (before executing the 'fit' method, this attribute is 0).")

    def _sort_set_l(self,set_l, reverse = False, criterion ='completeSelector'):
        """ Method to sort the set of all feasible attribute values (set of features L) generated by the method 'generateSetL'.
            :param set_l: Set of all feasible attribute values (set of features L) to be sorted. This method MODIFIES the input parameter. The elements of the set L MUST BE of type 'Selector' (or subclasses).
            :param reverse: If 'True', set l will be sorted descending/reverse. If 'False', set l will be sorted ascending. By default, False.
            :param criterion: Method used for sorting. Possible values: 'completeSelector', 'byAttribute', 'byOperator', 'byValue'. By default, 'completeSelector'.
            :rtype: list
            :return: the parameter set_L after sorting.
        """
        criterion_available_values = ['completeSelector', 'byAttribute', 'byOperator', 'byValue']
        if type(set_l) is not list:
            raise TypeError("Parameter 'set_L' must be a python list.")

        if type(reverse) is not bool :
            raise TypeError("Parameter 'reverse' must be a boolean.")
            
        if criterion not in criterion_available_values:
            raise ValueError("Parameter 'criterion' is not valid (see documentation).")
        # Sort depend on criterion.
        if criterion == 'completeSelector':
            set_l.sort(reverse=reverse)
        elif criterion == 'byAttribute':
            set_l.sort(reverse=reverse, key=lambda x : x._get_attribute_name())
        elif criterion == 'byOperator':
            set_l.sort(reverse=reverse, key=lambda x : x._get_operator())
        elif criterion == 'byValue':
            set_l.sort(reverse=reverse, key=lambda x : str(x._get_value())) # VERY IMPORTANT: The value of different selectors could be of different types.
        # Return the list after sorting.
        return set_l

    def _generate_set_l(self, pandas_dataframe: pandas.DataFrame, tuple_target_attribute_value:tuple[str,str], binary_attributes=None):
        """Method to generate the set of all feasible attribute values (set of features L) used in SD algorithm.
        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :param tuple_target_attribute_value: Tuple with the name of the target attribute (first element) and with the value of this attribute (second element). EXAMPLE1: ("age", 25). EXAMPLE2: ("class", "Setosa"). It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset,
          (3) it is VERY IMPORTANT to respect the types of the attributes: the value in the tuple (second element) MUST BE comparable with the values of the corresponding attribute in the dataset,
          (4) the value of the target attribute MUST exist in the dataset.
        :param binary_attributes: (OPTIONAL) List of categorical values to be considered as binary. It is VERY IMPORTANT to respect the following conditions:
          (1) binary_attributes must be a list,
          (2) binary_attributes must contain only attributes of pandas_dataframe,
          (3) each attribute of the list must have a maximum of two values.
        :rtype: list
        :return: all feasible attribute values (set of features L) used in SD algorithm (stored in a list).
        """
        if binary_attributes is None:
            binary_attributes = []
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if ( type(tuple_target_attribute_value) is not tuple ):
            raise TypeError("Parameter 'tuple_target_attribute_value' must be a tuple.")
        if (len(tuple_target_attribute_value) != 2):
            raise ValueError("Parameter 'tuple_target_attribute_value' must be of length 2.")
        if type(tuple_target_attribute_value[0]) is not str:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') must be a string.")
        if type(tuple_target_attribute_value[1]) is not str:
            raise ValueError("The name of the target attribute (second element in parameter 'tuple_target_attribute_value') must be a string.")
        if tuple_target_attribute_value[0] not in pandas_dataframe.columns:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') is not an attribute of the input dataset.")
        # Check binary_attributes
        if type(binary_attributes) is not list :
            raise ValueError("Parameter 'binary_attributes' must be a list")

        for i in binary_attributes :
            if i not in list(pandas_dataframe) :
                raise ValueError("Parameter 'binary_attributes' must contain only attributes of 'pandas_dataframe'")
            elif len(pandas_dataframe[i].unique()) > 2 :
                raise ValueError("Parameter 'binary_attributes' must contain only the name of attributes with no more than 2 possible values")
    
        # Variable to store all selectors of set of features L.
        #   - It is very important to AVOID DUPLICATED Selectors. So, we will use a PYTHON DICTIONARY where the key is the selector and the value is None (the value does not matter).
        final_set_l = dict()
        # We generate the set L.
        for column in pandas_dataframe.columns.drop(tuple_target_attribute_value[0]): # Iterate over dataframe column names, except target column name.
            # We check the possible types of the values of the column.
            #   - The type of the strings in a pandas DataFrame is directly 'str'.
            #   - If the element gotten with 'loc' is not 'str', we have to use 'item' method to get the "primitive element" (element of the primitive type).
            # We check the type using pandas API, because all elements of the column are of the same type.
            if is_string_dtype(pandas_dataframe[column]) : 
                if column in binary_attributes :
                    bin_values = pandas_dataframe[column].unique()

                    for value in bin_values :
                        final_set_l[ Selector(column, Operator.EQUAL, value) ] = None
                else :
                   # Crear un filtro booleano para ejemplos positivos y negativos
                    positive_mask = pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]
                    negative_mask = pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1]

                    # Obtener valores únicos de la columna para ejemplos positivos y negativos
                    positive_values = pandas_dataframe.loc[positive_mask, column].unique()
                    negative_values = pandas_dataframe.loc[negative_mask, column].unique()

                    # Agregar selectores para valores positivos y negativos
                    for value in positive_values:
                        final_set_l[Selector(column, Operator.EQUAL, value)] = None

                    for value in negative_values:
                        final_set_l[Selector(column, Operator.NOT_EQUAL, value)] = None

            elif is_float_dtype(pandas_dataframe[column]):
                            # Si el atributo es continuo, obtenemos los ejemplos positivos y negativos.
                    pandas_dataframe_positive_examples = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]]
                    pandas_dataframe_negative_examples = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1]]

                    # Convierte las columnas a matrices NumPy
                    positive_values = pandas_dataframe_positive_examples[column].to_numpy()
                    negative_values = pandas_dataframe_negative_examples[column].to_numpy()

                    # Calcula la suma de todos los pares posibles usando broadcasting
                    sum_matrix = positive_values[:, np.newaxis] + negative_values

                    # Calcula la media de todos los pares posibles y aplana la matriz
                    mean_values = (sum_matrix / 2).flatten()

                    # Aplicar operaciones vectorizadas sobre los valores medios
                    for mean_value in np.unique(mean_values):
                        final_set_l[Selector(column, Operator.LESS_OR_EQUAL, mean_value)] = None
                        final_set_l[Selector(column, Operator.GREATER, mean_value)] = None
            elif is_integer_dtype(pandas_dataframe[column]):
                            # Si el atributo es un entero, obtenemos los ejemplos positivos y negativos.
                pandas_dataframe_positive_examples = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1]]
                positive_values = pandas_dataframe_positive_examples[column].to_numpy()
                pandas_dataframe_negative_examples = pandas_dataframe[pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1]]
                negative_values = pandas_dataframe_negative_examples[column].to_numpy()

                # Generamos todas las combinaciones posibles de valores positivos y negativos usando broadcasting.
                positive_values = positive_values[:, np.newaxis]
                negative_values = negative_values[np.newaxis, :]

                mean_values = (positive_values + negative_values) / 2

                # Aplicar operaciones vectorizadas sobre los valores medios únicos
                for mean_value in np.unique(mean_values):
                    final_set_l[Selector(column, Operator.LESS_OR_EQUAL, mean_value)] = None
                    final_set_l[Selector(column, Operator.GREATER, mean_value)] = None

                # Agregar selectores para valores positivos y negativos
                for positive_value in np.unique(positive_values):
                    final_set_l[Selector(column, Operator.EQUAL, positive_value)] = None

                for negative_value in np.unique(negative_values):
                    final_set_l[Selector(column, Operator.NOT_EQUAL, negative_value)] = None
                        # In variable 'final_set_l', we do not have duplicates. Now, we have to return it as list.
        
        return list(final_set_l)        

    def _obtain_subgroup_parameters(self, pandas_dataframe, subgroup):
            """Internal method to obtain the subgroup parameters (tp, fp, TP and FP) in relation to a dataset.

            It is VERY IMPORTANT to respect the types of the attributes: the value of a selector of the subgroup MUST BE comparable with the value of the corresponding attribute in the dataset.

            :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
              (1) the dataset must be a pandas dataframe,
              (2) the dataset must not contain missing values,
              (3) for each attribute, all its values must be of the same type.
            :param subgroup: Input subgroup.
            :rtype: tuple
            :return: a tuple with the subgroup parameters in this order: (tp, fp, TP, FP).
            """
            if type(pandas_dataframe) is not DataFrame:
                raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
            if not isinstance(subgroup, Subgroup):
                raise TypeError("Parameter 'subgroup' must be of type 'Subgroup' (or subclasses).")
            # We use the "filter" method.
            (bool_Series_description_is_contained_AND_target_match, bool_Series_description_is_contained_AND_target_do_not_match, target_match) = subgroup.filter(pandas_dataframe)
            tp = bool_Series_description_is_contained_AND_target_match.sum()
            fp = bool_Series_description_is_contained_AND_target_do_not_match.sum()
            TP = target_match.sum()
            FP = (~target_match).sum()
            return tp, fp, TP, FP

    def _handle_individual_result(self, individual_result: tuple[Pattern, tuple[str, str], int, int, int, int], quality_measure : QualityMeasure, write:bool) -> float:
        """Private method to handle each individual result generated by the SD algorithm.

        :param individual_result: the individual result which is handled. In this case, it is a subgroup description, a target as a tuple and the subgroup parameters tp, fp, TP and FP.
        """
       # print(individual_result[0])
        # Get the subgroup parameters.
        tp = individual_result[2][0]
        fp = individual_result[2][1]
        TP = individual_result[2][2]
        FP = individual_result[2][3]

        # Compute the quality measure of the frequent pattern along with the target (i.e., the quality measure of the subgroup).
        dict_of_parameters = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.FALSE_POSITIVES: fp,
                              QualityMeasure.TRUE_POPULATION: TP, QualityMeasure.FALSE_POPULATION: FP ,
                              "g" : self._get_g_parameter()}
        quality_measure_value = round((quality_measure.compute(dict_of_parameters)),2)
        
        
        # Add the subgroup only if the quality measure value is greater or equal than the threshold.
        if quality_measure_value >= self._get_minimum_quality_measure_value():
           
            # If applicable, write in the file defined in the __init__ method.
            
            if self._file_path is not None and write:
                quality_measure_qg_value = round(Qg().compute(dict_of_parameters),2)
                # Get the description and the target.
                subgroup_description = individual_result[0]
                target_as_tuple = individual_result[1]  # Attribute name -> target_as_tuple[0], Attribute value -> target_as_tuple[1]
                # Create the selector
                selector = Selector(target_as_tuple[0], Operator.EQUAL, target_as_tuple[1])
                # Create the subgroup.
                subgroup = Subgroup(subgroup_description,selector)
                # Write.
                self._file = open(self._file_path, "a")
                self._file.write(str(subgroup._get_description())+" ; ")
                self._file.write("Quality Measure : " + str(quality_measure.get_name()) + " = " + str(quality_measure_value) + " , " + "Qg = "+str(quality_measure_qg_value)+"; ")
                self._file.write("tp = " + str(tp) + " ; ")
                self._file.write("fp = " + str(fp) + " ; ")
                self._file.write("TP = " + str(TP) + " ; ")
                self._file.write("FP = " + str(FP) + "\n")
                self._file.close()
            # Increment the number of selected subgroups.
            self._selected_subgroups = self._selected_subgroups + 1
        else:  # If the quality measure is not greater or equal, increment the number of unselected subgroups.
            self._unselected_subgroups = self._unselected_subgroups + 1
        return quality_measure_value

    def fit(self, pandas_dataframe: DataFrame, tuple_target_attribute_value: tuple[str,str], binary_attributes = []):
        """Method to run the SD algorithm and generate subgroups.

        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :param tuple_target_attribute_value: Tuple with the name of the target attribute (first element) and with the value of this attribute (second element). EXAMPLE1: ("age", 25). EXAMPLE2: ("class", "Setosa"). It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset,
          (3) it is VERY IMPORTANT to respect the types of the attributes: the value in the tuple (second element) MUST BE comparable with the values of the corresponding attribute in the dataset,
          (4) the value of the target attribute MUST exist in the dataset.
        :rtype: list
        :return: a list of lists with the k best subgroups (k = beam_width) and its quality measures.
        """
        if type(pandas_dataframe) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if ( type(tuple_target_attribute_value) is not tuple ):
            raise TypeError("Parameter 'tuple_target_attribute_value' must be a tuple.")
        if (len(tuple_target_attribute_value) != 2):
            raise ValueError("Parameter 'tuple_target_attribute_value' must be of length 2.")
        if type(tuple_target_attribute_value[0]) is not str:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') must be a string.")
        if tuple_target_attribute_value[0] not in pandas_dataframe.columns:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') is not an attribute of the input dataset.")
        # First,we obtain the set with the all feasible attribute values (set of features L)
        set_l = self._generate_set_l(pandas_dataframe,tuple_target_attribute_value,binary_attributes)
        # Then we will delete the selectors that form subgroups whose support is lower than min_suport
        new_set = []
        for i in set_l :
            subgroup = Subgroup(Pattern([i]), Selector(tuple_target_attribute_value[0], Operator.EQUAL, tuple_target_attribute_value[1]))
            subgroup_parameters = self._obtain_subgroup_parameters(pandas_dataframe, subgroup)
            self._handle_individual_result((Pattern([i]),tuple_target_attribute_value,subgroup_parameters),Support(),False)
            #if subgroup_support >= self._get_minimum_quality_measure_value() : #Improvement that appears in Enrique´s TFG  
            new_set.append(i)
        set_l = new_set
        # Initialize variables Beam and newBeam. IMPORTANT: Different lists with different subgroups.
        #   - Elements are LISTS with this content: [Subgroup, Qg quality measure of the subgroup].
        #   - This means that variables Beam and newBeam are lists of lists.
        #   - At the beginning, all Qg are 0.
        beam = []
        newBeam = []
        for i in range(self._get_beam_width()):
            beam.append([Subgroup(Pattern([]), Selector(tuple_target_attribute_value[0],  Operator.EQUAL, tuple_target_attribute_value[1])), 0])
            newBeam.append([Subgroup(Pattern([]), Selector(tuple_target_attribute_value[0],  Operator.EQUAL, tuple_target_attribute_value[1])), 0])
        # Variable to control if there were improvements in the beam list. Initially, True (to be able to do the first iteration).
        improvements_in_beam = True
        # Main loop (while there are improvements in Beam).
        while improvements_in_beam:
            improvements_in_beam = False # Inside every iteration (and at the beginning), we put it to false.
            for index in range(self._get_beam_width()):
                current_subgroup_in_beam_original = beam[index][0] # The subgroup is the first element in the sublist.
                for l in set_l:
                    # print(l)
                    current_subgroup_in_beam = current_subgroup_in_beam_original.copy()
                    # Add the selector in L to the pattern of subgroup. It is not necessary to make a copy because a Selector is immutable.
                    current_subgroup_in_beam._get_description().add_selector(l)
                    # print("Current : ",current_subgroup_in_beam)
                     
                    # We obtain Qg and support of the new subgroup.
                    current_subgroup_in_beam_parameters = self._obtain_subgroup_parameters(pandas_dataframe, current_subgroup_in_beam)
                    current_subgroup_in_beam_qg = self._handle_individual_result((Pattern([current_subgroup_in_beam]),tuple_target_attribute_value,current_subgroup_in_beam_parameters),Qg(),False)
                    
                    
                    # Update the Qg quality measure (second element in the tuple).
                    beam[index][1] = current_subgroup_in_beam_qg 
                    current_subgroup_in_beam_support = self._handle_individual_result((Pattern([current_subgroup_in_beam]),tuple_target_attribute_value,current_subgroup_in_beam_parameters),Support(),False)
                   
                    
                    # Obtain the worst sublist [subgroup, Qg] of newBeam.
                    worst_sublist_in_newBeam = newBeam[0] # Initially, the worst is the first one.
                    for x in range(1, self._get_beam_width()):
                        current_sublist_in_newBeam = newBeam[x]
                        if (current_sublist_in_newBeam[1] < worst_sublist_in_newBeam[1]):
                            worst_sublist_in_newBeam = current_sublist_in_newBeam
                    
                    # Check quality measures.
                    #print(self._get_minimum_quality_measure_value())
                    #print(current_subgroup_in_beam_support)
                    #print("Support >= MinQMSValue : ",current_subgroup_in_beam_support >= self._get_minimum_quality_measure_value())
                    #print("Support >= MinQMSValue : ",current_subgroup_in_beam_support >= self._get_minimum_quality_measure_value())
                    #print((current_subgroup_in_beam_support >= self._get_minimum_quality_measure_value()) and (current_subgroup_in_beam_qg > worst_sublist_in_newBeam[1]) and [current_subgroup_in_beam,current_subgroup_in_beam_qg] not in newBeam)
                    if (current_subgroup_in_beam_support >= self._get_minimum_quality_measure_value()) and (current_subgroup_in_beam_qg > worst_sublist_in_newBeam[1]) and [current_subgroup_in_beam,current_subgroup_in_beam_qg] not in newBeam :

                        # The worst subgroup (sublist, in this case) in newBeam is replaced by 'b' (current_subg_in_beam).
                        self._handle_individual_result((Pattern([current_subgroup_in_beam]),tuple_target_attribute_value,current_subgroup_in_beam_parameters),Support(),True)
                        worst_sublist_in_newBeam[0] = current_subgroup_in_beam.copy()
                        worst_sublist_in_newBeam[1] = beam[index][1]
                        
                        # Reorder newBeam by Qg (second element of the sublist).
                        newBeam.sort(key = lambda x : x[1], reverse = True)
                        
                        # If the condition of the 'if' is true, there will be improvements in the beam.
                        improvements_in_beam = True
            # beam <- newBeam
            for index in range(self._get_beam_width()):
                beam[index][0] = newBeam[index][0].copy()
                beam[index][1] = newBeam[index][1]
        return beam
