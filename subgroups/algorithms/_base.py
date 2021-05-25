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
        pass
    
    @abstractmethod
    def _save_individual_result(self, individual_result):
        pass
