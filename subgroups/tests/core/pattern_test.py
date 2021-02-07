# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'core/pattern.py'.
"""

from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.operator import Operator

def test_Pattern():
    assert (Pattern.generate_from_str("[]") == Pattern([]))
    pattern_1 = Pattern([Selector("name", Operator.EQUAL, "name1"), Selector("age", Operator.LESS, 25), \
                        Selector("age", Operator.GREATER, 78), Selector("att2", Operator.GREATER_OR_EQUAL, 25), \
                        Selector("age", Operator.GREATER, 78), Selector("att2", Operator.GREATER_OR_EQUAL, 25)])
    assert (Pattern.generate_from_str("[age < 25, name = 'name1', name = name1, att2 >= 25, age > 78, age < 25]") == pattern_1)
    assert (len(pattern_1) == 4)
    pattern_2 = Pattern([Selector("name", Operator.EQUAL, "name1"), Selector("name", Operator.EQUAL, "name1"), \
                        Selector("name", Operator.EQUAL, "name1"), Selector("name", Operator.EQUAL, "name1"), \
                        Selector("age", Operator.GREATER, 78), Selector("name", Operator.EQUAL, "name1")])
    assert (len(pattern_2) == 2)
    assert (Selector("name", Operator.EQUAL, "name1") in pattern_2)
    assert (Selector("att2", Operator.GREATER_OR_EQUAL, 128) not in pattern_2)
    assert (Selector("att2", Operator.GREATER_OR_EQUAL, 128) not in pattern_1)
    pattern_2.add_selector(Selector("att2", Operator.GREATER_OR_EQUAL, 128))
    assert (len(pattern_2) == 3)
    assert (Selector("att2", Operator.GREATER_OR_EQUAL, 128) in pattern_2)
    assert (pattern_2.get_selector(0) == Selector("age", Operator.GREATER, 78))
    pattern_2.add_selector(Selector("aaaaa", Operator.GREATER_OR_EQUAL, -789))
    assert (pattern_2.get_selector(0) == Selector("aaaaa", Operator.GREATER_OR_EQUAL, -789))
    assert (len(pattern_2) == 4)
    assert (str(pattern_2) == str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = name1]")))
    assert (str(pattern_2) == str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = 'name1']")))
    assert (str(pattern_2) == str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = name1, aaaaa >= -789, age > 78, att2 >= 128, name = name1]")))
    assert (str(pattern_2) == str(Pattern.generate_from_str("[aaaaa >= -789, age > 78, att2 >= 128, name = 'name1', aaaaa >= -789, age > 78, att2 >= 128, name = 'name1']")))
    assert (str(pattern_2) == "[aaaaa >= -789, age > 78, att2 >= 128, name = 'name1']")
    assert (pattern_1 == pattern_1)
    assert (pattern_1 == pattern_1.copy())
    assert (pattern_1 != pattern_2)
    assert (pattern_1 != pattern_2.copy())
    index = 0
    for elem in pattern_2:
        assert (elem == pattern_2.get_selector(index))
        index = index + 1
    pattern_2.remove_selector(Selector.generate_from_str("age > 78"))
    assert (len(pattern_2) == 3)
    assert (pattern_2.get_selector(0) == Selector.generate_from_str("aaaaa >= -789"))
    assert (pattern_2.get_selector(1) == Selector.generate_from_str("att2 >= 128"))
    pattern_2.remove_selector(Selector.generate_from_str("age > 78"))
    assert (len(pattern_2) == 3)
    assert (pattern_2.get_selector(0) == Selector.generate_from_str("aaaaa >= -789"))
    assert (pattern_2.get_selector(1) == Selector.generate_from_str("att2 >= 128"))
    pattern_2.add_selector(Selector.generate_from_str("name = 'name1'"))
    assert (len(pattern_2) == 3)
    assert (pattern_2.get_selector(0) == Selector.generate_from_str("aaaaa >= -789"))
    assert (pattern_2.get_selector(1) == Selector.generate_from_str("att2 >= 128"))
    pattern_3 = Pattern([])
    assert (len(pattern_3) == 0)
    pattern_3.remove_selector(Selector("age", Operator.GREATER, 78))
    assert (len(pattern_3) == 0)
    try:
        pattern_3.get_selector(125)
        assert (False)
    except IndexError:
        assert (True)
    pattern_4 = Pattern.generate_from_str("[age < 25, name = 'name1', name = name1, att2 >= 25, age > 78, age < 25]")
    assert (len(pattern_4) == 4)
    pattern_4.add_selector(Selector("zzzz", Operator.EQUAL, "value4"))
    assert (len(pattern_4) == 5)
    pattern_4.remove_selector(Selector("zzzz", Operator.EQUAL, "value4"))
    assert (len(pattern_4) == 4)
    assert (str(pattern_4) == "[age < 25, age > 78, att2 >= 25, name = 'name1']")
    pattern_4.remove_selector_by_index(1)
    assert (len(pattern_4) == 3)
    assert (str(pattern_4) == "[age < 25, att2 >= 25, name = 'name1']")
    try:
        pattern_3.remove_selector_by_index(125)
        assert (False)
    except IndexError:
        assert (True)
    Pattern([]).remove_selector(Selector.generate_from_str("aaaaa >= -789"))
