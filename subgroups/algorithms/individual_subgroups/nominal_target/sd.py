class AlgorithmSD(Algorithm):
    """This class represents the algorithm SD (Subgroup Discovery).

    IMPORTANT NOTE: You must not access directly to the attributes of the objects. You must use the corresponding methods.

    :type g_parameter: int or float
    :param g_parameter: Generalization parameter.
    :type min_support: int or float
    :param min_support: Minimum support that need to have a SUBGROUP to be considered. Value in form of PROPORTION (between 0 and 1).
    :type beam_width: int
    :param beam_width: Width of the beam.
    """

    def __init__(self, g_parameter, min_support, beam_width):
        """Method to initialize an object of type 'AlgorithmSD'.
        """
        if (type(g_parameter) is not int) and (type(g_parameter) is not float):
            raise TypeError("Parameter 'g_parameter' must be an integer (type 'int') or a float.")
        if (type(min_support) is not int) and (type(min_support) is not float):
            raise TypeError("Parameter 'min_support' must be an integer (type 'int') or a float.")
        if min_support < 0 or min_support > 1 :
            raise ValueError("Parameter min_support must be in range [0,1].")
        if type(beam_width) is not int:
            raise TypeError("Parameter 'beam_width' must be an integer (type 'int').")
        if not (beam_width > 0):
            raise ValueError("Width of the beam must be greater than 0.")
        self.gParameter = g_parameter
        self.minSupport = min_support
        self.beamWidth = beam_width

    def generateSetL(self, pandas_dataframe, tuple_target_attribute_value, binary_attributes = []):
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
        :type binary_attributes: list
        :param binary_attributes: (OPTIONAL) List of categorical values to be considered as binary. It is VERY IMPORTANT to respect the following conditions:
          (1) binary_attributes must be a list,
          (2) binary_attributes must contain only attributes of pandas_dataframe,
          (3) each attribute of the list must have a maximum of two values.
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
        first_element_index = pandas_dataframe.index[0]
        for column in columns_without_target: # Iterate over dataframe column names, except target column name.
            # We check the possible types of the values of the column.
            #   - The type of the strings in a pandas DataFrame is directly 'str'.
            #   - If the element gotten with 'loc' is not 'str', we have to use 'item' method to get the "primitive element" (element of the primitive type).
            if (type(pandas_dataframe[column].iloc[0]) is str): # Only check the first element, because all elements of the column are of the same type.
                if column in binary_attributes :
                    bin_values = pandas_dataframe[column]
                    for value in bin_values :
                        final_set_l[ Selector(column, Selector.OPERATOR_EQUAL, value) ] = None
                else :
                    index_dict = self.__getIndexDictionary__(pandas_dataframe)
                    for row in pandas_dataframe.itertuples(False):
                        if (row[index_dict[tuple_target_attribute_value[0]]] == tuple_target_attribute_value[1]): # If the example/row is positive.
                            final_set_l[ Selector(column, Selector.OPERATOR_EQUAL, row[index_dict[column]]) ] = None
                        elif (row[index_dict[tuple_target_attribute_value[0]]] != tuple_target_attribute_value[1]): # If the example/row is negative.
                            final_set_l[ Selector(column, Selector.OPERATOR_NOT_EQUAL, row[index_dict[column]]) ] = None
            elif (type(pandas_dataframe[column].iloc[0].item()) is float):
                # If the attribute is continuous, we have to get the positive examples and the negative examples.
                pandas_dataframe_positive_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1] ]
                pandas_dataframe_negative_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1] ]
                # We generate all possible pairs with the positive and negative examples.
                index_dict_positive_examples = self.__getIndexDictionary__(pandas_dataframe_positive_examples)
                index_dict_negative_examples = self.__getIndexDictionary__(pandas_dataframe_negative_examples)
                for positive_example_row in pandas_dataframe_positive_examples.itertuples(False):
                    for negative_example_row in pandas_dataframe_negative_examples.itertuples(False):
                        final_set_l[ Selector(column, Selector.OPERATOR_LESS_OR_EQUAL, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Selector.OPERATOR_GREATER, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
            elif (type(pandas_dataframe[column].iloc[0].item()) is int):
                # If the attribute is an integer, we have to get the positive examples and the negative examples.
                pandas_dataframe_positive_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] == tuple_target_attribute_value[1] ]
                pandas_dataframe_negative_examples = pandas_dataframe[ pandas_dataframe[tuple_target_attribute_value[0]] != tuple_target_attribute_value[1] ]
                # We generate all possible pairs with the positive and negative examples.
                index_dict_positive_examples = self.__getIndexDictionary__(pandas_dataframe_positive_examples)
                index_dict_negative_examples = self.__getIndexDictionary__(pandas_dataframe_negative_examples)
                for positive_example_row in pandas_dataframe_positive_examples.itertuples(False):
                    for negative_example_row in pandas_dataframe_negative_examples.itertuples(False):
                        final_set_l[ Selector(column, Selector.OPERATOR_LESS_OR_EQUAL, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Selector.OPERATOR_GREATER, (positive_example_row[index_dict_positive_examples[column]]+negative_example_row[index_dict_negative_examples[column]])/2) ] = None
                        final_set_l[ Selector(column, Selector.OPERATOR_EQUAL, positive_example_row[index_dict_positive_examples[column]]) ] = None
                        final_set_l[ Selector(column, Selector.OPERATOR_NOT_EQUAL, negative_example_row[index_dict_negative_examples[column]]) ] = None
        # In variable 'final_set_l', we do not have duplicates. Now, we have to return it as list.
        return list(final_set_l)

    def __getIndexDictionary__(self, dataset):
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


    def sortSetL(self, set_L, reverse = False, criterion = 'completeSelector'):
        """Method to sort the set of all feasible attribute values (set of features L) generated by the method 'generateSetL'.

        :type set_L: list
        :param set_L: Set of all feasible attribute values (set of features L) to be sorted. This method MODIFIES the input parameter. The elements of the set L MUST BE of type 'Selector' (or subclasses).
        :type reverse: bool
        :param reverse: If 'True', set l will be sorted descending/reverse. If 'False', set l will be sorted ascending. By default, False.
        :type criterion: str
        :param criterion: Method used for sorting. Possible values: 'completeSelector', 'byAttribute', 'byOperator', 'byValue'. By default, 'completeSelector'.
        :rtype: list
        :return: the parameter set_L after sorting.
        """
        criterion_available_values = ['completeSelector', 'byAttribute', 'byOperator', 'byValue']
        if type(set_L) is not list:
            raise TypeError("Parameter 'set_L' must be a python list.")
        if type(reverse) is not bool:
            raise TypeError("Parameter 'reverse' must be a boolean.")
        if criterion not in criterion_available_values:
            raise ValueError("Parameter 'criterion' is not valid (see documentation).")
        # Sort depend on criterion.
        if criterion == 'completeSelector':
            set_L.sort(reverse=reverse)
        elif criterion == 'byAttribute':
            set_L.sort(reverse=reverse, key=lambda x : x.getAttribute())
        elif criterion == 'byOperator':
            set_L.sort(reverse=reverse, key=lambda x : x.getOperator())
        elif criterion == 'byValue':
            set_L.sort(reverse=reverse, key=lambda x : str(x.getValue())) # VERY IMPORTANT: The value of different selectors could be of different types.
        # Return the list after sorting.
        return set_L

    def obtainBasicMetrics(self, pandas_dataframe, subgroup):
        """Internal method to obtain the basic metrics (tp, fp, TP and FP) of a subgroup in a dataset.

        It is VERY IMPORTANT to respect the types of the attributes: the value of a selector of the subgroup MUST BE comparable with the value of the corresponding attribute in the dataset.

        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: Input dataset. It is VERY IMPORTANT to respect the following conditions:
          (1) the dataset must be a pandas dataframe,
          (2) the dataset must not contain missing values,
          (3) for each attribute, all its values must be of the same type.
        :type subgroup: Subgroup
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
        subgroup_condition = subgroup.getCondition()
        subgroup_target = subgroup.getTarget()
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
            subgroup_condition_and_row_match = True # Variable to control if the condition of the subgroup and the row match. Initially, yes.
            index_in_subgroup_condition = 0 # Index over the selectors of the condition of the subgroup.
            while (index_in_subgroup_condition < len(subgroup_condition)) and (subgroup_condition_and_row_match): # Iterate over the selectors of the condition of the subgroup.
                current_selector = subgroup_condition.getListOfSelectors()[index_in_subgroup_condition]
                try: # IMPORTANT: If the attribute of the selector is not in the dataset, an exception of pandas (KeyError) will be raised.
                    # If one of the selectors of the condition of the subgroup does not match, the condition of the subgroup does not match (and we can go to the next row).
                    subgroup_condition_and_row_match = current_selector.match(current_selector.getAttribute(), row[current_selector.getAttribute()])
                except KeyError as e:
                    subgroup_condition_and_row_match = False
                index_in_subgroup_condition = index_in_subgroup_condition + 1
            # SECOND: we check the target variable of the subgroup.
            try:
                subgroup_target_and_row_match = subgroup_target.match(subgroup_target.getAttribute(), row[subgroup_target.getAttribute()])
            except KeyError as e:
                subgroup_target_and_row_match = False
            # FINALLY, we check the results.
            if (subgroup_condition_and_row_match) and (subgroup_target_and_row_match):
                tp = tp + 1
            if (subgroup_condition_and_row_match) and (not subgroup_target_and_row_match):
                fp = fp + 1
            if subgroup_target_and_row_match:
                TP = TP + 1
            if not subgroup_target_and_row_match:
                FP = FP + 1
        return (tp, fp, TP, FP)

    def fit(self, pandas_dataframe, tuple_target_attribute_value, set_L):
        """Method to run the algorithm SD and generate subgroups.

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
        :type set_L: list
        :param set_L: Set of all feasible attribute values (set of features L).
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
        if type(set_L) is not list:
            raise TypeError("Parameter 'set_L' must be a python list.")


        # First, we will delete the selectors that form subgroups whose support is lower than min_suuport
        new_set = []
        for i in set_L :
            subg = SubgroupForSD(Pattern([i]), Selector(tuple_target_attribute_value[0], Selector.OPERATOR_EQUAL, tuple_target_attribute_value[1]))
            subg_metrics = self.obtainBasicMetrics(pandas_dataframe, subg)
            subg_support = QualityMeasureSupport().compute({QualityMeasure.BasicMetric_tp : subg_metrics[0], QualityMeasure.BasicMetric_TP : subg_metrics[2], QualityMeasure.BasicMetric_FP : subg_metrics[3]})
            if subg_support >= self.minSupport :
                new_set.append(i)
        set_L = new_set

        # Initialize variables Beam and newBeam. IMPORTANT: Different lists with different subgroups.
        #   - Elements are LISTS with this content: [SubgroupForSD, Qg quality measure of the subgroup].
        #   - This means that variables Beam and newBeam are lists of lists.
        #   - At the beginning, all Qg are 0.
        beam = []
        newBeam = []
        for i in range(self.beamWidth):
            beam.append([SubgroupForSD(Pattern([]), Selector(tuple_target_attribute_value[0], Selector.OPERATOR_EQUAL, tuple_target_attribute_value[1])), 0])
            newBeam.append([SubgroupForSD(Pattern([]), Selector(tuple_target_attribute_value[0], Selector.OPERATOR_EQUAL, tuple_target_attribute_value[1])), 0])
        # Variable to control if there were improvements in the beam list. Initially, True (to be able to do the first iteration).
        improvements_in_beam = True
        # Main loop (while there are improvements in Beam).
        while improvements_in_beam:
            improvements_in_beam = False # Inside every iteration (and at the beginning), we put it to false.
            for index in range(self.beamWidth):
                current_subg_in_beam_original = beam[index][0] # The subgroup is the first element in the sublist.
                for l in set_L:
                    current_subg_in_beam = current_subg_in_beam_original.copy()
                    current_subg_in_beam.getCondition().addSelector(l) # Add the selector in L to the pattern of subgroup. It is not necessary to make a copy because a Selector is immutable.
                    # We obtain Qg and support of the new subgroup.
                    current_subg_in_beam_BasicMetrics = self.obtainBasicMetrics(pandas_dataframe, current_subg_in_beam)
                    current_subg_in_beam_qg = QualityMeasureQg(self.gParameter).compute({QualityMeasure.BasicMetric_tp : current_subg_in_beam_BasicMetrics[0], QualityMeasure.BasicMetric_fp : current_subg_in_beam_BasicMetrics[1]})
                    beam[index][1] = current_subg_in_beam_qg # Update the Qg quality measure (second element in the tuple).
                    current_subg_in_beam_support = QualityMeasureSupport().compute({QualityMeasure.BasicMetric_tp : current_subg_in_beam_BasicMetrics[0], QualityMeasure.BasicMetric_TP : current_subg_in_beam_BasicMetrics[2], QualityMeasure.BasicMetric_FP : current_subg_in_beam_BasicMetrics[3]})
                    # Obtain the worst sublist [subgroup, Qg] of newBeam.
                    worst_sublist_in_newBeam = newBeam[0] # Initially, the worst is the first one.
                    for x in range(1, self.beamWidth):
                        current_sublist_in_newBeam = newBeam[x]
                        if (current_sublist_in_newBeam[1] < worst_sublist_in_newBeam[1]):
                            worst_sublist_in_newBeam = current_sublist_in_newBeam
                    # Check quality measures.
                    if (current_subg_in_beam_support >= self.minSupport) and (current_subg_in_beam_qg > worst_sublist_in_newBeam[1]) and [current_subg_in_beam,current_subg_in_beam_qg] not in newBeam :
                        # The worst subgroup (sublist, in this case) in newBeam is replaced by 'b' (current_subg_in_beam).
                        worst_sublist_in_newBeam[0] = current_subg_in_beam.copy()
                        worst_sublist_in_newBeam[1] = beam[index][1]
                        # Reorder newBeam by Qg (second element of the sublist).
                        newBeam.sort(key = lambda x : x[1], reverse = True)
                        # If the condition of the 'if' is true, there will be improvements in the beam.
                        improvements_in_beam = True
            # beam <- newBeam
            for index in range(self.beamWidth):
                beam[index][0] = newBeam[index][0].copy()
                beam[index][1] = newBeam[index][1]
        return beam
