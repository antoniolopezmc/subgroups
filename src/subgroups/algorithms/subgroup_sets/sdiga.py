# -*- coding: utf-8 -*-

# Contributors:
#    Iván García Alcaraz <igalcaraz19@gmail.com>

"""This file contains the implementation of the SDIGA algorithm.
"""
import pandas as pd

from pandas import DataFrame
from subgroups.algorithms.algorithm import Algorithm
from pandas.api.types import is_string_dtype
from subgroups.core.pattern import Pattern
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import InconsistentMethodParametersError, DatasetAttributeTypeError
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.quality_measures.support import Support
from subgroups.quality_measures.ppv import PPV

#Python annotations.
from typing import Tuple, Union

def _chromosome_encoding_and_dictionary(pandas_dataframe : DataFrame, target : tuple[str, str]) -> Tuple[DataFrame,dict,list]:
    """
    This function maps the "str" dataset to a chromosome representation using categorical functions and returns a dictionary with the mapping aplicated.

    :param pandas_dataframe: the DataFrame which is provided to find the subgroups. This algorithm only supports nominal attributes (i.e., type 'str').
    :return: a tuple with the DataFrame parsed using int values for non target columns, a dictionary with the mapping applied and a list with the attribute names.
    """
    df = pandas_dataframe.drop(columns=[target[0]]).astype('category')
    dictionary_df = df.apply(lambda x: x.cat.categories).to_dict()
    attribute_list = df.columns.tolist()
    df_coded = df.apply(lambda x: x.cat.codes + 1)
    df_coded[target[0]] = pandas_dataframe[target[0]]
    return df_coded, dictionary_df, attribute_list

def _chromosome_decoding(chromosome : pd.Series, dictionary_df : dict, attribute_list : list) -> Pattern:
    """
    This function decodes a chromosome uwsing a dictionary with the mapping applied.

    :param chromosome: the chromosome to be decoded.
    :param dictionary_df: the dictionary with the mapping applied.
    :param attribute_list: the list with the attribute names.
    :return: a Pattern object with the decoded chromosome.
    """
    selector_list = []
    #loop through all the chromosome indexes
    for gene in chromosome.keys():
        #if the gene is not 0
        if chromosome[gene] != 0:
            selector_list.append(Selector(gene, Operator.EQUAL, dictionary_df[gene][chromosome[gene]-1]))
    pattern = Pattern(selector_list)
    return pattern

def _filter_rows(chromosome: pd.Series, pandas_dataframe: DataFrame) -> DataFrame:
    """
    This function filters the rows of a DataFrame using a chromosome.

    :param chromosome: the chromosome to be used to filter the rows.
    :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
    :return: a DataFrame with the rows filtered by the chromosome.
    """
    # Create a boolean mask with all True values initially
    mask = pd.Series(True, index=pandas_dataframe.index)
    # Iterate over each index and corresponding chromosome value
    for i, chrom_val in enumerate(chromosome):
        # If chromosome[i] is non-zero, update the mask
        if chrom_val != 0:
            mask &= (pandas_dataframe.iloc[:,i] == chrom_val)
    # Return the filtered dataframe rows
    return pandas_dataframe[mask]

def _get_tp_and_fp(chromosome: pd.Series, pandas_dataframe: DataFrame, target: Tuple[str,str]) -> Tuple[int, int]:
    """
    This function calculates the True Positives and False Positives of a chromosome.

    :param chromosome: the chromosome to be evaluated.
    :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
    :param target: a tuple with 2 elements: the target attribute name and the target value.
    :return: a tuple with the True Positives and False Positives of the chromosome.
    """
    filtered_df = _filter_rows(chromosome, pandas_dataframe)
    
    print(filtered_df)

    # Calculate the True Positives and False Positives.
    tp = sum(filtered_df[target[0]].apply(lambda x: target[1]==x))
    fp = len(filtered_df) - tp
    return tp, fp


