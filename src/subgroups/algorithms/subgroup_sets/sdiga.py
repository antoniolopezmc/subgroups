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

def _chromosome_encoding_and_dictionary(pandas_dataframe : DataFrame, target : tuple[str, str]) -> Tuple[DataFrame,dict]:
    """
    This function maps the "str" values of the DataFrame to int values, creating a dictionary with the mapping applied.
    It also returns the DataFrame with the int values for non target columns.
    The target column is not modified.

    :param pandas_dataframe: the DataFrame which is provided to find the subgroups. This algorithm only supports nominal attributes (i.e., type 'str').
    :param target: a tuple with 2 elements: the target attribute name and the target value.
    :return: a tuple with the DataFrame parsed using int values for non target columns and a dictionary with the mapping applied.
    """

    df = pandas_dataframe.drop(columns=[target[0]]).astype('category')
    dictionary_df = df.apply(lambda x: x.cat.categories.to_list()).to_dict()
    df_coded = df.apply(lambda x: x.cat.codes + 1)
    df_coded = df_coded.astype('uint16')
    df_coded[target[0]] = pandas_dataframe[target[0]]
    return df_coded, dictionary_df

def _chromosome_decoding(chromosome : pd.Series, dictionary_df : dict) -> Pattern:
    """
    This function decodes a chromosome using a dictionary with the mapping applied.
    It creates a Pattern object with the decoded chromosome, which contains the selectors for each gene in the chromosome.

    :param chromosome: the chromosome to be decoded. The chromosome don't have the target column or fitness value.
    :param dictionary_df: the dictionary with the mapping applied.
    :return: a Pattern object with the decoded chromosome.
    """
    selector_list = []
    #loop through all the chromosome indexes
    for gene in chromosome.keys():
        #if the gene is not 0
        if chromosome[gene] != 0:
            selector_list.append(Selector(gene, Operator.EQUAL, dictionary_df[gene][int(chromosome[gene])-1]))
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
    This function filters the rows of a DataFrame not using a chromosome.

    :param chromosome: the chromosome to be used to filter the rows.
    :param pandas_dataframe: the DataFrame which is provided to find the subgroups.
    :return: a DataFrame with the rows filtered by not containing the chromosome.
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

    # Calculate the True Positives and False Positives.
    tp = sum(filtered_df[target[0]].apply(lambda x: target[1]==x))
    fp = len(filtered_df) - tp
    return tp, fp


def _calculate_support( tp:int, TP : int, FP:int) -> float:
    """
    This function calculates the support of a chromosome.

    :param tp: the number of True Positives of the chromosome.
    :param TP: the total number of True Population in the dataset.
    :param FP: the total number of False Population in the dataset.
    :return: the support value of the chromosome.
    """
    #tp,fp = _get_tp_and_fp(chromosome, dataframe, target)
    if tp==TP==FP==0:
        return 0
    
    dict_of_support = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.TRUE_POPULATION: TP, QualityMeasure.FALSE_POPULATION: FP}
    return Support().compute(dict_of_support)


    
def _calculate_confidence(tp:int, fp:int) -> float:
    """
    This function calculates the confidence of a chromosome.

    :param tp: the number of True Positives of the chromosome.
    :param fp: the number of False Positives of the chromosome.
    :return: the confidence value of the chromosome.
    """
    #tp,fp = _get_tp_and_fp(chromosome, dataframe, target)
    if tp==fp==0:
        return 0
    
    dict_of_confidence = {QualityMeasure.TRUE_POSITIVES: tp, QualityMeasure.FALSE_POSITIVES: fp}
    return PPV().compute(dict_of_confidence)


