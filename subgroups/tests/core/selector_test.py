# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'core/selector.py'.
"""

from subgroups.core.selector import Selector
from subgroups.core.operator import Operator
from subgroups import exceptions

def test_Selector_attributes():
    # These examples must run ok.
    selector1 = Selector("attribute_name_1", Operator.EQUAL, "value_1")
    assert(selector1.attribute_name == "attribute_name_1")
    assert(selector1.operator == Operator.EQUAL)
    assert(selector1.value == "value_1")
    assert(type(selector1.value) is str)
    assert(str(selector1) == "attribute_name_1 = \'value_1\'")
    try:
        repr(selector1)
        assert (False)
    except exceptions.MethodNotSupportedError:
        assert (True)
    selector2 = Selector("attribute_name_2", Operator.NOT_EQUAL, "value_2")
    assert(selector2.attribute_name == "attribute_name_2")
    assert(selector2.operator == Operator.NOT_EQUAL)
    assert(selector2.value == "value_2")
    assert(type(selector2.value) is str)
    assert(str(selector2) == "attribute_name_2 != \'value_2\'")
    selector3 = Selector("attribute_name_3", Operator.LESS, 90)
    assert(selector3.attribute_name == "attribute_name_3")
    assert(selector3.operator == Operator.LESS)
    assert(selector3.value == 90)
    assert(type(selector3.value) is int)
    assert(str(selector3) == "attribute_name_3 < 90")
    selector4 = Selector("attribute_name_4", Operator.LESS_OR_EQUAL, 5.045)
    assert(selector4.attribute_name == "attribute_name_4")
    assert(selector4.operator == Operator.LESS_OR_EQUAL)
    assert(selector4.value == 5.045)
    assert(type(selector4.value) is float)
    assert(str(selector4) == "attribute_name_4 <= 5.045")
    selector5 = Selector("attribute_name_5", Operator.EQUAL, "5.045")
    assert(selector5.attribute_name == "attribute_name_5")
    assert(selector5.operator == Operator.EQUAL)
    assert(selector5.value == "5.045")
    assert(type(selector5.value) is str)
    assert(str(selector5) == "attribute_name_5 = \'5.045\'")
    try:
        selector6 = Selector("", Operator.GREATER_OR_EQUAL, 60)
        assert (True)
    except ValueError:
        assert (False)
    try:
        selector7 = Selector("attribute_name_7", Operator.NOT_EQUAL, "")
        assert (True)
    except ValueError:
        assert (False)
    # These examples must raise an exception (the exception that appears in 'except').
    try:
        selector8 = Selector(45, Operator.GREATER_OR_EQUAL, 60)
        assert (False)
    except TypeError:
        assert (True)
    try:
        selector9 = Selector("attribute_name_9", 45, 60)
        assert (False)
    except TypeError:
        assert (True)
    try:
        selector10 = Selector("attribute_name_10", "hello", 60)
        assert (False)
    except TypeError:
        assert (True)
    try:
        selector11 = Selector("attribute_name_11", Operator.GREATER_OR_EQUAL, "value_11") # If the value is of type str, only the operators "=" and "!=" are available. 
        assert (False)
    except ValueError:
        assert (True)

def test_Selector_match_mathod():
    selector1 = Selector("a", Operator.EQUAL, 23)
    selector2 = Selector("a", Operator.GREATER, 23)
    assert (selector1.match("a", 23))
    assert not (selector1.match("a", 30))
    assert not (selector1.match("z", 30))
    assert not (selector1.match("a", 30.0))
    assert not (selector1.match("a", "23"))
    assert (selector2.match("a", 30))
    assert not (selector2.match("a", 5))
    assert not (selector2.match("z", 5))
    assert (selector2.match("a", 30.0))
    assert not (selector2.match("a", "30")) # The the input does not match with the selector, because we cannot apply the operator '>' between a str and an int.
    # These examples must raise an exception (the exception that appears in 'except').
    try:
        selector3 = Selector("attribute_name_3", Operator.EQUAL, "value_3")
        selector3.match(12, "value_3")
        assert(False)
    except TypeError:
        assert(True)

def test_Selector_generate_from_str_method():
    assert (Selector.generate_from_str("a = 23") == Selector("a", Operator.EQUAL, 23))
    assert (Selector.generate_from_str("a != 23") == Selector("a", Operator.NOT_EQUAL, 23))
    assert (Selector.generate_from_str("a < 23") == Selector("a", Operator.LESS, 23))
    assert (Selector.generate_from_str("a > 23") == Selector("a", Operator.GREATER, 23))
    assert (Selector.generate_from_str("a <= 23") == Selector("a", Operator.LESS_OR_EQUAL, 23))
    assert (Selector.generate_from_str("a >= 23") == Selector("a", Operator.GREATER_OR_EQUAL, 23))
    assert (type(Selector.generate_from_str("a >= 23").value) is int)
    assert (Selector.generate_from_str("a > 23.06") == Selector("a", Operator.GREATER, 23.06))
    assert (type(Selector.generate_from_str("a > 23.06").value) is float)
    assert (Selector.generate_from_str("a != 'hello'") == Selector("a", Operator.NOT_EQUAL, "hello"))
    assert (type(Selector.generate_from_str("a != 'hello'").value) is str)
    assert (Selector.generate_from_str("a != 'hello'").value == "hello")
    assert (Selector.generate_from_str('a != "hello"') == Selector("a", Operator.NOT_EQUAL, "hello"))
    assert (type(Selector.generate_from_str('a != "hello"').value) is str)
    assert (Selector.generate_from_str('a != "hello"').value == "hello")
    assert (Selector.generate_from_str("a != \'hello\'") == Selector("a", Operator.NOT_EQUAL, "hello"))
    assert (type(Selector.generate_from_str("a != \'hello\'").value) is str)
    assert (Selector.generate_from_str("a != \'hello\'").value == "hello")
    assert (Selector.generate_from_str('a != \"hello\"') == Selector("a", Operator.NOT_EQUAL, "hello"))
    assert (type(Selector.generate_from_str('a != \"hello\"').value) is str)
    assert (Selector.generate_from_str('a != \"hello\"').value == "hello")
    assert (Selector.generate_from_str("a != hello") == Selector("a", Operator.NOT_EQUAL, "hello"))
    assert (type(Selector.generate_from_str("a != hello").value) is str)
    assert (Selector.generate_from_str("a != hello").value == "hello")
    assert (Selector.generate_from_str("a != 25.36.12") == Selector("a", Operator.NOT_EQUAL, "25.36.12"))
    assert (type(Selector.generate_from_str("a != 25.36.12").value) is str)
    assert (Selector.generate_from_str("a != 25.36.12").value == "25.36.12")
    try:
        Selector.generate_from_str("a < 'hello'")
        assert(False)
    except ValueError:
        assert(True)

def test_Selector_comparisons():
    selector1 = Selector("a", Operator.EQUAL, 23)
    selector2 = Selector("a", Operator.EQUAL, 23)
    selector3 = Selector("a", Operator.NOT_EQUAL, 23)
    selector4 = Selector("b", Operator.EQUAL, 23)
    selector5 = Selector("a", Operator.EQUAL, 25)
    assert (selector1 == selector2)
    assert (selector1 <= selector2)
    assert (selector1 >= selector2)
    assert (selector1 != selector3)
    assert (selector1 < selector3)
    assert not (selector1 > selector3)
    assert (selector1 <= selector3)
    assert not (selector1 >= selector3)
    assert (selector1 < selector4)
    assert not (selector1 == selector5)
    assert (selector1 != selector5)
    assert (selector1 < selector5)
    assert (selector1 <= selector5)
    assert not (selector1 > selector5)
    assert not (selector1 >= selector5)
