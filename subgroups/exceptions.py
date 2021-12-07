# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains new exceptions used by the library.
"""

class OperatorNotSupportedError(NotImplementedError):
    """This exception is raised when an operator is not correctly implemented in the Operator class.
    """

class ParameterNotFoundError(KeyError):
    """This exception is raised when a needed parameter is not found in the quality measure computing process.
    """

class SubgroupParameterNotFoundError(ParameterNotFoundError):
    """This exception is raised when a subgroup parameter (i.e., tp, fp, TP or FP) is not found in the quality measure computing process.
    """

class InconsistentMethodParametersError(RuntimeError):
    """This exception is raised when a method has not been called with the appropriate parameters.
    """

class DatasetAttributeTypeError(TypeError):
    """This exception is raised when the type of an attribute in a dataset is not supported by a Subgroup Discovery (SD) algorithm.
    """

class DuplicateFpTreeNodeError(RuntimeError):
    """This exception is raised when attempting to add a FPTreeNode which already exists.
    """
