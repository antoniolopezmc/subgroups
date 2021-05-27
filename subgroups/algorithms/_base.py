# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains the implementation of the parent class for all the algorithms.
"""

from abc import ABC, abstractmethod

class Algorithm(ABC):
    """This abstract class defines the parent class for all the algorithms.
    """
    
    __slots__ = ()
    
    @abstractmethod
    def fit(self, pandas_dataframe, target):
        """Main method to run the corresponding algorithm.
        
        :type pandas_dataframe: pandas.DataFrame
        :param pandas_dataframe: the DataFrame which is scanned.
        :type target: tuple[str, str]
        :param target: a tuple with 2 elements: the target attribute name and the target value.
        """
        pass
    
    @abstractmethod
    def _save_individual_result(self, individual_result):
        """Private method to save a individual result and, if applicable, write it in a file.
        
        :type individual_result: (it depends on each algorithm)
        :param individual_result: the individual result which is saved and, if applicable, written in the file.
        """
        pass