class SDIGA(Algorithm):
    """
    This class implements the SDIGA algorithm, which employs genetic operations for subgroup discovery.
    IMPORTANT: Only categorical values are supported. Combination of values from the same variable are not supported.

    :param max_generation: Maximum number of generations for the evolution process.
    :param population_size: Number of individuals in the population.
    :param crossover_prob: Probability of performing crossover during reproduction.
    :param mutation_prob: Probability of mutating an individual.
    :param support_weight: Weight of the support measure in the fitness evaluation.
    :param confidence_weight: Weight of the confidence measure in the fitness evaluation.
    :param min_confidence: Minimum confidence threshold for selecting the best individual.
    :param write_results_in_file: whether the results obtained will be written in a file. By default, False.
    :param file_path: if 'write_results_in_file' is True, path of the file in which the results will be written.
    """

    __slots__ = ['_max_generation', '_population_size','_crossover_prob', '_mutation_prob', '_support_weight', '_confidence_weight', '_min_confidence','_file_path','_file']

    def __init__(self, max_generation: int, population_size: int, crossover_prob: float, mutation_prob: float, support_weight: int, confidence_weight: int, min_confidence: float, write_results_in_file: bool = False, file_path: Union[str, None] = None) -> None:
        if (type(max_generation) is not int):
            raise TypeError("The parameter 'max_generation' must be 'int'.")
        if (type(population_size) is not int):
            raise TypeError("The parameter 'population_size' must be 'int'.")
        if (type(crossover_prob) is not float):
            raise TypeError("The parameter 'crossover_prob' must be 'float'.")
        if (type(mutation_prob) is not float):
            raise TypeError("The parameter 'mutation_prob' must be 'float'.")
        if (type(support_weight) is not int):
            raise TypeError("The parameter 'support_weight' must be 'int'.")
        if (type(confidence_weight) is not int):
            raise TypeError("The parameter 'confidence_weight' must be 'int'.")
        if (type(min_confidence) is not float):
            raise TypeError("The parameter 'min_confidence' must be 'float'.")
        if (type(write_results_in_file) is not bool):
            raise TypeError("The parameter 'write_results_in_file' must be 'bool'.")
        if ((type(file_path) is not str) and (file_path is not None)):
            raise TypeError("The parameter 'file_path' must be 'str' or 'NoneType'.")
        if ((write_results_in_file) and (file_path is None)):
            raise ValueError("If the parameter 'write_results_in_file' is True, the parameter 'file_path' must no be None.")
        if (max_generation <= 0):
            raise ValueError("The parameter 'max_generation' must be greater than 0.")
        if (population_size <= 0):
            raise ValueError("The parameter 'population_size' must be greater than 0.")
        if (crossover_prob <= 0 or crossover_prob > 1):
            raise ValueError("The parameter 'crossover_prob' must be in the range (0, 1].")
        if (mutation_prob <= 0 or mutation_prob > 1):
            raise ValueError("The parameter 'mutation_prob' must be in the range (0, 1].")
        if (support_weight < 0):
            raise ValueError("The parameter 'support_weight' must be greater than or equal to 0.")
        if (confidence_weight < 0):
            raise ValueError("The parameter 'confidence_weight' must be greater than or equal to 0.")
        self._max_generation = max_generation
        self._population_size = population_size
        self._crossover_prob = crossover_prob
        self._mutation_prob = mutation_prob
        self._support_weight = support_weight
        self._confidence_weight = confidence_weight
        self._min_confidence = min_confidence
        if (write_results_in_file):
            self._file_path = file_path
        else:
            self._file_path = None
        self._file = None
    def _get_max_generation(self) -> int:
        return self._max_generation
    
    def _get_population_size(self) -> int:
        return self._population_size
    
    def _get_crossover_prob(self) -> float:
        return self._crossover_prob
    
    def _get_mutation_prob(self) -> float:
        return self._mutation_prob
    
    def _get_support_weight(self) -> int:
        return self._support_weight
    
    def _get_confidence_weight(self) -> int:
        return self._confidence_weight
    
    def _get_min_confidence(self) -> float:
        return self._min_confidence
    
    max_generation = property(_get_max_generation, None, None, "Maximum number of generations for the evolution process.")
    population_size = property(_get_population_size, None, None, "Number of individuals in the population.")
    crossover_prob = property(_get_crossover_prob, None, None, "Probability of performing crossover during reproduction.")
    mutation_prob = property(_get_mutation_prob, None, None, "Probability of mutating an individual.")
    support_weight = property(_get_support_weight, None, None, "Weight of the support measure in the fitness evaluation.")
    confidence_weight = property(_get_confidence_weight, None, None, "Weight of the confidence measure in the fitness evaluation.")
    min_confidence = property(_get_min_confidence, None, None, "Minimum confidence threshold for selecting the best individual.")
    
    def _fitness_evaluation(self, chromosome : pd.Series, dataframe : DataFrame, unchecked_dataframe : DataFrame, target : tuple[str, str], TP:int, FP:int) -> float:
        """
        This function evaluates the fitness of a chromosome using the support and confidence measures.

        :param chromosome: the chromosome to be evaluated.
        :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: the fitness value of the chromosome.
        """

        tp_uncovered, fp_uncovered = _get_tp_and_fp(chromosome, unchecked_dataframe, target)
        tp,fp = _get_tp_and_fp(chromosome, dataframe, target)
        
        # Calculate the support and confidence of the pattern.
        dict_of_support = {QualityMeasure.TRUE_POSITIVES: tp_uncovered, QualityMeasure.TRUE_POPULATION: TP, QualityMeasure.FALSE_POPULATION: FP}
        dict_of_confidence = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.FALSE_POSITIVES: fp}
        support = Support().compute(dict_of_support)
        confidence = PPV().compute(dict_of_confidence)
        # Calculate the fitness value.
        fitness = (self._support_weight * support + self._confidence_weight * confidence)/(self._support_weight + self._confidence_weight)
        return fitness

    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """
        Main method to run the SDIGA algorithm. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        if (type(pandas_dataframe) is not DataFrame):
            raise DatasetAttributeTypeError("The parameter 'pandas_dataframe' must be a pandas DataFrame.")
        if (type(target) is not tuple):
            raise TypeError("The parameter 'target' must be a tuple.")
        if (len(target) != 2):
            raise ValueError("The parameter 'target' must have length 2.")
        if ((type(target[0]) is not str) or (type(target[1]) is not str)):
            raise TypeError("The elements of the parameter 'target' must be strings.")
        # IMPORTANT: this algorithm only supports nominal attributes (i.e., type 'str').
        for column in pandas_dataframe.columns:
            if not is_string_dtype(pandas_dataframe[column]):
                raise DatasetAttributeTypeError("Error in attribute '" + str(column) + "'. This algorithm only supports nominal attributes (i.e., type 'str').")
            
        if (target[1] not in pandas_dataframe[target[0]].unique()):
            raise ValueError("The second element of the parameter 'target' must be a value of the target variable. "+str(target[1])+" not in "+str(pandas_dataframe[target[0]].unique()))
        
        # Calculate TP and FP.
        TP = sum(pandas_dataframe[target[0]] == target[1])
        FP = len(pandas_dataframe) - TP

        # Map the dataset to a chromosome representation.
        encoded_df, enconded_dict, encoded_list = _chromosome_encoding_and_dictionary(pandas_dataframe, target) 
        
        # Create the unchecked dataframe.
        unchecked_df = encoded_df.copy()
        
        # Create empty best_cases.
        best_cases = []

        # Select random population.
        # TODO: I really don't know if the population should be selected randomly of a full chromosome
        # or if some random gene sould be 0.
        population = encoded_df.drop(columns=['deceased']).sample(n=self._population_size)
        
        # Evaluate the fitness of each individual.
        

        # Repeat until no new examples or confidence example < min_confidence.
        #    GA(algorithm).
        #       Select 2 parents.
        #       Perform crossover.
        #       Perform mutation.
        #       Evaluate the fitness of new individuals.
        #       Select the best values between 2 last population or 2 new individual.
        #   Local search (best poblation).
        #   If confidence(R) >= min_confidence and R new cases
        #       best_cases.append(R)
        #       mark R cases as visited.
        #           recalculate the non visited dataframe.
        # Return best_cases.