def _generate_population(codification_dict:dict, population_size:int) -> pd.DataFrame:
    
    """
    This function generates a population of chromosomes using the codification dictionary.
    :param codification_dict: the dictionary with the unique values of the dataset by columns.
    :param population_size: the size of the population to be generated.
    :return: a DataFrame with the population of chromosomes.
    """
    # Create an empty list to store the population
    list_of_chromosomes = []
    
    # Generate random chromosomes
    for _ in range(population_size):
        chromosome = {key: random.randint(0, len(value)+1) for key, value in codification_dict.items()}
        list_of_chromosomes.append(chromosome)
    # Convert the list of chromosomes to a DataFrame
    return pd.DataFrame(list_of_chromosomes, columns=codification_dict.keys())


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

    __slots__ = ['_max_generation', '_population_size','_crossover_prob', '_mutation_prob', '_confidence_weight', '_support_weight', '_min_confidence','_encoded_dict','_unchecked_dataframe','_unselected_subgroups','_selected_subgroups','_TP','_FP','_TP_unchecked','_FP_unchecked','_file_path','_file']

    def __init__(self, max_generation: int, population_size: int, crossover_prob: float, mutation_prob: float, confidence_weight: float, support_weight: float, min_confidence: float, write_results_in_file: bool = False, file_path: Union[str, None] = None) -> None:
        if (type(max_generation) is not int):
            raise TypeError("The parameter 'max_generation' must be 'int'.")
        if (type(population_size) is not int):
            raise TypeError("The parameter 'population_size' must be 'int'.")
        if (type(crossover_prob) is not float):
            raise TypeError("The parameter 'crossover_prob' must be 'float'.")
        if (type(mutation_prob) is not float):
            raise TypeError("The parameter 'mutation_prob' must be 'float'.")
        if (type(support_weight) is not float):
            raise TypeError("The parameter 'support_weight' must be 'int'.")
        if (type(confidence_weight) is not float):
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
        if (crossover_prob <= 0 or crossover_prob >= 1):
            raise ValueError("The parameter 'crossover_prob' must be in the range (0, 1].")
        if (mutation_prob <= 0 or mutation_prob >= 1):
            raise ValueError("The parameter 'mutation_prob' must be in the range (0, 1].")
        if (support_weight < 0):
            raise ValueError("The parameter 'support_weight' must be greater than 0.")
        if (confidence_weight < 0):
            raise ValueError("The parameter 'confidence_weight' must be greater than 0.")
        if (min_confidence < 0):
            raise ValueError("The parameter 'min_confidence' must be greater than 0.")
        

        self._max_generation: int = max_generation
        self._population_size: int = population_size
        self._crossover_prob: float = crossover_prob
        self._mutation_prob: float = mutation_prob
        self._support_weight: float = support_weight
        self._confidence_weight: float = confidence_weight
        self._min_confidence: float = min_confidence
        self._encoded_dict:dict[str, list[str]] = None
        self._unchecked_dataframe:DataFrame = None
        self._unselected_subgroups:int = 0
        self._selected_subgroups:int = 0
        self._TP:int = 0
        self._FP:int = 0
        self._TP_unchecked:int = 0
        self._FP_unchecked:int = 0
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
    
    def _get_support_weight(self) -> float:
        return self._support_weight
    
    def _get_confidence_weight(self) -> float:
        return self._confidence_weight
    
    def _get_min_confidence(self) -> float:
        return self._min_confidence
    
    def _get_encoded_dict(self) -> dict:
        return self._encoded_dict
    
    def _get_unchecked_dataframe(self) -> DataFrame:
        return self._unchecked_dataframe
    
    def _get_unselected_subgroups(self) -> int:
        return self._unselected_subgroups

    def _get_selected_subgroups(self) -> int:
        return self._selected_subgroups
    
    def _get_TP(self) -> int:
        return self._TP
    
    def _get_FP(self) -> int:
        return self._FP
    
    def _get_TP_unchecked(self) -> int:
        return self._TP_unchecked
    
    def _get_FP_unchecked(self) -> int:
        return self._FP_unchecked
    

    max_generation = property(_get_max_generation, None, None, "Maximum number of generations for the evolution process.")
    population_size = property(_get_population_size, None, None, "Number of individuals in the population.")
    crossover_prob = property(_get_crossover_prob, None, None, "Probability of performing crossover during reproduction.")
    mutation_prob = property(_get_mutation_prob, None, None, "Probability of mutating an individual.")
    support_weight = property(_get_support_weight, None, None, "Weight of the support measure in the fitness evaluation.")
    confidence_weight = property(_get_confidence_weight, None, None, "Weight of the confidence measure in the fitness evaluation.")
    min_confidence = property(_get_min_confidence, None, None, "Minimum confidence threshold for selecting the best individual.")
    encoded_dict = property(_get_encoded_dict, None, None, "Dictionary of the unique values of the dataset by columns.")
    unchecked_dataframe = property(_get_unchecked_dataframe, None, None, "DataFrame with the unchecked dataset.")
    unselected_subgroups = property(_get_unselected_subgroups, None, None, "Number of unselected subgroups after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")
    selected_subgroups = property(_get_selected_subgroups, None, None, "Number of selected subgroups after executing the SDMap algorithm (before executing the 'fit' method, this attribute is 0).")
    TP = property(_get_TP, None, None, "Number of True Positives.")
    FP = property(_get_FP, None, None, "Number of False Positives.")
    TP_unchecked = property(_get_TP_unchecked, None, None, "Number of True Positives from the unchecked dataset.")
    FP_unchecked = property(_get_FP_unchecked, None, None, "Number of False Positives from the unchecked dataset.")
    
    def _fitness_evaluation(self, chromosome : pd.Series, dataframe : DataFrame, target : tuple[str, str]) -> float:
        """
        This function evaluates the fitness of a chromosome based on the support and confidence measures.
        The fitness value is calculated as a weighted average of the support and confidence measures.
        The support and confidence measures are calculated using the True Positives and False Positives of the chromosome.

        :param chromosome: the chromosome to be evaluated.
        :param dataframe: the DataFrame which is provided to find the subgroups.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: the fitness value of the chromosome.
        """
        #calculate support value
        tp_sup, fp_sup = _get_tp_and_fp(chromosome, self._unchecked_dataframe,target)
        support = _calculate_support(tp_sup, self._TP_unchecked, self._FP_unchecked)

        #calculate confidence value
        tp_conf, fp_conf = _get_tp_and_fp(chromosome, dataframe, target)
        confidence = _calculate_confidence(tp_conf, fp_conf)
        # Calculate the fitness value.
        fitness = (self._support_weight * support + self._confidence_weight * confidence)/(self._support_weight + self._confidence_weight)
        return fitness
    

    
    def _perform_crossover(self, parent1: pd.Series, parent2:pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        This function performs the crossover operation between two parents.

        :param parent1: the first parent. Chromosome representation of the first parent.
        :param parent2: the second parent. Chromosome representation of the second parent.
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
                child.iloc[mutation_point] = 0
            else:
                child.iloc[mutation_point] = random.choice(range(1, len(self._encoded_dict[child.keys()[mutation_point]]) + 1))

    def _local_search(self, chromosome: pd.Series, dataframe: DataFrame, target: tuple[str, str]) -> Tuple[Pattern, float, float, int, int]:
        """
        This function performs a local search on the best individual found by the genetic algorithm.

        :param chromosome: the best individual found by the genetic algorithm.
        :param dataframe: the DataFrame which is provided to find the subgroups.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: a tuple with the best subgroup found, its confidence, its fitness value, and the True Positives and False Positives of the best subgroup.
        """
        # Get chromosome measures
        tp_chrom, fp_chrom = _get_tp_and_fp(chromosome, dataframe, target)
        support_chromosome = _calculate_support(tp_chrom, self._TP, self._FP)
        confidence_chromosome = _calculate_confidence(tp_chrom, fp_chrom)

        # Initialize the best subgroup
        best_subgroup = chromosome
        best_support = support_chromosome
        best_confidence = confidence_chromosome
        best_tp = tp_chrom
        best_fp = fp_chrom

        better = True

        # Repeat until no better individual is found
        while better:
            better = False
            best_candidate = None
            best_support_delta = 0
            best_metrics = None

            # Iterate over all the genes of the chromosome
            for i in range(len(best_subgroup)):
                if best_subgroup.iloc[i] == 0:
                    continue
                # Create a new chromosome with the gene set to 0
                new_chromosome = best_subgroup.copy()
                new_chromosome.iloc[i] = 0

                # Calculate the support and confidence of the new chromosome
                tp, fp = _get_tp_and_fp(new_chromosome, dataframe, target)
                new_support = _calculate_support(tp, self._TP, self._FP)
                new_confidence = _calculate_confidence(tp, fp)

                # Check if the new chromosome is better
                if new_support >= support_chromosome and new_confidence >= confidence_chromosome and new_confidence > 0:
                    delta = new_support - support_chromosome
                    if delta > best_support_delta:
                        best_candidate = new_chromosome
                        best_support_delta = delta
                        best_metrics = (new_support, new_confidence, tp, fp)

            # Update the best subgroup if a better candidate is found
            if best_candidate is not None:
                better = True
                best_subgroup = best_candidate
                best_support, best_confidence, best_tp, best_fp = best_metrics
                support_chromosome = best_support
                confidence_chromosome = best_confidence

        # Return the best subgroup and its metrics
        if best_confidence >= self._min_confidence:
            return best_subgroup, best_confidence, self._fitness_evaluation(best_subgroup, dataframe, target), best_tp, best_fp
        else:
            return chromosome, confidence_chromosome, self._fitness_evaluation(chromosome, dataframe, target), tp_chrom, fp_chrom
            
    def _SDIGA(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> list[Subgroup]:
        """"
        This function implements the SDIGA algorithm. It uses a genetic algorithm to find the best subgroups in the dataset after that it applies a local search to find the best subgroup.
        :param pandas_dataframe: the DataFrame which is scanned. This algorithm only supports nominal attributes (i.e., type 'str'). IMPORTANT: missing values are not supported yet.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        :return: a list of the best subgroups found by the algorithm.
        """
        
        # Calculate TP and FP.
        self._TP_unchecked = self._TP = sum(pandas_dataframe[target[0]] == target[1])
        self._FP_unchecked = self._FP = len(pandas_dataframe) - self._TP_unchecked

        # Map the dataset to a chromosome representation.
        encoded_df, self._encoded_dict = _chromosome_encoding_and_dictionary(pandas_dataframe, target) 
        
        # Create the unchecked dataframe.
        self._unchecked_dataframe = encoded_df.copy()
        
        # Create empty best_cases.
        best_cases:list[Pattern] = []

        new_subgroup = True
        last_subgroup_confidence = self._min_confidence

        # Repeat until no new examples or confidence example < min_confidence.
        while new_subgroup and last_subgroup_confidence >= self._min_confidence:
            last_subgroup_confidence = self._min_confidence-1

            # Select random population.
            
            population = _generate_population(self._encoded_dict, self._population_size)
            
            # Evaluate the fitness of each individual.
            population['fitness'] = population.apply(lambda x: self._fitness_evaluation(x, encoded_df, target), axis=1)

            # Sort the population by fitness.
            population = population.sort_values(by='fitness', ascending=False)

            # Repeat until max_generation.(GA loop)
            for generation in range(self._max_generation):
                
                # Select 2 parents
                parent1, parent2  = population.iloc[0].drop('fitness'), population.iloc[1].drop('fitness')

                # Calculate probabilities and
                
                # Perform crossover_prob (2 point crossover)
                child1, child2 = self._perform_crossover(parent1, parent2)

                # Perform mutation_prob (mutation 50% gene = 0, 50% gene = random)
                self._perform_mutation(child1)
                self._perform_mutation(child2)

                # Evaluate the fitness of new individuals
                child1_fitness = self._fitness_evaluation(child1, encoded_df, target)
                child2_fitness = self._fitness_evaluation(child2, encoded_df, target)

                child1['fitness'] = child1_fitness
                child2['fitness'] = child2_fitness

                # Add the new children to the new population if their fitness is better than the last row of the current population
                population.iloc[-1] = child1
                population.iloc[-1] = child2

                # Select the best values between last population and new individuals
                population = population.nlargest(self._population_size, 'fitness')

                self._unselected_subgroups += 2


            self._unselected_subgroups += self._population_size-1
            # Local search (best chromosome).
            last_chromosome, last_subgroup_confidence, last_fitness, last_tp, last_fp = self._local_search(population.iloc[0].drop('fitness'), encoded_df, target)
            last_subgroup = _chromosome_decoding(last_chromosome, self._encoded_dict)

            # If confidence(R) >= min_confidence and R new cases
            
            if any(case.is_refinement(last_subgroup, refinement_of_itself=True) for case in best_cases):
                new_subgroup = False
                continue
            if last_subgroup_confidence < self._min_confidence:
                continue
            
            # Calculate the unchecked tp and fp values.
            tp, fp = _get_tp_and_fp(last_chromosome, self._unchecked_dataframe, target)
            # mark R cases as visited.
            best_cases.append(last_subgroup)
            self._selected_subgroups += 1

            # Create the subgroup object.
            subgroup = Subgroup(last_subgroup, Selector(target[0], Operator.EQUAL, target[1]))

            if self._file_path is not None:
                self._file.write(str(subgroup) + " ; ")
                self._file.write("Quality Measure Fitness = " + str(last_fitness) + " ; ")
                self._file.write("tp = " + str(last_tp) + " ; ")
                self._file.write("fp = " + str(last_fp) + " ; ")
                self._file.write("TP = " + str(self._TP) + " ; ")
                self._file.write("FP = " + str(self._FP) + " ; ")
                self._file.write("unchecked_tp = " + str(tp) + " ; ")
                self._file.write("unchecked_fp = " + str(fp) + " ; ")
                self._file.write("TP_unchecked = " + str(self._TP_unchecked) + " ; ")
                self._file.write("FP_unchecked = " + str(self._FP_unchecked) + "\n")
            # recalculate the non visited dataframe.
            # recalculate the TP and FP
            self._unchecked_dataframe = _filter_rows_without_chromosome(last_chromosome, self._unchecked_dataframe)
            self._TP_unchecked = sum(self._unchecked_dataframe[target[0]] == target[1])
            self._FP_unchecked = len(self._unchecked_dataframe) - self._TP_unchecked
        return best_cases


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
        
        if (self._file_path is not None):
                self._file = open(self._file_path, "w")
        best_cases = self._SDIGA(pandas_dataframe, target)
        if (self._file_path is not None):
                self._file.close()
                self._file = None