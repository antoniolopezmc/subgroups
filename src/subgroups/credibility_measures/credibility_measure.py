# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <fmora@um.es>

"""This file contains the implementation of the root class of all the implemented credibility measures. This class is an abstract class and cannot be instantiated.
"""

from abc import ABC, abstractmethod

# Python annotations.
from typing import Union, ClassVar

class CredibilityMeasure(ABC):
    """This abstract class defines the root class of all the implemented credibility measures.
    """

    __slots__ = ()

    @abstractmethod
    def compute(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Method to compute the corresponding credibility measure (you can also call to the instance for this purpose).
        
        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the corresponding credibility measure.
        """
        raise NotImplementedError("The 'compute' method from the 'CredibilityMeasure' abstract class is an abstract method.")
    
    @abstractmethod
    def get_name(self) -> str:
        """Method to get the credibility measure name (equal to the class name).
        """
        raise NotImplementedError("The 'get_name' method from the 'CredibilityMeasure' abstract class is an abstract method.")
    
    @abstractmethod
    def __call__(self, dict_of_parameters : dict[str, Union[int, float]]) -> float:
        """Compute the corresponding credibility measure.

        :param dict_of_parameters: python dictionary which contains all the necessary parameters used to compute this credibility measure.
        :return: the computed value for the corresponding credibility measure.
        """
        raise NotImplementedError("The '__call__' method from the 'CredibilityMeasure' abstract class is an abstract method.")