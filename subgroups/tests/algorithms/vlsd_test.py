# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the file 'algorithms/vlsd.py'.
"""

from pandas import DataFrame
from subgroups.algorithms.vlsd import VLSD
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
from subgroups.quality_measures.qg import Qg
from subgroups.exceptions import DatasetAttributeTypeError
from subgroups.core.subgroup import Subgroup
import os

def test_VLSD_init_method_1():
    dictionary = dict()
    vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, additional_parameters_for_the_quality_measure=dictionary, additional_parameters_for_the_optimistic_estimate=dictionary)
    assert (len(vlsd.additional_parameters_for_the_quality_measure) == 0)
    assert (len(vlsd.additional_parameters_for_the_optimistic_estimate) == 0)
    assert (vlsd.additional_parameters_for_the_quality_measure == dictionary)
    assert (vlsd.additional_parameters_for_the_optimistic_estimate == dictionary)
    assert (vlsd.additional_parameters_for_the_quality_measure == vlsd.additional_parameters_for_the_optimistic_estimate)
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_optimistic_estimate) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(vlsd.additional_parameters_for_the_optimistic_estimate))
    dictionary = dict({"g" : 0.5})
    vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, additional_parameters_for_the_quality_measure=dictionary, additional_parameters_for_the_optimistic_estimate=dictionary)
    assert (len(vlsd.additional_parameters_for_the_quality_measure) == 1)
    assert (len(vlsd.additional_parameters_for_the_optimistic_estimate) == 1)
    assert (vlsd.additional_parameters_for_the_quality_measure == dictionary)
    assert (vlsd.additional_parameters_for_the_optimistic_estimate == dictionary)
    assert (vlsd.additional_parameters_for_the_quality_measure == vlsd.additional_parameters_for_the_optimistic_estimate)
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_optimistic_estimate) != id(dictionary))
    assert (id(vlsd.additional_parameters_for_the_quality_measure) != id(vlsd.additional_parameters_for_the_optimistic_estimate))
    assert (vlsd.additional_parameters_for_the_quality_measure["g"] == 0.5)
    assert (vlsd.additional_parameters_for_the_optimistic_estimate["g"] == 0.5)
    vlsd.additional_parameters_for_the_optimistic_estimate["g"] = 0.1
    assert (vlsd.additional_parameters_for_the_quality_measure != vlsd.additional_parameters_for_the_optimistic_estimate)
    assert (vlsd.additional_parameters_for_the_quality_measure["g"] == 0.5)
    assert (vlsd.additional_parameters_for_the_optimistic_estimate["g"] == 0.1)

def test_VLSD_init_method_2():
    vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -0.85)
    try:
        vlsd = VLSD(Qg(), -1, WRAccOptimisticEstimate1(), -0.85, additional_parameters_for_the_quality_measure={"Qg" : 0.2})
        assert (False)
    except ValueError:
        assert (True)

def test_VLSD_fit_method_1():
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -0.85)
        vlsd.fit(df, ("class", 0))
        assert (False)
    except DatasetAttributeTypeError:
        assert (True)
    try:
        df = DataFrame({"class" : [0,1,2,2]}) # The class must be nominal (type 'str').
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), 0.85)
        vlsd.fit(df, ("class", "0"))
        assert (False)
    except DatasetAttributeTypeError:
        assert (True)
    try:
        df = DataFrame({"att1" : [4,5,2,6], "class" : ["0","1","2","2"]}) # All the attributes must be nominal (type 'str').
        vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), 0.85)
        vlsd.fit(df, ("class", "0"))
        assert (False)
    except DatasetAttributeTypeError:
        assert (True)

def test_VLSD_fit_method_2():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, write_results_in_file=True, file_path="./results.txt")
    vlsd.fit(df, target)
    assert (vlsd.visited_nodes == 25)
    list_of_written_results = []
    file_to_read = open("./results.txt", "r")
    for line in file_to_read:
        list_of_written_results.append(line)
    list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
    assert ( Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'") in list_of_subgroups )
    file_to_read.close()
    os.remove("./results.txt")

def test_VLSD_fit_method_3():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    vlsd = VLSD(WRAcc(), 0, WRAccOptimisticEstimate1(), 0, write_results_in_file=True, file_path="./results.txt")
    vlsd.fit(df, target)
    assert (vlsd.visited_nodes == 13)
    list_of_written_results = []
    file_to_read = open("./results.txt", "r")
    for line in file_to_read:
        list_of_written_results.append(line)
    list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
    assert ( Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'") in list_of_subgroups )
    file_to_read.close()
    os.remove("./results.txt")

def test_VLSD_fit_method_4():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    vlsd = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, write_results_in_file=True, file_path="./results.txt")
    vlsd.fit(df, target)
    assert (vlsd.visited_nodes == 12)
    list_of_written_results = []
    file_to_read = open("./results.txt", "r")
    for line in file_to_read:
        list_of_written_results.append(line)
    list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
    assert ( Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'") in list_of_subgroups )
    file_to_read.close()
    os.remove("./results.txt")

def test_VLSD_fit_method_5():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # IMPORTANT: the subgroup parameters TP and FP (inserted as additional parameters) must be deleted in the __init__ method.
    vlsd = VLSD(WRAcc(), 0.1, WRAccOptimisticEstimate1(), 0.1, additional_parameters_for_the_quality_measure={"TP" : 100000, "g" : 0.5}, additional_parameters_for_the_optimistic_estimate={"FP" : 100000, "g" : 0.4}, write_results_in_file=True, file_path="./results.txt")
    assert (len(vlsd.additional_parameters_for_the_quality_measure) == 1)
    vlsd.fit(df, target)
    assert (vlsd.visited_nodes == 12)
    list_of_written_results = []
    file_to_read = open("./results.txt", "r")
    for line in file_to_read:
        list_of_written_results.append(line)
    list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
    assert ( Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'") in list_of_subgroups )
    file_to_read.close()
    os.remove("./results.txt")

def test_VLSD_fit_method_6():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, sort_criterion_in_s1 = "quality-ascending", sort_criterion_in_other_sizes = "no-order", write_results_in_file=True, file_path="./results.txt")
    vlsd.fit(df, target)
    assert (vlsd.visited_nodes == 25)
    list_of_written_results = []
    file_to_read = open("./results.txt", "r")
    for line in file_to_read:
        list_of_written_results.append(line)
    list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
    assert ( Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'") in list_of_subgroups )
    file_to_read.close()
    os.remove("./results.txt")

def test_VLSD_fit_method_7():
    df = DataFrame({"a1" : ["a","b","c","c"], "a2" : ["q","q","s","q"], "a3" : ["f","g","h","k"], "class" : ["n","y","n","y"]})
    target = ("class", "y")
    # IMPORTANT: WRAcc quality measure is defined between -1 and 1.
    vlsd = VLSD(WRAcc(), -1, WRAccOptimisticEstimate1(), -1, sort_criterion_in_s1 = "no-order", sort_criterion_in_other_sizes = "quality-descending", write_results_in_file=True, file_path="./results.txt")
    vlsd.fit(df, target)
    assert (vlsd.visited_nodes == 25)
    list_of_written_results = []
    file_to_read = open("./results.txt", "r")
    for line in file_to_read:
        list_of_written_results.append(line)
    list_of_subgroups = [Subgroup.generate_from_str(elem.split(";")[0][:-1]) for elem in list_of_written_results]
    assert ( Subgroup.generate_from_str("Description: [a1 = a], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a3 = f], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = a, a3 = f, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = b, a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a3 = h], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a2 = s, a3 = h, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = f], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = f, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = g, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = h], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = h, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a1 = c, a2 = q], Target: class = 'y'") in list_of_subgroups )
    assert ( Subgroup.generate_from_str("Description: [a3 = k, a2 = q], Target: class = 'y'") in list_of_subgroups )
    file_to_read.close()
    os.remove("./results.txt")
