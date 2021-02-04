# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'core/operator.py'.
"""

from subgroups.core.operator import Operator

def test_Operator_evaluate_method():
    # --------------------------------------------------------------
    # Operator EQUAL.
    # - int type.
    assert (Operator.EQUAL.evaluate(2, 2))
    assert not (Operator.EQUAL.evaluate(2, 3))
    # - float type.
    assert (Operator.EQUAL.evaluate(2.0, 2.0))
    assert not (Operator.EQUAL.evaluate(2.0, 3.0))
    # - str type.
    assert (Operator.EQUAL.evaluate("abc", "abc"))
    assert not (Operator.EQUAL.evaluate("abc", "azz"))
    # - int and float types.
    assert (Operator.EQUAL.evaluate(2, 2.0))
    assert not (Operator.EQUAL.evaluate(2.0, 3))
    # - str and any numeric types (they support this operator).
    try:
        assert not (Operator.EQUAL.evaluate("a", 23))
        assert not (Operator.EQUAL.evaluate(1.0, "cbf"))
        assert (True)
    except:
        assert (False)
    # --------------------------------------------------------------
    # Operator NOT_EQUAL.
    # - int type.
    assert (Operator.NOT_EQUAL.evaluate(2, 3))
    assert not (Operator.NOT_EQUAL.evaluate(2, 2))
    # - float type.
    assert (Operator.NOT_EQUAL.evaluate(2.0, 3.0))
    assert not (Operator.NOT_EQUAL.evaluate(2.0, 2.0))
    # - str type.
    assert (Operator.NOT_EQUAL.evaluate("abc", "azz"))
    assert not (Operator.NOT_EQUAL.evaluate("abc", "abc"))
    # - int and float types.
    assert (Operator.NOT_EQUAL.evaluate(2.0, 3))
    assert not (Operator.NOT_EQUAL.evaluate(2, 2.0))
    # - str and any numeric types (they support this operator).
    try:
        assert (Operator.NOT_EQUAL.evaluate("a", 23))
        assert (Operator.NOT_EQUAL.evaluate(1.0, "cbf"))
        assert (True)
    except:
        assert (False)
    # --------------------------------------------------------------
    # Operator LESS.
    # - int type.
    assert (Operator.LESS.evaluate(2, 21))
    assert not (Operator.LESS.evaluate(23, 3))
    # - float type.
    assert (Operator.LESS.evaluate(2.0, 21.0))
    assert not (Operator.LESS.evaluate(23.0, 3.0))
    # - str type.
    assert (Operator.LESS.evaluate("abc", "bcd"))
    assert not (Operator.LESS.evaluate("bcd", "abc"))
    # - int and float types.
    assert (Operator.LESS.evaluate(2.0, 3))
    assert not (Operator.LESS.evaluate(20, 2.0))
    # - str and any numeric types (they support this operator).
    try:
        Operator.LESS.evaluate("a", 23.0)
        assert (False)
    except:
        assert (True)
    # --------------------------------------------------------------
    # Operator GREATER.
    # - int type.
    assert (Operator.GREATER.evaluate(21, 2))
    assert not (Operator.GREATER.evaluate(3, 23))
    # - float type.
    assert (Operator.GREATER.evaluate(21.0, 2.0))
    assert not (Operator.GREATER.evaluate(3.0, 23.0))
    # - str type.
    assert (Operator.GREATER.evaluate("bcd", "abc"))
    assert not (Operator.GREATER.evaluate("abc", "bcd"))
    # - int and float types.
    assert (Operator.GREATER.evaluate(20.0, 3))
    assert not (Operator.GREATER.evaluate(2, 2.1))
    # - str and any numeric types (they support this operator).
    try:
        Operator.GREATER.evaluate("a", 23.0)
        assert (False)
    except:
        assert (True)
    # --------------------------------------------------------------
    # Operator LESS_OR_EQUAL.
    # - int type.
    assert (Operator.LESS_OR_EQUAL.evaluate(2, 21))
    assert not (Operator.LESS_OR_EQUAL.evaluate(23, 3))
    assert (Operator.LESS_OR_EQUAL.evaluate(2, 2))
    # - float type.
    assert (Operator.LESS_OR_EQUAL.evaluate(2.0, 21.0))
    assert not (Operator.LESS_OR_EQUAL.evaluate(23.0, 3.0))
    assert (Operator.LESS_OR_EQUAL.evaluate(2.0, 2.0))
    # - str type.
    assert (Operator.LESS_OR_EQUAL.evaluate("abc", "bcd"))
    assert not (Operator.LESS_OR_EQUAL.evaluate("bcd", "abc"))
    assert (Operator.LESS_OR_EQUAL.evaluate("abc", "abc"))
    # - int and float types.
    assert (Operator.LESS_OR_EQUAL.evaluate(2.0, 3))
    assert not (Operator.LESS_OR_EQUAL.evaluate(20, 2.0))
    assert (Operator.LESS_OR_EQUAL.evaluate(2.0, 2))
    # - str and any numeric types (they support this operator).
    try:
        Operator.LESS_OR_EQUAL.evaluate("a", 23.0)
        assert (False)
    except:
        assert (True)
    # --------------------------------------------------------------
    # Operator GREATER_OR_EQUAL.
    # - int type.
    assert (Operator.GREATER_OR_EQUAL.evaluate(21, 2))
    assert not (Operator.GREATER_OR_EQUAL.evaluate(3, 23))
    assert (Operator.GREATER_OR_EQUAL.evaluate(2, 2))
    # - float type.
    assert (Operator.GREATER_OR_EQUAL.evaluate(21.0, 2.0))
    assert not (Operator.GREATER_OR_EQUAL.evaluate(3.0, 23.0))
    assert (Operator.GREATER_OR_EQUAL.evaluate(2.0, 2.0))
    # - str type.
    assert (Operator.GREATER_OR_EQUAL.evaluate("bcd", "abc"))
    assert not (Operator.GREATER_OR_EQUAL.evaluate("abc", "bcd"))
    assert (Operator.GREATER_OR_EQUAL.evaluate("abc", "abc"))
    # - int and float types.
    assert (Operator.GREATER_OR_EQUAL.evaluate(20.0, 3))
    assert not (Operator.GREATER_OR_EQUAL.evaluate(1, 2.0))
    assert (Operator.GREATER_OR_EQUAL.evaluate(2.0, 2))
    # - str and any numeric types (they support this operator).
    try:
        Operator.GREATER_OR_EQUAL.evaluate("a", 23.0)
        assert (False)
    except:
        assert (True)
    # --------------------------------------------------------------

def test_Operator_string_representation():
    assert (str(Operator.EQUAL) == "=")
    assert (str(Operator.NOT_EQUAL) == "!=")
    assert (str(Operator.LESS) == "<")
    assert (str(Operator.GREATER) == ">")
    assert (str(Operator.LESS_OR_EQUAL) == "<=")
    assert (str(Operator.GREATER_OR_EQUAL) == ">=")
