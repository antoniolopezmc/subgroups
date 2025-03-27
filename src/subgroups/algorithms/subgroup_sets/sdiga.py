# -*- coding: utf-8 -*-

# Contributors:
#    Iván García Alcaraz <igalcaraz19@gmail.com>

"""This file contains the implementation of the SDIGA algorithm.
"""
import pandas as pd

from pandas import DataFrame
from numpy import random
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

def _chromosome_decoding(chromosome : pd.Series, dictionary_df : dict) -> Pattern:
    """
    This function decodes a chromosome uwsing a dictionary with the mapping applied.

    :param chromosome: the chromosome to be decoded.
    :param dictionary_df: the dictionary with the mapping applied.
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

def _filter_rows_with_chromosome(chromosome: pd.Series, pandas_dataframe: DataFrame) -> DataFrame:
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

def _filter_rows_without_chromosome(chromosome: pd.Series, pandas_dataframe: DataFrame) -> DataFrame:
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
    return pandas_dataframe[~mask]

def _get_tp_and_fp(chromosome: pd.Series, pandas_dataframe: DataFrame, target: Tuple[str,str]) -> Tuple[int, int]:
    """
    This function calculates the True Positives and False Positives of a chromosome.

    :param chromosome: the chromosome to be evaluated.
    :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
    :param target: a tuple with 2 elements: the target attribute name and the target value.
    :return: a tuple with the True Positives and False Positives of the chromosome.
    """
    filtered_df = _filter_rows_with_chromosome(chromosome, pandas_dataframe)
    
    print(filtered_df)

    # Calculate the True Positives and False Positives.
    tp = sum(filtered_df[target[0]].apply(lambda x: target[1]==x))
    fp = len(filtered_df) - tp
    return tp, fp

def _calculate_support( chromosome : pd.Series, dataframe : DataFrame, target : tuple[str, str], TP : int, FP:int) -> float:
    """
    This function calculates the support of a chromosome.

    :param chromosome: the chromosome to be evaluated.
    :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
    :param target: a tuple with 2 elements: the target attribute name and the target value.
    :return: the support value of the chromosome.
    """
    tp,fp = _get_tp_and_fp(chromosome, dataframe, target)
    dict_of_support = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.TRUE_POPULATION: TP, QualityMeasure.FALSE_POPULATION: FP}
    return Support().compute(dict_of_support)
    
def _calculate_confidence(chromosome : pd.Series, dataframe : DataFrame, target : tuple[str, str]) -> float:
    """
    This function calculates the confidence of a chromosome.

    :param chromosome: the chromosome to be evaluated.
    :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
    :param target: a tuple with 2 elements: the target attribute name and the target value.
    :return: the confidence value of the chromosome.
    """
    tp,fp = _get_tp_and_fp(chromosome, dataframe, target)
    dict_of_confidence = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.FALSE_POSITIVES: fp}
    return PPV().compute(dict_of_confidence)


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

    __slots__ = ['_max_generation', '_population_size','_crossover_prob', '_mutation_prob', '_support_weight', '_confidence_weight', '_min_confidence','_encoded_dict','_file_path','_file']

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
        self._encoded_dict = None
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
    
    def _get_encoded_dict(self) -> dict:
        return self._encoded_dict
    
    max_generation = property(_get_max_generation, None, None, "Maximum number of generations for the evolution process.")
    population_size = property(_get_population_size, None, None, "Number of individuals in the population.")
    crossover_prob = property(_get_crossover_prob, None, None, "Probability of performing crossover during reproduction.")
    mutation_prob = property(_get_mutation_prob, None, None, "Probability of mutating an individual.")
    support_weight = property(_get_support_weight, None, None, "Weight of the support measure in the fitness evaluation.")
    confidence_weight = property(_get_confidence_weight, None, None, "Weight of the confidence measure in the fitness evaluation.")
    min_confidence = property(_get_min_confidence, None, None, "Minimum confidence threshold for selecting the best individual.")
    encoded_dict = property(_get_encoded_dict, None, None, "Dictionary of the unique values of the dataset by columns.")
    
    def _fitness_evaluation(self, chromosome : pd.Series, dataframe : DataFrame, unchecked_dataframe : DataFrame, target : tuple[str, str], TP:int, FP:int) -> float:
        """
        This function evaluates the fitness of a chromosome using the support and confidence measures.

        :param chromosome: the chromosome to be evaluated.
        :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: the fitness value of the chromosome.
        """

        support = _calculate_support(chromosome, unchecked_dataframe, target, TP, FP)
        confidence = _calculate_confidence(chromosome, dataframe, target)
        # Calculate the fitness value.
        fitness = (self._support_weight * support + self._confidence_weight * confidence)/(self._support_weight + self._confidence_weight)
        return fitness
    

    
    def _perform_crossover(self, parent1: pd.Series, parent2:pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        This function performs the crossover operation between two parents.

        :param parent1: the first parent.
        :param parent2: the second parent.
        :return: a tuple with the two children obtained from the crossover operation.
        """
        if random.rand() < self._crossover_prob:
            crossover_points = sorted(random.choice(range(len(parent1)), 2, replace=False))
            child1 = pd.concat([parent1[:crossover_points[0]], parent2[crossover_points[0]:crossover_points[1]], parent1[crossover_points[1]:]])
            child2 = pd.concat([parent2[:crossover_points[0]], parent1[crossover_points[0]:crossover_points[1]], parent2[crossover_points[1]:]])
        else:
            child1, child2 = parent1.copy(), parent2.copy()
        return child1,child2
    
    def _perform_mutation(self, child:pd.Series)-> None:
        """
        This function performs the mutation operation on a child.

        :param child: the child to be mutated.
        """
        if random.rand() < self._mutation_prob:
            mutation_point = random.choice(range(len(child)))
            if random.rand() < 0.5:
                child[mutation_point] = 0
            else:
                child[mutation_point] = random.choice(range(1, len(self._enconded_dict[child.keys()[mutation_point]]) + 1))

    def _local_search(self, chromosome: pd.Series, dataframe: DataFrame, unchecked_dataframe: DataFrame, target: tuple[str, str], TP:int, FP:int) -> Tuple[Pattern, float]:
        """
        This function performs a local search on the best individual found by the genetic algorithm.

        :param best_individual: the best individual found by the genetic algorithm.
        :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :param TP: the number of True Positives.
        :param FP: the number of False Positives.
        :return: a Pattern object with the best subgroup found by the local search and the confidence of the subgroup.
        """
        #Best individual is the best subgroup of the local search
        best_subgroup = chromosome

        #Calculate the support and confidence of the best individual
        best_support = _calculate_support(best_subgroup, unchecked_dataframe, target, TP, FP)
        best_confidence = _calculate_confidence(best_subgroup, dataframe, target)

        #store the chromosome measures
        chromosome_measures = [best_support, best_confidence]
        better = True

        #Repeat until no better individual is found
        while better:
            better = False
            #Iterate over all the genes of the chromosome
            for i in range(len(best_subgroup)):
                #If the gene is 0, continue
                if best_subgroup.iloc[i] == 0:
                    continue
                #Create a new chromosome with the gene set to 0
                new_chromosome = best_subgroup.copy()
                new_chromosome.iloc[i] = 0
                #Calculate the support and confidence of the new chromosome
                new_support = _calculate_support(new_chromosome, unchecked_dataframe, target, TP, FP)
                new_confidence = _calculate_confidence(new_chromosome, dataframe, target)
                #If the new chromosome better or equal to og_chromosome -> better
                if new_support >= chromosome_measures[0] and new_confidence >= chromosome_measures[1]:
                    better = True
                    #Update the measures if the new chromosome is better
                    if new_support > best_support:
                        best_support = new_support
                        best_confidence = new_confidence
                        best_subgroup = new_chromosome
        if best_confidence >= self._min_confidence:
            return _chromosome_decoding(best_subgroup, self._enconded_dict), best_confidence
        else:
            return _chromosome_decoding(chromosome, self._enconded_dict), chromosome_measures[1]
            



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
        encoded_df, self._enconded_dict, encoded_list = _chromosome_encoding_and_dictionary(pandas_dataframe, target) 
        
        # Create the unchecked dataframe.
        unchecked_df = encoded_df.copy()
        
        # Create empty best_cases.
        best_cases = []

        # Select random population.
        # TODO: I really don't know if the population should be selected randomly of a full chromosome
        # or if some random gene sould be 0.
        population = encoded_df.drop(columns=['deceased']).sample(n=self._population_size)
        
        # Evaluate the fitness of each individual.
        population['fitness'] = population.apply(lambda x: self._fitness_evaluation(x, encoded_df, unchecked_df, target, TP, FP), axis=1)

        new_subgroup = True
        last_subgroup_confidence = self._min_confidence

        # Repeat until no new examples or confidence example < min_confidence.
        while new_subgroup and last_subgroup_confidence >= self._min_confidence:
            
            last_subgroup_confidence = self._min_confidence-1

            # Repeat until max_generation.(GA loop)
            for generation in range(self._max_generation):
                new_population = []
                
                # Select 2 parents
                parents = population.sample(n=2, weights='fitness')
                parent1, parent2 = parents.iloc[0].drop('fitness'), parents.iloc[1].drop('fitness')

                # Perform crossover_prob (2 point crossover)
                child1, child2 = self._perform_crossover(parent1, parent2)

                # Perform mutation_prob (mutation 50% gene = 0, 50% gene = random)
                self._perform_mutation(child1)
                self._perform_mutation(child2)

                # Evaluate the fitness of new individuals
                child1_fitness = self._fitness_evaluation(child1, encoded_df, unchecked_df, target, TP, FP)
                child2_fitness = self._fitness_evaluation(child2, encoded_df, unchecked_df, target, TP, FP)

                child1['fitness'] = child1_fitness
                child2['fitness'] = child2_fitness

                new_population.extend([child1, child2])

                # Select the best values between last population and new individuals
                population = pd.concat([population, pd.DataFrame(new_population)]).nlargest(self._population_size, 'fitness')

            # Local search (best poblation).
            last_subgroup, last_subgroup_confidence = self._local_search(population.iloc[0], encoded_df, unchecked_df, target, TP, FP)

            # If confidence(R) >= min_confidence and R new cases
            if last_subgroup in best_cases:
                new_subgroup = False
                continue
            if last_subgroup_confidence < self._min_confidence:
                continue
            
            
            # mark R cases as visited.
            best_cases.append(last_subgroup)
            # recalculate the non visited dataframe.
            # recalculate the TP and FP
            unchecked_df = _filter_rows_without_chromosome(last_subgroup, unchecked_df)
            TP, FP = _get_tp_and_fp(last_subgroup, encoded_df, target)

        # Return best_cases.
        return best_cases