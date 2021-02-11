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
    """This exception is raised when a subgroup parameter in not found in the quality measure computing process.
    """
