# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of some additional functions used in the MDL principle.
"""

from functools import lru_cache
from numpy import log2, ceil, log, sqrt # log from numpy -> ln

@lru_cache(maxsize=1000)
def universal_code_for_integer(input_integer_value : int) -> float:
    """Compute the universal code LN(i) for the input integer value.

    :param input_integer_value: integer value on which to compute the universal code.
    :return: the universal code LN(i) for the input integer value.
    """
    if type(input_integer_value) is not int:
        raise TypeError("The type of the parameter 'input_integer_value' must be 'int'.")
    if input_integer_value < 0:
        raise ValueError("The value of 'input_integer_value' must be greater or equal than 0.")
    if input_integer_value == 0:
        return 0
    else:
        threshold = 0.000001 # Threshold for the condition of the while loop.
        result = log2(2.865064)  # Initially, the result is 'log2(k0)'.
        current_log_value = log2(input_integer_value)
        while current_log_value > threshold:
            result = result + current_log_value
            current_log_value = log2(current_log_value)
    return result

## "Computing the Multinomial Stochastic Complexity in Sub-Linear Time" paper.
##      L -> number_of_categories.
##      n -> number_of_samples.
def multinomial_with_recurrence(number_of_categories : int, number_of_samples : int) -> float:
    """Compute the multinomial distribution complexity.

    :param number_of_categories: number of categories of the multinomial distribution.
    :param number_of_samples: number of instances/points/samples/rows/registers.
    :return: the multinomial distribution complexity.
    """
    if type(number_of_categories) is not int:
        raise TypeError("The type of the parameter 'number_of_categories' must be 'int'.")
    if type(number_of_samples) is not int:
        raise TypeError("The type of the parameter 'number_of_samples' must be 'int'.")
    if number_of_categories <= 0:
        raise ValueError("The value of 'number_of_categories' must be greater than 0.")
    if number_of_samples < 0:
        raise ValueError("The value of 'number_of_samples' must be greater or equal than 0.")
    if number_of_categories == 1:
        return 1.0
    elif number_of_samples == 0:
        return 0.0
    else:
        sum = 1.0
        b = 1.0
        d = 10
        bound = int(ceil(2+sqrt(2*number_of_samples*d*log(10)))) # See equation 38 of the paper.
        for k in range(1,bound+1):
            b = (number_of_samples-k+1) / number_of_samples * b
            sum = sum + b
        old_sum = 1.0
        for j in range(3, number_of_categories+1):
            new_sum = sum + (number_of_samples*old_sum) / (j-2)
            old_sum = sum
            sum = new_sum
        return sum

@lru_cache(maxsize=1000)
def log2_multinomial_with_recurrence(number_of_categories : int, number_of_samples : int) -> float:
    """Compute the logarithm to base 2 of the multinomial distribution complexity.

    :param number_of_categories: number of categories of the multinomial distribution.
    :param number_of_samples: number of instances/points/samples/rows/registers.
    :return: the logarithm to base 2 of the multinomial distribution complexity or 0 if the multinomial distribution complexity is 0.
    """
    mdc = multinomial_with_recurrence(number_of_categories, number_of_samples)
    if mdc > 0:
        return log2(mdc)
    else:
        return 0.0
