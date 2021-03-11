# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""
This file contains new exceptions used by the library.
"""

class OperatorNotSupportedError(NotImplementedError):
    """This exception is raised when an operator is not correctly implemented in the Operator class.
    """

class SubgroupParameterNotFoundError(KeyError):
    """This exception is raised when a subgroup parameter is not found in the quality measure computing process.
    """

class ParametersError(RuntimeError):
    """This exception is raised when a method has not been called with the appropriate parameters.
    """

class TargetAttributeTypeError(TypeError):
    """This exception is raised when the type of the target attribute is not supported by a Subgroup Discovery (SD) algorithm.
    """
