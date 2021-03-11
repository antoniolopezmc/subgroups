# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the file 'algorithms/sdmap.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.sdmap import SDMap
from subgroups.quality_measures.wracc import WRAcc
from subgroups.exceptions import ParametersError, TargetAttributeTypeError

def test_SDMap_init_method():
    try:
        SDMap("hello", 0.85)
        assert (False)
    except TypeError:
        assert (True)
    try:
        SDMap(WRAcc(), "hello")
        assert (False)
    except TypeError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_tp=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_fp=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_n=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_fp=0, minimum_n=0)
        assert (False)
    except ParametersError:
        assert (True)
    try:
        SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0, minimum_n=0)
        assert (False)
    except ParametersError:
        assert (True)

def test_SDMap_fit_method_1():
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be discrete (type 'str').
        sdmap = SDMap(WRAcc(), 0.85, minimum_tp=0, minimum_fp=0)
        sdmap.fit(df, ("class", 0))
        assert (False)
    except TargetAttributeTypeError:
        assert (True)

def test_SDMap_fit_method_2():
    df = DataFrame({"a1" : [0,1,2,2], "a2" : [41,41,11,41], "a3" : [78,45,21,36], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    sdmap = SDMap(WRAcc(), 0, minimum_n=0)
    subgroups = sdmap.fit(df, target)

