# -*- coding: utf-8 -*-

# Contributors:
#    Álvaro Riquelme Tornel <alvaroriquelmetornel@gmail.com>

"""This file contains the implementation of the CN2SD algorithm.
"""
import pandas
from pandas import DataFrame
from subgroups.algorithms.algorithm import Algorithm
from subgroups.quality_measures import WRAcc
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import EmptyDatasetError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from math import inf, isinf
from typing import Union

def _get_index_dictionary( dataset):
        """Auxiliary method to calculate the index dictionary, a data structure that maps each column name of a pandas dataframe into its integer value.

        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
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



class CN2SD(Algorithm):
    """This class represents the algorithm SD (Subgroup Discovery).

    IMPORTANT NOTE: You must not access directly to the attributes of the objects. You must use the corresponding methods.

    This class represents the SDMap algorithm. Two threshold types could be used: (1) the true positives tp and the false positives fp separately or (2) the subgroup description size n (n = tp + fp). This means that: (1) if 'minimum_tp' and 'minimum_fp' have a value of type 'int', 'minimum_n' must be None; and (2) if 'minimum_n' has a value of type 'int', 'minimum_tp' and 'minimum_fp' must be None.
    :param min_support: Minimum support that need to have a subgroup to be considered. Value in form of PROPORTION (between 0 and 1).
    :param beam_width: Width of the beam.
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """

   # __slots__ =( "beam_width","_unselected_subgroups", "_selected_subgroups", "_file_path", "_file")
    def __init__(self, weighting_scheme : str, max_rule_length = inf ,gamma: Union[int,float] = -1,  beam_width : int = 20 ,write_results_in_file : bool = False, file_path : Union[str, None] = None) -> None:
        """Method to initialize an object of type 'AlgorithmSD'.
        """
        if (type (gamma) is not int) and (type(gamma) is not float):
            raise TypeError("Parameter 'g_parameter' must be an integer (type 'int') or a float.")

        if type(weighting_scheme) is not str :
            raise TypeError("Parameter 'weighting_scheme' must be a string")
        if not (weighting_scheme == 'aditive' or weighting_scheme == 'multiplicative'):
            raise TypeError("Parameter 'weighting_scheme' must be 'aditive' or 'multiplicative'.")
        if (not (weighting_scheme == 'multiplicative')) and (gamma !=-1) :
            raise TypeError("Parameter 'gamma' is unnecesary for the "+weighting_scheme+" weighting scheme.")
        if (weighting_scheme == 'multiplicative') and (gamma < 0) and (gamma > 1) :
            raise ValueError("Parameter 'gamma' must be in range [0,1].")
        
        if type(beam_width) is not int:
            raise TypeError("Parameter 'beam_width' must be an integer (type 'int').")
        if not (beam_width > 0):
            raise ValueError("Width of the beam must be greater than 0.")
        
        if (isinf(max_rule_length) and max_rule_length > 0) :
            None # Do nothing, since it is the default value (positive infinite)          
        else :
            if type(max_rule_length) is not int :
                raise TypeError("Parameter 'max_rule_length' must be an integer (type 'int').")
            if max_rule_length < 1 :
                raise TypeError("Parameter 'max_rule_length' must be greater than 0.")

        if (write_results_in_file) and (file_path is None):
            raise ValueError(
                "If the parameter 'write_results_in_file' is True, the parameter 'file_path' must not be None.")
        self._gamma = gamma
        self._beamWidth = beam_width
        self._weighting_scheme = weighting_scheme
        self._max_rule_length = max_rule_length
        self._unselected_subgroups = 0
        self._selected_subgroups = 0
        
        if write_results_in_file:
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None



    def _get_gamma(self) -> Union[int,float]:
        return self._gamma

    def _get_beam_width(self) -> int:
        return self._beamWidth

    def _get_weighting_scheme(self) -> str : 
        return self._weighting_scheme
    
    def _get_max_rule_length(self) -> str : 
        return self._max_rule_length
    
    def _get_unselected_subgroups(self) -> int : 
        return self._unselected_subgroups

    def _get_selected_subgroups(self) -> int : 
        return self._selected_subgroups
    
    def _get_file(self) -> Union[int,float]:
        return self._file

    def fit(self, dataset : DataFrame, target_attribute : str , binary_attributes = []) :
        """Method to run the algorithm CN2 and generate subgroups considering all the values of the target attribute.

        :type dataset: pandas.DataFrame
        :param dataset: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :type target_attribute: str
        :param target_attribute: The name of the target attribute. It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset.
        :type binary_attributes: list
        :param binary_attributes: (OPTIONAL) List of categorical values to be considered as binary. It is VERY IMPORTANT to respect the following conditions:
          (1) binary_attributes must be a list,
          (2) binary_attributes must contain only attributes of pandas_dataframe,
          (3) each attribute of the list must have a maximum of two values.
        :rtype: list
        :return: a list of lists with the k best subgroups (k = beam_width) and its quality measures.
        """
        
        # Check if the parameter 'dataset' is correct
        if type(dataset) is not DataFrame :
            raise TypeError("Parameter 'dataset' must be a pandas DataFrame.")
        if (dataset.shape[0] == 0) or (dataset.shape[1] == 0) :
            raise EmptyDatasetError("The input dataset is empty.")
        
        # Check if the parameter 'target_attribute' is correct
        if  type(target_attribute) is not str :
            raise TypeError("Parameter 'target_attribute' must be string.")
        if target_attribute not in dataset.columns:
            raise ValueError("The name of the target attribute (named "+ target_attribute+") is not an attribute of the input dataset.")
        
        # Check binary_attributes
        if type(binary_attributes) is not list :
            raise TypeError("Parameter 'binary_attributes' must be a list")
        for i in binary_attributes :
            if i not in list(dataset) :
                raise ValueError("Parameter 'binary_attributes' must contain only attributes of 'dataset'")
            elif len(dataset[i].unique()) > 2 :
                raise ValueError("Parameter 'binary_attributes' must contain only the name of attributes with no more than 2 possible values")
   
        # Initialization.     
        # List with the weight of each row of each item (row) of the dataset. Initially it is 1.
        rule_list = []       
        # Get all the feasible values of a class
        target_values = dataset[target_attribute].unique()
        
        for c in target_values :
            subgroup_class_c = self._fit_one_class(dataset, (target_attribute, c), binary_attributes = binary_attributes)
            for i, quality in subgroup_class_c:
                rule_list.append((i,quality))
              
        return rule_list
    
    def _fit_one_class(self, dataset, target_value, weights = None, binary_attributes = []) :
        """Method to run the algorithm CN2 and generate subgroups considering a value for the target attribute.

        :type dataset: pandas.DataFrame
        :param dataset: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :type target_value: tuple
        :param target_value: Tuple with the name of the target attribute (first element) and with the value of this attribute (second element). EXAMPLE1: ("age", 25). EXAMPLE2: ("class", "Setosa"). It is VERY IMPORTANT to respect the following conditions:
          (1) the name of the target attribute MUST be a string,
          (2) the name of the target attribute MUST exist in the dataset,
          (3) it is VERY IMPORTANT to respect the types of the attributes: the value in the tuple (second element) MUST BE comparable with the values of the corresponding attribute in the dataset,
          (4) the value of the target attribute MUST exist in the dataset.
        :type weights: list
        :param weights: List containing the weights of each transaction of the database. If not set, the weight of each item will be 1. The following condition must be respected:
          (1) the name of the target attribute MUST be a list,
          (2) the length of the list attribute MUST be the same that the number of rows of the dataset,
          (3) the elements of the list should be numbers (int or float) in the range [0,1].
        :type binary_attributes: list
        :param binary_attributes: (OPTIONAL) List of categorical values to be considered as binary. It is VERY IMPORTANT to respect the following conditions:
          (1) binary_attributes must be a list,
          (2) binary_attributes must contain only attributes of pandas_dataframe,
          (3) each attribute of the list must have a maximum of two values.
        :rtype: list
        :return: a list of lists with the k best subgroups (k = beam_width) and its quality measures.
        """
        
        # Check if the parameter 'dataset' is correct
        if type(dataset) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if (dataset.shape[0] == 0) or (dataset.shape[1] == 0):
            raise EmptyDatasetError("The input dataset is empty.")
        
        # Check if the parameter 'target_value' is correct
        if (type(target_value) is not tuple ) :
            raise TypeError("Parameter 'target_value' must be a tuple.")
        if (len(target_value) != 2):
            raise ValueError("Parameter 'target_value' must be of length 2.")
        if type(target_value[0]) is not str:
            raise ValueError("The name of the target attribute (first element of the parameter 'target_value') must be a string.")
        if target_value[0] not in dataset.columns:
            raise ValueError("The name of the target attribute (first element of the parameter 'target_value') is not an attribute of the input dataset.")

        #Check if the parameter 'weights' is correct
        if (weights is None) :
            weights = [1] * len(dataset.index)
        else :
            if type(weights) is not list :
                raise TypeError("Parameter 'weights' must be a list")
            if len(weights) != len(dataset.index) : 
                raise TypeError("Parameter 'weights' must have the same number of elements that rows in the dataset")
            for i in weights :
                if (type(i) is int or type(i) is float) and (i > 0 and i < 1) :
                    raise TypeError("Parameter 'weights': The elements of the list must be int or float in range [0,1]")
        
        # Check binary_attributes
        if type(binary_attributes) is not list :
            raise ValueError("Parameter 'binary_attributes' must be a list")
        for i in binary_attributes :
            if i not in list(dataset) :
                raise ValueError("Parameter 'binary_attributes' must contain only attributes of 'dataset'")
            elif len(dataset[i].unique()) > 2 :
                raise ValueError("Parameter 'binary_attributes' must contain only the name of attributes with no more than 2 possible values")
   
        # Initialization
        selector_list = self._generate_set_l(dataset, target_value, binary_attributes= binary_attributes) 
        subgroup_list = []
        while True :
            best_condition, quality = self._find_best_condition_(dataset, weights, target_value, selector_list)
            if best_condition != Pattern([]) : 
                # We build a subgroup  with the best condition and add it to the list
                subgroup = Subgroup(best_condition, Selector(target_value[0], Operator.EQUAL, target_value[1]))
                if subgroup not in [[ i for i, j in subgroup_list ], [ j for i, j in subgroup_list ]][0]  :
                    subgroup_list.append((subgroup, quality))
                
                # Apply the covering algorithm
                # First, we need to get the association between pandas indexing and array indexing
                index = _get_index_dictionary(dataset)  
                if self._get_weighting_scheme() == 'aditive' :
                    # Aditive covering algorithm
                    i = 0
                    for row in dataset.itertuples(False) :
                        if subgroup.match_element(row, index) :
                            if weights[i] > 0:
                                weights[i] = 1/(1/weights[i] + 1)
                                if weights[i] < 0.1 :
                                    weights[i] = 0
                        i = i + 1
                
                elif self._get_weighting_scheme() == 'multiplicative' :
                    # Multiplicative covering algorithm (using gamma)
                    i = 0
                    for row in dataset.itertuples(False) :
                        if subgroup.match_element(row, index) :
                            weights[i] = weights[i] * self._get_gamma()
                            if weights[i] < 0.1 :
                                weights[i] = 0
                        i = i + 1
            else :
                break
        return subgroup_list
    
    def _find_best_condition_(self, dataset, weights, target_value, selector_list):
        target_selector = Selector(target_value[0], Operator.EQUAL, target_value[1])
        # List of potential conditions for the induced subgroup (type = list of Pattern).
        # It should be initialized as empty, but if we do so, we won't be able to iterate over it the first time
        # Being so, we decided to put and empty condition (empty Pattern)
        beam = [Pattern([])]
        # Best condition found (type = Pattern). Initialized as empty             
        best_condition = Pattern([])
        # WRAcc associated to the best condition. Initially 0, since WRAcc([] -> target) = 0
        best_WRAcc = 0
        size = 0
        while True :
            new_beam = []
            # Create new_beam = x^y, where x belongs to beam and y belongs to the set of all possible selectors
            for b in beam :
                for selector in selector_list :
                    new_b = b.copy()
                    new_b.add_selector(selector)
                    new_b_metrics = self._obtain_basic_metrics(dataset, weights, Subgroup(new_b, target_selector))
                    new_b_WRAcc = self._handle_individual_result((new_b,target_value,new_b_metrics),best_WRAcc)
                   #dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : new_b_metrics[0], QualityMeasure.FALSE_POSITIVES : new_b_metrics[1], QualityMeasure.TRUE_POPULATION : new_b_metrics[2], QualityMeasure.FALSE_POPULATION : new_b_metrics[3]}
                   #new_b_WRAcc = WRAcc().compute(dict_of_parameters)
                    if new_b not in beam and new_b not in new_beam and new_b_WRAcc != 0:
                        # Do an ordered insertion with some characteristics. Not specified in the pseudocode, but it will improve the efficiency:
                        #    Just add the subgroup new_b to new_beam if it will improve new_beam or the length of new_beam is lower than the user specified maximum beam width
                        i = 0
                        while i < len(new_beam) :
                            i_metrics = self._obtain_basic_metrics(dataset, weights, Subgroup(new_beam[i], target_selector))
                            #dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : i_metrics[0], QualityMeasure.FALSE_POSITIVES : i_metrics[1], QualityMeasure.TRUE_POPULATION : i_metrics[2], QualityMeasure.FALSE_POPULATION : i_metrics[3]}
                            #i_WRAcc = WRAcc().compute(dict_of_parameters)
                            i_WRAcc = self._handle_individual_result((new_beam[i],target_value,i_metrics),best_WRAcc)
                            if new_b_WRAcc > i_WRAcc :
                                break
                            i = i + 1
                        new_beam.insert(i,new_b)
                        if len(new_beam) > self._get_beam_width() :
                            new_beam.pop(self._get_beam_width())

            # Remove from new_beam the elements in beam
            # Done while iterating
            
            # Remove from new_beam the null elements (ex. age = 5 and age = 7)
            # Not yet implemented. Probably another possibility will be studied, since these calculations are quite complex
            # The solution taken right now consists on ignoring the subgroups with WRAcc <= 0 (done while iterating)
            # If the best element of the new beam (if there is one) is better that our best condition so forth,
            # We will replace the best condition by this element. This element is the first, since new_beam is ordered
            # according to its WRAcc    
            if new_beam != [] :
                new_beam_best_metrics = self._obtain_basic_metrics(dataset, weights, Subgroup(new_beam[0], target_selector))
                new_beam_best_WRAcc = self._handle_individual_result((new_beam[0],target_value,new_beam_best_metrics),best_WRAcc)
                if new_beam_best_WRAcc > best_WRAcc :
                    best_condition = new_beam[0]
                    best_WRAcc = new_beam_best_WRAcc
            
            # Remove the worst elements in new_beam until its size == beam_width (user-defined size of the beam)
            new_beam = new_beam[:self._get_beam_width()]      
              
            # Let beam be the new_beam  
            beam = new_beam
            size = size + 1
            
            # Repeat until no elements in beam
            if beam == [] or size >= self._get_max_rule_length() :
                break
        
        return (best_condition, best_WRAcc)
      
    def _generate_set_l(self, pandas_dataframe, tuple_target_attribute_value, binary_attributes = []):
        """Method to generate the set of all feasible attribute values (set of features L) used in SD algorithm.

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
        :return: all feasible attribute values (set of features L) used in SD algorithm (stored in a list).
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
        # Variable to store all selectors of set of features L.
        #   - It is very important to AVOID DUPLICATED Selectors. So, we will use a PYTHON DICTIONARY where the key is the selector and the value is None (the value does not matter).
        final_set_l = dict()
        # We generate the set L.
        columns_without_target = pandas_dataframe.columns[pandas_dataframe.columns != tuple_target_attribute_value[0]]
        first_element_index = pandas_dataframe.index[0]
        for column in columns_without_target: # Iterate over dataframe column names, except target column name.
            # We check the possible types of the values of the column.
            #   - The type of the strings in a pandas DataFrame is directly 'str'. 
            #   - If the element gotten with 'loc' is not 'str', we have to use 'item' method to get the "primitive element" (element of the primitive type).
            if (type(pandas_dataframe[column].iloc[0]) is str): # Only check the first element, because all elements of the column are of the same type.
                if column in binary_attributes :
                    bin_values = pandas_dataframe[column]
                    for value in bin_values :
                        final_set_l[Selector(column, Operator.EQUAL, value) ] = None
                else :
                    index_dict = _get_index_dictionary(pandas_dataframe)
                    for row in pandas_dataframe.itertuples(False):
                        if (row[index_dict[tuple_target_attribute_value[0]]] == tuple_target_attribute_value[1]): # If the example/row is positive.
                            final_set_l[Selector(column, Operator.EQUAL, row[index_dict[column]]) ] = None
                        elif (row[index_dict[tuple_target_attribute_value[0]]] != tuple_target_attribute_value[1]): # If the example/row is negative.
                            final_set_l[Selector(column, Operator.NOT_EQUAL, row[index_dict[column]]) ] = None
            elif (type(pandas_dataframe[column].iloc[0].item()) is float):
                # If the attribute is continuous, we have to get the positive examples and the negative examples.
                pandas_dataframe_positive_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1] ]
                pandas_dataframe_negative_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1] ]
                # We generate all possible pairs with the positive and negative examples.
                index_dict_positive_examples = self._get_index_dictionary(pandas_dataframe_positive_examples)
                index_dict_negative_examples = self._get_index_dictionary(pandas_dataframe_negative_examples)
                for positive_example_row in pandas_dataframe_positive_examples.itertuples(False):
                    for negative_example_row in pandas_dataframe_negative_examples.itertuples(False):
                        final_set_l[ Selector(column, Operator.LESS_OR_EQUAL, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Operator.GREATER, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
            elif (type(pandas_dataframe[column].iloc[0].item()) is int):
                # If the attribute is an integer, we have to get the positive examples and the negative examples.
                pandas_dataframe_positive_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1] ]
                pandas_dataframe_negative_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1] ]
                # We generate all possible pairs with the positive and negative examples.
                index_dict_positive_examples = self._get_index_dictionary(pandas_dataframe_positive_examples)
                index_dict_negative_examples = self._get_index_dictionary(pandas_dataframe_negative_examples)
                for positive_example_row in pandas_dataframe_positive_examples.itertuples(False):
                    for negative_example_row in pandas_dataframe_negative_examples.itertuples(False):
                        final_set_l[ Selector(column, Operator.LESS_OR_EQUAL, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Operator.GREATER, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Operator.EQUAL, positive_example_row[index_dict_positive_examples[column]]) ] = None
                        final_set_l[ Selector(column, Operator.NOT_EQUAL, negative_example_row[index_dict_negative_examples[column]]) ] = None
        # In variable 'final_set_l', we do not have duplicates. Now, we have to return it as list.
        return list(final_set_l)        
       
    def _obtain_basic_metrics(self, dataset, weights, subgroup): 
        """Internal method to get the modified WRAcc of a subgroup given a dataset with its rows weighted (as described by Lavrac, 2004)

        It is VERY IMPORTANT to respect the types of the attributes: the value of a selector of the subgroup MUST BE comparable with the value of the corresponding attribute in the dataset.
        
        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :type weights: list
        :param weights: List containing the weights of each transaction of the database. If not set, the weight of each item will be 1. The following condition must be respected:
          (1) the name of the target attribute MUST be a list,
          (2) the length of the list attribute MUST be the same that the number of rows of the dataset,
          (3) the elements of the list should be numbers (int or float) in the range [0,1].
        :type subgroup: Subgroup
        :param subgroup: Input subgroup.
        :rtype: float
        :return: The modified WRAcc of the subgroup for the weighted database.
        """
        # Check if the parameter 'dataset' is correct
        if type(dataset) is not DataFrame:
            raise TypeError("Parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if (dataset.shape[0] == 0) or (dataset.shape[1] == 0):
            raise EmptyDatasetError("The input dataset is empty.")
        
        #Check if the parameter 'weights' is correct
        if (weights is None) :
            weights = [1] * len(dataset.index)
        else :
            if type(weights) is not list :
                raise TypeError("Parameter 'weights' must be a list")
            if len(weights) != len(dataset.index) : 
                raise TypeError("Parameter 'weights' must have the same number of elements that rows in the dataset")
            for i in weights :
                if not ((type(i) is int or type(i) is float) and (i >= 0 and i <= 1)) :
                    raise TypeError("Parameter 'weights': The elements of the list must be int or float in range [0,1]")

        # Check if the 'parameter' subgroup is correct
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
       # print("---------------Dataset------------")
       # print(dataset)
        index_dict = _get_index_dictionary(dataset)
      #  print("*******Index_Dict**********")
      #  print(index_dict)
        row_index = 0
        for row in dataset.itertuples(False):
            #print("---------row----------")
            #print(row)
            # FIRST: we check the condition of the subgroup.
            subgroup_condition_and_row_match = True # Variable to control if the condition of the subgroup and the row match. Initially, yes.
            index_in_subgroup_condition = 0 # Index over the selectors of the condition of the subgroup.
            while (index_in_subgroup_condition < len(subgroup_condition)) and (subgroup_condition_and_row_match): # Iterate over the selectors of the condition of the subgroup.
                current_selector = subgroup_condition.get_list_of_selectors()[index_in_subgroup_condition]
                #print("Current selector : ",current_selector)
                try: # IMPORTANT: If the attribute of the selector is not in the dataset, an exception of pandas (KeyError) will be raised.
                    # If one of the selectors of the condition of the subgroup does not match, the condition of the subgroup does not match (and we can go to the next row).
                    subgroup_condition_and_row_match = current_selector.match(current_selector._get_attribute_name(), row[index_dict[current_selector._get_attribute_name()]])
                 #   print("Subgroup condition and row match : " ,subgroup_condition_and_row_match)
                except KeyError as e:
                    subgroup_condition_and_row_match = False
                index_in_subgroup_condition = index_in_subgroup_condition + 1

            # SECOND: we check the target variable of the subgroup.
           
            #print("Subgroup target : ", subgroup_target._get_attribute_name(), row[index_dict[subgroup_target._get_attribute_name()]])
            try:
                subgroup_target_and_row_match = subgroup_target.match(subgroup_target._get_attribute_name(), row[index_dict[subgroup_target._get_attribute_name()]])
                #print("Subgroup target and row match : " ,subgroup_target_and_row_match)
            except KeyError as e:
                subgroup_target_and_row_match = False
                # FINALLY, we check the results.
                #print(row_index , current_selector , (current_selector._get_attribute_name(), row[index_dict[current_selector._get_attribute_name()]]))
                #print(row_index , subgroup_condition_and_row_match) 
                #print (row_index , subgroup_target, subgroup_target._get_attribute_name(), row[index_dict[subgroup_target._get_attribute_name()]] )
                #print(row_index , subgroup_target_and_row_match)
            if (subgroup_condition_and_row_match) and (subgroup_target_and_row_match):
                tp = tp + weights[row_index]         
            if (subgroup_condition_and_row_match) and (not subgroup_target_and_row_match):
                fp = fp + weights[row_index]
            if subgroup_target_and_row_match:
                TP = TP + weights[row_index]
            if not subgroup_target_and_row_match:
                FP = FP + weights[row_index]
                  
            row_index = row_index + 1
        return tp,fp,TP,FP      
 
    def _handle_individual_result(self, individual_result: tuple[Pattern, tuple[str, str], int, int, int, int], best_Wracc) -> float:
        """Private method to handle each individual result generated by the SDMap algorithm.
        
        :param individual_result: the individual result which is handled. In this case, it is a subgroup description, a target as a tuple and the subgroup parameters tp, fp, TP and FP.
        """
        # Get the subgroup parameters.
        tp = individual_result[2][0]
        fp = individual_result[2][1]
        TP = individual_result[2][2]
        FP = individual_result[2][3]
        # Compute the quality measure of the frequent pattern along with the target (i.e., the quality measure of the subgroup).
        dict_of_parameters = {QualityMeasure.TRUE_POSITIVES : tp, QualityMeasure.FALSE_POSITIVES : fp, QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP}
        quality_measure_value = WRAcc().compute(dict_of_parameters)
        # If applicable, write in the file defined in the __init__ method.
        if quality_measure_value >= best_Wracc:
            if self._file_path is not None:
                # Get the description and the target.
                subgroup_description = individual_result[0]
                target_as_tuple = individual_result[1] # Attribute name -> target_as_tuple[0], Attribute value -> target_as_tuple[1]
                # Create the subgroup.
                subgroup = Subgroup(subgroup_description, Selector(target_as_tuple[0], Operator.EQUAL, target_as_tuple[1]))
                
                # Write.
                self._file = open(self._file_path, "w")
                self._file.write(str(subgroup) + " ; ")
                self._file.write("Quality Measure " + "WRACC" + " = " + str(quality_measure_value) + " ; ")
                self._file.write("tp = " + str(tp) + " ; ")
                self._file.write("fp = " + str(fp) + " ; ")
                self._file.write("TP = " + str(TP) + " ; ")
                self._file.write("FP = " + str(FP) + "\n")
                self._file.close()
            # Increment the number of selected subgroups.
                self._selected_subgroups = self._selected_subgroups + 1
        else: # If the quality measure is not greater or equal, increment the number of unselected subgroups.
            self._unselected_subgroups = self._unselected_subgroups + 1
        return quality_measure_value