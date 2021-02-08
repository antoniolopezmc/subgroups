# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'core/selector.py'.
"""

from subgroups.core.selector import Selector
from subgroups.core.operator import Operator

def test_Selector_creation_process():
    # --------------------------------------------------------------
    assert (len(Selector._dict_of_selectors) == 0)
    selector1 = Selector("a", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 1)
    selector2 = Selector("a", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 1)
    selector3 = Selector("a", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 2)
    selector4 = Selector("a", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 2)
    selector5 = Selector("a", Operator.LESS, 52)
    assert (len(Selector._dict_of_selectors) == 3)
    selector6 = Selector("a", Operator.LESS, 52)
    assert (len(Selector._dict_of_selectors) == 3)
    selector7 = Selector("a", Operator.GREATER, 52)
    assert (len(Selector._dict_of_selectors) == 4)
    selector8 = Selector("qwe", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 5)
    selector9 = Selector("qwe", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 5)
    selector10 = Selector("qwe", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 6)
    selector11 = Selector("qwe", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 6)
    selector12 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 7)
    selector13 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 7)
    selector14 = Selector("qwe", Operator.GREATER_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 8)
    # --------------------------------------------------------------
    assert (id(selector1) == id(selector2))
    assert (id(selector3) == id(selector4))
    assert (id(selector5) == id(selector6))
    assert (id(selector1) != id(selector7))
    assert (id(selector2) != id(selector7))
    assert (id(selector3) != id(selector7))
    assert (id(selector4) != id(selector7))
    assert (id(selector5) != id(selector7))
    assert (id(selector6) != id(selector7))
    # --------------------------------------------------------------
    assert (id(selector8) == id(selector9))
    assert (id(selector10) == id(selector11))
    assert (id(selector12) == id(selector13))
    assert (id(selector8) != id(selector14))
    assert (id(selector9) != id(selector14))
    assert (id(selector10) != id(selector14))
    assert (id(selector11) != id(selector14))
    assert (id(selector12) != id(selector14))
    assert (id(selector13) != id(selector14))
    # --------------------------------------------------------------
    assert (id(selector1) != id(selector8))
    assert (id(selector2) != id(selector9))
    assert (id(selector3) != id(selector10))
    assert (id(selector4) != id(selector11))
    assert (id(selector5) != id(selector12))
    assert (id(selector6) != id(selector13))
    assert (id(selector7) != id(selector14))
    # --------------------------------------------------------------
    assert (len(Selector._dict_of_selectors) == 8)
    del selector1
    del selector2
    del selector3
    del selector4
    del selector5
    del selector6
    del selector7
    del selector8
    del selector9
    del selector10
    del selector11
    del selector12
    del selector13
    del selector14
    assert (len(Selector._dict_of_selectors) == 0)

def test_Selector_deletion_process():
    # --------------------------------------------------------------
    assert (len(Selector._dict_of_selectors) == 0)
    selector1 = Selector("a", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 1)
    selector2 = Selector("a", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 1)
    selector3 = Selector("a", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 2)
    selector4 = Selector("a", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 2)
    selector5 = Selector("a", Operator.LESS, 52)
    assert (len(Selector._dict_of_selectors) == 3)
    selector6 = Selector("a", Operator.LESS, 52)
    assert (len(Selector._dict_of_selectors) == 3)
    selector7 = Selector("a", Operator.GREATER, 52)
    assert (len(Selector._dict_of_selectors) == 4)
    selector8 = Selector("qwe", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 5)
    selector9 = Selector("qwe", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 5)
    selector10 = Selector("qwe", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 6)
    selector11 = Selector("qwe", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 6)
    selector12 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 7)
    selector13 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 7)
    selector14 = Selector("qwe", Operator.GREATER_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 8)
    # --------------------------------------------------------------
    assert (len(Selector._dict_of_selectors) == 8)
    del selector1
    assert (len(Selector._dict_of_selectors) == 8)
    del selector2
    assert (len(Selector._dict_of_selectors) == 7)
    del selector3
    assert (len(Selector._dict_of_selectors) == 7)
    del selector4
    assert (len(Selector._dict_of_selectors) == 6)
    del selector5
    assert (len(Selector._dict_of_selectors) == 6)
    del selector6
    assert (len(Selector._dict_of_selectors) == 5)
    del selector7
    assert (len(Selector._dict_of_selectors) == 4)
    del selector8
    assert (len(Selector._dict_of_selectors) == 4)
    del selector9
    assert (len(Selector._dict_of_selectors) == 3)
    del selector10
    assert (len(Selector._dict_of_selectors) == 3)
    del selector11
    assert (len(Selector._dict_of_selectors) == 2)
    del selector12
    assert (len(Selector._dict_of_selectors) == 2)
    del selector13
    assert (len(Selector._dict_of_selectors) == 1)
    del selector14
    assert (len(Selector._dict_of_selectors) == 0)
    # --------------------------------------------------------------
    assert (len(Selector._dict_of_selectors) == 0)
    selector1 = Selector("a", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 1)
    selector2 = Selector("a", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 1)
    selector3 = Selector("a", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 2)
    selector4 = Selector("a", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 2)
    selector5 = Selector("a", Operator.LESS, 52)
    assert (len(Selector._dict_of_selectors) == 3)
    selector6 = Selector("a", Operator.LESS, 52)
    assert (len(Selector._dict_of_selectors) == 3)
    selector7 = Selector("a", Operator.GREATER, 52)
    assert (len(Selector._dict_of_selectors) == 4)
    selector8 = Selector("qwe", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 5)
    selector9 = Selector("qwe", Operator.EQUAL, 23)
    assert (len(Selector._dict_of_selectors) == 5)
    selector10 = Selector("qwe", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 6)
    selector11 = Selector("qwe", Operator.EQUAL, 45)
    assert (len(Selector._dict_of_selectors) == 6)
    selector12 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 7)
    selector13 = Selector("qwe", Operator.LESS_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 7)
    selector14 = Selector("qwe", Operator.GREATER_OR_EQUAL, 52)
    assert (len(Selector._dict_of_selectors) == 8)
    # --------------------------------------------------------------
    assert (len(Selector._dict_of_selectors) == 8)
    selector14 = None
    assert (len(Selector._dict_of_selectors) == 7)
    selector13 = None
    assert (len(Selector._dict_of_selectors) == 7)
    selector12 = None
    assert (len(Selector._dict_of_selectors) == 6)
    selector11 = None
    assert (len(Selector._dict_of_selectors) == 6)
    selector10 = None
    assert (len(Selector._dict_of_selectors) == 5)
    selector9 = None
    assert (len(Selector._dict_of_selectors) == 5)
    selector8 = None
    assert (len(Selector._dict_of_selectors) == 4)
    selector7 = None
    assert (len(Selector._dict_of_selectors) == 3)
    selector6 = None
    assert (len(Selector._dict_of_selectors) == 3)
    selector5 = None
    assert (len(Selector._dict_of_selectors) == 2)
    selector4 = None
    assert (len(Selector._dict_of_selectors) == 2)
    selector3 = None
    assert (len(Selector._dict_of_selectors) == 1)
    selector2 = None
    assert (len(Selector._dict_of_selectors) == 1)
    selector1 = None
    assert (len(Selector._dict_of_selectors) == 0)

def test_Selector_attributes():
    # These examples must run ok.
    selector1 = Selector("attribute_name_1", Operator.EQUAL, "value_1")
    assert(selector1.attribute_name == "attribute_name_1")
    assert(selector1.operator == Operator.EQUAL)
    assert(selector1.value == "value_1")
    assert(type(selector1.value) is str)
    assert(str(selector1) == "attribute_name_1 = \'value_1\'")
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

def test_Selector_match_method():
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
    # These examples must raise an exception (the exception that appears in 'except').
    try:
        selector2.match("a", "30") # The method raises a TypeError exception with these parameters, because we cannot apply the operator '>' between a str and an int.
        assert(False)
    except TypeError:
        assert(True)
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
