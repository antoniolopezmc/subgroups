# -*- coding: utf-8 -*-

# Contributors:
#    Álvaro Riquelme Tornel <alvaroriquelmetornel@gmail.com>

"""This file contains the implementation of the SD algorithm.
"""
import pandas
from pandas import DataFrame
from subgroups.algorithms.algorithm import Algorithm
from subgroups.quality_measures import Qg, Support
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import EmptyDatasetError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from typing import Union


def _delete_subgroup_parameters_from_a_dictionary(dict_of_parameters: dict[str, Union[int, float]]):
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

def _get_index_dictionary(dataset:pandas.DataFrame):
    """Auxiliary method to calculate the index dictionary, a data structure that maps each column name of a pandas dataframe into its integer value.

    :param dataset: Input dataset. It is VERY IMPORTANT to respect the following conditions:
      (1) the dataset must be a pandas dataframe,
      (2) the dataset must not contain missing values,
      (3) for each attribute, all its values must be of the same type.
    :rtype: dict
    :return: the index dictionary for the given pandas dataframe.
    """
    if type(dataset) is not DataFrame :
        raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
    if (dataset.shape[0] == 0) or (dataset.shape[1] == 0) :
        raise EmptyDatasetError("The input dataset is empty.")
    i = 0
    index_dict = {}
    for column in dataset.columns :
        index_dict.update({column : i})
        i = i + 1
    return index_dict




