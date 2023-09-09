# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the root class of all implemented algorithms. This class is an abstract class and cannot be instantiated.
"""

from abc import ABC, abstractmethod
from pandas import DataFrame

class Algorithm(ABC):
    """This abstract class defines the root class of all implemented algorithms.
    """
    
    __slots__ = ()
    
    @abstractmethod
    def fit(self, pandas_dataframe : DataFrame, target : tuple[str, str]) -> None:
        """Main method to run the corresponding algorithm.
        
        :param pandas_dataframe: the DataFrame which is scanned.
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        raise NotImplementedError("The 'fit' method from the 'Algorithm' abstract class is an abstract method.")
    
