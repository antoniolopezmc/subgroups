# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""
This file contains new exceptions used by the library.
"""

class OperatorNotSupportedError(NotImplementedError):
    """This exception is raised when an operator is not correctly implemented in the Operator class.
    """

class AbstractClassError(NotImplementedError):
    """Exception raised by abstract classes.
    """

class AbstractMethodError(NotImplementedError):
    """Exception raised by abstract methods.
    """