class SD(Algorithm):
    """This class represents the algorithm SD (Subgroup Discovery).

    IMPORTANT NOTE: You must not access directly to the attributes of the objects. You must use the corresponding methods.

    This class represents the SDMap algorithm. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
    :param minimum_quality_measure_value: the minimum quality measure value threshold.
    :param min_support: Minimum support that need to have a subgroup to be considered. Value in form of PROPORTION (between 0 and 1).
    :param beam_width: Width of the beam.
    :param quality_measure: the quality measure which is used.
    :param additional_parameters_for_the_quality_measure: if the quality measure passed by parameter needs more parameters apart from tp, fp, TP and FP to be computed, they need to be specified here.
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """

   # __slots__ =( "g_parameter,_minimum_quality_measure_value","_quality_measure","_additional_parameters_for_the_quality_measure", "beam_width","_unselected_subgroups", "_selected_subgroups", "_file_path", "_file")
    def __init__(self, g_parameter: Union[int,float], minimum_quality_measure_value: Union[int,float],  beam_width : int = 20 ,write_results_in_file : bool = False, file_path : Union[str, None] = None) -> None:
        """Method to initialize an object of type 'AlgorithmSD'.
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
        self._beamWidth = beam_width
        #self._quality_measure = quality_measure
        self._unselected_subgroups = 0
        self._selected_subgroups = 0
        #self._additional_parameters_for_the_quality_measure = additional_parameters_for_the_quality_measure.copy()
        #_delete_subgroup_parameters_from_a_dictionary(self._additional_parameters_for_the_quality_measure)
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
        return self._beamWidth

    def _get_quality_measure(self) -> QualityMeasure :
        return self._quality_measure
    
    def _get_unselected_subgroups(self) -> int : 
        return self._unselected_subgroups

    def _get_selected_subgroups(self) -> int : 
        return self._selected_subgroups
    
    def _additional_parameters_for_the_quality_measure(self) -> dict :
        return self._additional_parameters_for_the_quality_measure
    
    def _get_file(self) -> Union[int,float]:
        return self._file

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
        if (pandas_dataframe.shape[0] == 0) or (pandas_dataframe.shape[1] == 0):
            raise EmptyDatasetError("The input dataset is empty.")
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
        columns_without_target = pandas_dataframe.columns[pandas_dataframe.columns != tuple_target_attribute_value[0]]
        for column in columns_without_target: # Iterate over dataframe column names, except target column name.
            # We check the possible types of the values of the column.
            #   - The type of the strings in a pandas DataFrame is directly 'str'.
            #   - If the element gotten with 'loc' is not 'str', we have to use 'item' method to get the "primitive element" (element of the primitive type).
            if type(pandas_dataframe[column].iloc[0]) is str: # Only check the first element, because all elements of the column are of the same type.
                if column in binary_attributes :
                    bin_values = pandas_dataframe[column]
                    for value in bin_values :
                        final_set_l[ Selector(column, Operator.EQUAL, value) ] = None
                else :
                    index_dict = _get_index_dictionary(pandas_dataframe)
                    for row in pandas_dataframe.itertuples(False):
                        if row[index_dict[tuple_target_attribute_value[0]]] == tuple_target_attribute_value[1]: # If the example/row is positive.
                            final_set_l[ Selector(column, Operator.EQUAL, row[index_dict[column]]) ] = None
                        elif row[index_dict[tuple_target_attribute_value[0]]] != tuple_target_attribute_value[1]: # If the example/row is negative.
                            final_set_l[ Selector(column, Operator.NOT_EQUAL, row[index_dict[column]]) ] = None
            elif (type(pandas_dataframe[column].iloc[0].item()) is float):
                    # If the attribute is continuous, we have to get the positive examples and the negative examples.
                    pandas_dataframe_positive_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1] ]
                    pandas_dataframe_negative_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1] ]
                    # We generate all possible pairs with the positive and negative examples.
                    index_dict_positive_examples = _get_index_dictionary(pandas_dataframe_positive_examples)
                    index_dict_negative_examples = _get_index_dictionary(pandas_dataframe_negative_examples)
                    for positive_example_row in pandas_dataframe_positive_examples.itertuples(False):
                        for negative_example_row in pandas_dataframe_negative_examples.itertuples(False):
                            final_set_l[ Selector(column, Operator.LESS_OR_EQUAL, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                            final_set_l[ Selector(column, Operator.GREATER, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
            elif (type(pandas_dataframe[column].iloc[0].item()) is int):
                # If the attribute is an integer, we have to get the positive examples and the negative examples.
                pandas_dataframe_positive_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1] ]
                pandas_dataframe_negative_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1] ]
                # We generate all possible pairs with the positive and negative examples.
                index_dict_positive_examples = _get_index_dictionary(pandas_dataframe_positive_examples)
                index_dict_negative_examples = _get_index_dictionary(pandas_dataframe_negative_examples)
                for positive_example_row in pandas_dataframe_positive_examples.itertuples(False):
                    for negative_example_row in pandas_dataframe_negative_examples.itertuples(False):
                        final_set_l[ Selector(column, Operator.LESS_OR_EQUAL, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Operator.GREATER, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Operator.EQUAL, positive_example_row[index_dict_positive_examples[column]]) ] = None
                        final_set_l[ Selector(column, Operator.NOT_EQUAL, negative_example_row[index_dict_negative_examples[column]]) ] = None
        # In variable 'final_set_l', we do not have duplicates. Now, we have to return it as list.
        return list(final_set_l)        

    def _obtain_basic_metrics(self, pandas_dataframe, subgroup):
            """Internal method to obtain the basic metrics (tp, fp, TP and FP) of a subgroup in a dataset.

            It is VERY IMPORTANT to respect the types of the attributes: the value of a selector of the subgroup MUST BE comparable with the value of the corresponding attribute in the dataset.

            :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
              (1) the dataset must be a pandas dataframe,
              (2) the dataset must not contain missing values,
              (3) for each attribute, all its values must be of the same type.
            :param subgroup: Input subgroup.
            :rtype: tuple
            :return: a tuple with the basic metrics in this order: (tp, fp, TP, FP).
            """
            if type(pandas_dataframe) is not DataFrame:
                raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
            if (pandas_dataframe.shape[0] == 0) or (pandas_dataframe.shape[1] == 0):
                raise EmptyDatasetError("The input dataset is empty.")
            if not isinstance(subgroup, Subgroup):
                raise TypeError("Parameter 'subgroup' must be of type 'Subgroup' (or subclasses).")
            # We need to use the condition of the subgroup (Pattern) and the target variable (Selector) separatly.
            subgroup_condition = subgroup._get_description()
            subgroup_target = subgroup._get_target()
            # We initialize the basic metrics that we want to obtain.
            tp = 0
            fp = 0
            TP = 0
            FP = 0
            # EXTREMELY IMPORTANT: DOCUMENTATION OF PANDAS: ITERROWS.
            #   - Because iterrows returns a Series for each row, it does NOT preserve dtypes across the rows (dtypes are preserved across columns for DataFrames).
            #   - This is important because types in Selector are primitive types of python (and not pandas or numpy types).
            for index, row in pandas_dataframe.iterrows():
                # FIRST: we check the condition of the subgroup.
                subgroup_condition_and_row_match = True  # Variable to control if the condition of the subgroup and the row match. Initially, yes.
                index_in_subgroup_condition = 0  # Index over the selectors of the condition of the subgroup.
                while (index_in_subgroup_condition < len(subgroup_condition)) and (
                subgroup_condition_and_row_match):  # Iterate over the selectors of the condition of the subgroup.
                    current_selector = subgroup_condition.get_list_of_selectors()[index_in_subgroup_condition]
                    try:  # IMPORTANT: If the attribute of the selector is not in the dataset, an exception of pandas (KeyError) will be raised.
                        # If one of the selectors of the condition of the subgroup does not match, the condition of the subgroup does not match (and we can go to the next row).
                        subgroup_condition_and_row_match = current_selector.match(current_selector._get_attribute_name(),
                                                                                  row[current_selector._get_attribute_name()])
                    except KeyError as e:
                        subgroup_condition_and_row_match = False
                    index_in_subgroup_condition = index_in_subgroup_condition + 1
                # SECOND: we check the target variable of the subgroup.
                try:
                    subgroup_target_and_row_match = subgroup_target.match(subgroup_target._get_attribute_name(),
                                                                          row[subgroup_target._get_attribute_name()])
                except KeyError as e:
                    subgroup_target_and_row_match = False
                # FINALLY, we check the results.
                if subgroup_condition_and_row_match and subgroup_target_and_row_match:
                    tp = tp + 1
                if subgroup_condition_and_row_match and (not subgroup_target_and_row_match):
                    fp = fp + 1
                if subgroup_target_and_row_match:
                    TP = TP + 1
                if not subgroup_target_and_row_match:
                    FP = FP + 1
            return tp, fp, TP, FP

    def _handle_individual_result(self, individual_result: tuple[Pattern, tuple[str, str], int, int, int, int]) -> float:
        """Private method to handle each individual result generated by the SDMap algorithm.

        :param individual_result: the individual result which is handled. In this case, it is a subgroup description, a target as a tuple and the subgroup parameters tp, fp, TP and FP.
        """
        # Get the subgroup parameters.
        tp = individual_result[2][0]
        fp = individual_result[2][1]
        TP = individual_result[2][2]
        FP = individual_result[2][3]

        # Compute the quality measure of the frequent pattern along with the target (i.e., the quality measure of the subgroup).
        dict_of_parameters = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.FALSE_POSITIVES: fp,
                              QualityMeasure.TRUE_POPULATION: TP, QualityMeasure.FALSE_POPULATION: FP ,
                              "g" : self._get_g_parameter()}
       # dict_of_parameters.update(self._get_additional_parameters_for_the_quality_measure())
        quality_measure_value = Support().compute(dict_of_parameters)
        # Add the subgroup only if the quality measure value is greater or equal than the threshold.
        if quality_measure_value >= self._get_minimum_quality_measure_value():
            # If applicable, write in the file defined in the __init__ method.
            if self._file_path is not None:
                
                # Get the description and the target.
                subgroup_description = individual_result[0]
                target_as_tuple = individual_result[1]  # Attribute name -> target_as_tuple[0], Attribute value -> target_as_tuple[1]
                # Create the selector
                selector = Selector(target_as_tuple[0], Operator.EQUAL, target_as_tuple[1])
                # Create the subgroup.
                subgroup = Subgroup(subgroup_description,selector)
                # Write.
                self._file = open(self._file_path, "w")
                self._file.write(str(subgroup) + " ; ")
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

    def fit(self, pandas_dataframe: DataFrame, tuple_target_attribute_value: tuple[str,str]):
        """Method to run the algorithm SD and generate subgroups.

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
        if (pandas_dataframe.shape[0] == 0) or (pandas_dataframe.shape[1] == 0):
            raise EmptyDatasetError("The input dataset is empty.")
        if ( type(tuple_target_attribute_value) is not tuple ):
            raise TypeError("Parameter 'tuple_target_attribute_value' must be a tuple.")
        if (len(tuple_target_attribute_value) != 2):
            raise ValueError("Parameter 'tuple_target_attribute_value' must be of length 2.")
        if type(tuple_target_attribute_value[0]) is not str:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') must be a string.")
        if tuple_target_attribute_value[0] not in pandas_dataframe.columns:
            raise ValueError("The name of the target attribute (first element in parameter 'tuple_target_attribute_value') is not an attribute of the input dataset.")
        # First,we obtain the set with the all feasible attribute values (set of features L)
        set_l = self._generate_set_l(pandas_dataframe,tuple_target_attribute_value)
        # Then we will delete the selectors that form subgroups whose support is lower than min_suport
        new_set = []
        for i in set_l :
            subgroup = Subgroup(Pattern([i]), Selector(tuple_target_attribute_value[0], Operator.EQUAL, tuple_target_attribute_value[1]))
            subgroup_metrics = self._obtain_basic_metrics(pandas_dataframe, subgroup)
            subgroup_support = self._handle_individual_result((Pattern([i]),tuple_target_attribute_value,subgroup_metrics))
            if subgroup_support >= self._get_minimum_quality_measure_value() : 
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
                    current_subgroup_in_beam = current_subgroup_in_beam_original.copy()
                    current_subgroup_in_beam._get_description().add_selector(l) # Add the selector in L to the pattern of subgroup. It is not necessary to make a copy because a Selector is immutable.
                    # We obtain Qg and support of the new subgroup.
                    current_subgroup_in_beam_BasicMetrics = self._obtain_basic_metrics(pandas_dataframe, current_subgroup_in_beam)
                    current_subgroup_in_beam_qg = Qg().compute({QualityMeasure.TRUE_POSITIVES : current_subgroup_in_beam_BasicMetrics[0], QualityMeasure.FALSE_POSITIVES : current_subgroup_in_beam_BasicMetrics[1],"g":self._get_g_parameter()})
                    beam[index][1] = current_subgroup_in_beam_qg # Update the Qg quality measure (second element in the tuple).
                    current_subgroup_in_beam_support = Support().compute({QualityMeasure.TRUE_POSITIVES : current_subgroup_in_beam_BasicMetrics[0], QualityMeasure.TRUE_POPULATION : current_subgroup_in_beam_BasicMetrics[2], QualityMeasure.FALSE_POPULATION : current_subgroup_in_beam_BasicMetrics[3]})
                    # Obtain the worst sublist [subgroup, Qg] of newBeam.
                    worst_sublist_in_newBeam = newBeam[0] # Initially, the worst is the first one.
                    for x in range(1, self._get_beam_width()):
                        current_sublist_in_newBeam = newBeam[x]
                        if (current_sublist_in_newBeam[1] < worst_sublist_in_newBeam[1]):
                            worst_sublist_in_newBeam = current_sublist_in_newBeam
                    # Check quality measures.
                    if (current_subgroup_in_beam_support >= self._get_minimum_quality_measure_value()) and (current_subgroup_in_beam_qg > worst_sublist_in_newBeam[1]) and [current_subgroup_in_beam,current_subgroup_in_beam_qg] not in newBeam :
                        # The worst subgroup (sublist, in this case) in newBeam is replaced by 'b' (current_subg_in_beam).
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
