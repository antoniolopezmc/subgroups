# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""
This file contains new exceptions used by the library.
"""

class OperatorNotSupportedError(RuntimeError):
    """This exception is raised when an operator is not correctly implemented in the Operator class.
    """

class MethodNotSupportedError(NotImplementedError):
    """This exception is raised when an object does not support a method.
    """
