# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the folder 'quality_measures'.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.quality_measures.support import Support
from subgroups.quality_measures.coverage import Coverage
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.binomial_test import BinomialTest
from subgroups.quality_measures.qg import Qg
from subgroups.quality_measures.sensitivity import Sensitivity
from subgroups.quality_measures.ppv import PPV
from subgroups.quality_measures.wracc_optimistic_estimate_1 import WRAccOptimisticEstimate1
from subgroups.quality_measures.binomial_test_optimistic_estimate_1 import BinomialTestOptimisticEstimate1
from subgroups.quality_measures.piatetsky_shapiro import PiatetskyShapiro
from subgroups.quality_measures.piatetsky_shapiro_optimistic_estimate_1 import PiatetskyShapiroOptimisticEstimate1
from subgroups.quality_measures.piatetsky_shapiro_optimistic_estimate_2 import PiatetskyShapiroOptimisticEstimate2
from subgroups.quality_measures.precision_gain import PrecisionGain
from subgroups.quality_measures.wracc_absolute_value import WRAccAbsoluteValue
from math import sqrt

def test_quality_measures():
    support = Support()
    coverage = Coverage()
    wracc = WRAcc()
    binomial_test = BinomialTest()
    qg = Qg()
    sensitivity = Sensitivity()
    ppv = PPV()
    wracc_optimistic_estimate_1 = WRAccOptimisticEstimate1()
    binomial_test_optimistic_estimate_1 = BinomialTestOptimisticEstimate1()
    piatetsky_shapiro = PiatetskyShapiro()
    piatetsky_shapiro_optimistic_estimate_1 = PiatetskyShapiroOptimisticEstimate1()
    piatetsky_shapiro_optimistic_estimate_2 = PiatetskyShapiroOptimisticEstimate2()
    precision_gain = PrecisionGain()
    wracc_absolute_value = WRAccAbsoluteValue()
    # --------------------------------------------------
    assert (type(support) == Support)
    assert (type(coverage) == Coverage)
    assert (type(wracc) == WRAcc)
    assert (type(binomial_test) == BinomialTest)
    assert (type(qg) == Qg)
    assert (type(sensitivity) == Sensitivity)
    assert (type(ppv) == PPV)
    assert (type(wracc_optimistic_estimate_1) == WRAccOptimisticEstimate1)
    assert (type(binomial_test_optimistic_estimate_1) == BinomialTestOptimisticEstimate1)
    assert (type(piatetsky_shapiro) == PiatetskyShapiro)
    assert (type(piatetsky_shapiro_optimistic_estimate_1) == PiatetskyShapiroOptimisticEstimate1)
    assert (type(piatetsky_shapiro_optimistic_estimate_2) == PiatetskyShapiroOptimisticEstimate2)
    assert (type(precision_gain) == PrecisionGain)
    assert (type(wracc_absolute_value) == WRAccAbsoluteValue)
    # --------------------------------------------------
    assert (id(support) == id(Support()))
    assert (id(coverage) == id(Coverage()))
    assert (id(wracc) == id(WRAcc()))
    assert (id(binomial_test) == id(BinomialTest()))
    assert (id(qg) == id(Qg()))
    assert (id(sensitivity) == id(Sensitivity()))
    assert (id(ppv) == id(PPV()))
    assert (id(wracc_optimistic_estimate_1) == id(WRAccOptimisticEstimate1()))
    assert (id(binomial_test_optimistic_estimate_1) == id(BinomialTestOptimisticEstimate1()))
    assert (id(piatetsky_shapiro) == id(PiatetskyShapiro()))
    assert (id(piatetsky_shapiro_optimistic_estimate_1) == id(PiatetskyShapiroOptimisticEstimate1()))
    assert (id(piatetsky_shapiro_optimistic_estimate_2) == id(PiatetskyShapiroOptimisticEstimate2()))
    assert (id(precision_gain) == id(PrecisionGain()))
    assert (id(wracc_absolute_value) == id(WRAccAbsoluteValue()))
    assert (id(wracc) != id(wracc_absolute_value))
    assert (id(WRAcc()) != id(WRAccAbsoluteValue()))
    # --------------------------------------------------
    assert (support.get_name() == "Support")
    assert (coverage.get_name() == "Coverage")
    assert (wracc.get_name() == "WRAcc")
    assert (binomial_test.get_name() == "BinomialTest")
    assert (qg.get_name() == "Qg")
    assert (sensitivity.get_name() == "Sensitivity")
    assert (ppv.get_name() == "PPV")
    assert (wracc_optimistic_estimate_1.get_name() == "WRAccOptimisticEstimate1")
    assert (binomial_test_optimistic_estimate_1.get_name() == "BinomialTestOptimisticEstimate1")
    assert (piatetsky_shapiro.get_name() == "PiatetskyShapiro")
    assert (piatetsky_shapiro_optimistic_estimate_1.get_name() == "PiatetskyShapiroOptimisticEstimate1")
    assert (piatetsky_shapiro_optimistic_estimate_2.get_name() == "PiatetskyShapiroOptimisticEstimate2")
    assert (precision_gain.get_name() == "PrecisionGain")
    assert (wracc_absolute_value.get_name() == "WRAccAbsoluteValue")
    # --------------------------------------------------
    assert (len(support.optimistic_estimate_of()) == 0)
    assert (len(coverage.optimistic_estimate_of()) == 0)
    assert (len(wracc.optimistic_estimate_of()) == 0)
    assert (len(binomial_test.optimistic_estimate_of()) == 0)
    assert (len(qg.optimistic_estimate_of()) == 0)
    assert (len(sensitivity.optimistic_estimate_of()) == 0)
    assert (len(ppv.optimistic_estimate_of()) == 0)
    assert (len(wracc_optimistic_estimate_1.optimistic_estimate_of()) == 1)
    assert (len(binomial_test_optimistic_estimate_1.optimistic_estimate_of()) == 1)
    assert (len(piatetsky_shapiro.optimistic_estimate_of()) == 0)
    assert (len(piatetsky_shapiro_optimistic_estimate_1.optimistic_estimate_of()) == 1)
    assert (len(piatetsky_shapiro_optimistic_estimate_2.optimistic_estimate_of()) == 1)
    assert (len(precision_gain.optimistic_estimate_of()) == 0)
    assert (len(wracc_absolute_value.optimistic_estimate_of()) == 0)

def test_quality_measures_compute():
    tp = 3
    fp = 4
    TP = 5
    FP = 6
    g = 0.1
    n = tp + fp
    N = TP + FP
    p = tp / n # p = tp / ( tp + fp )
    p0 = TP / N # p0 = TP / ( TP + FP )
    dict_of_parameters = dict({QualityMeasure.SUBGROUP_PARAMETER_tp : tp, QualityMeasure.SUBGROUP_PARAMETER_fp : fp, QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP, "g" : g})
    # --------------------------------------------------
    assert (Support()(dict_of_parameters) == (tp / ( TP + FP )))
    assert (Coverage()(dict_of_parameters) == (( tp + fp ) / ( TP + FP )))
    assert (WRAcc()(dict_of_parameters) == (( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )))
    assert (BinomialTest()(dict_of_parameters) == (( ( (p-p0)*sqrt(n) ) / ( sqrt(p0*(1-p0)) ) ) * sqrt( N / ( N - n ) )))
    assert (Qg()(dict_of_parameters) == (tp / ( fp + g )))
    assert (Sensitivity()(dict_of_parameters) == (tp / TP))
    assert (PPV()(dict_of_parameters) == (tp / ( tp + fp )))
    assert (WRAccOptimisticEstimate1()(dict_of_parameters) == ( (tp*tp)/(tp+fp) ) * ( 1 - ( TP/(TP+FP) ) ))
    assert (BinomialTestOptimisticEstimate1()(dict_of_parameters) == (( sqrt(tp) ) * ( 1 - ( (TP)/(TP+FP) ) )))
    assert (PiatetskyShapiro()(dict_of_parameters) == n*(p-p0))
    assert (PiatetskyShapiroOptimisticEstimate1()(dict_of_parameters) == n*(1-p0))
    assert (PiatetskyShapiroOptimisticEstimate2()(dict_of_parameters) == n*p*(1-p0))
    assert (PrecisionGain()(dict_of_parameters) == ( tp / ( tp + fp ) ) - ( TP / ( TP + FP ) ))
    assert (WRAccAbsoluteValue()(dict_of_parameters) == abs( (( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )) ))
    assert (WRAccAbsoluteValue()(dict_of_parameters) == abs(WRAcc()(dict_of_parameters)))
    # --------------------------------------------------
    assert (Support()(dict_of_parameters) == Support().compute(dict_of_parameters))
    assert (Coverage()(dict_of_parameters) == Coverage().compute(dict_of_parameters))
    assert (WRAcc()(dict_of_parameters) == WRAcc().compute(dict_of_parameters))
    assert (BinomialTest()(dict_of_parameters) == BinomialTest().compute(dict_of_parameters))
    assert (Qg()(dict_of_parameters) == Qg().compute(dict_of_parameters))
    assert (Sensitivity()(dict_of_parameters) == Sensitivity().compute(dict_of_parameters))
    assert (PPV()(dict_of_parameters) == PPV().compute(dict_of_parameters))
    assert (WRAccOptimisticEstimate1()(dict_of_parameters) == WRAccOptimisticEstimate1().compute(dict_of_parameters))
    assert (BinomialTestOptimisticEstimate1()(dict_of_parameters) == BinomialTestOptimisticEstimate1().compute(dict_of_parameters))
    assert (PiatetskyShapiro()(dict_of_parameters) == PiatetskyShapiro().compute(dict_of_parameters))
    assert (PiatetskyShapiroOptimisticEstimate1()(dict_of_parameters) == PiatetskyShapiroOptimisticEstimate1().compute(dict_of_parameters))
    assert (PiatetskyShapiroOptimisticEstimate2()(dict_of_parameters) == PiatetskyShapiroOptimisticEstimate2().compute(dict_of_parameters))
    assert (PrecisionGain()(dict_of_parameters) == PrecisionGain().compute(dict_of_parameters))
    assert (WRAccAbsoluteValue()(dict_of_parameters) == WRAccAbsoluteValue().compute(dict_of_parameters))
    assert (WRAccAbsoluteValue()(dict_of_parameters) == abs(WRAcc().compute(dict_of_parameters)))
    # --------------------------------------------------
    try:
        Support()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Support().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Coverage()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Coverage().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        WRAcc()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        WRAcc().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        BinomialTest()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        BinomialTest().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Qg()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Qg().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Sensitivity()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Sensitivity().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PPV()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PPV().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        WRAccOptimisticEstimate1()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        WRAccOptimisticEstimate1().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        BinomialTestOptimisticEstimate1()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        BinomialTestOptimisticEstimate1().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PiatetskyShapiro()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PiatetskyShapiro().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PiatetskyShapiroOptimisticEstimate1()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PiatetskyShapiroOptimisticEstimate1().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PiatetskyShapiroOptimisticEstimate2()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PiatetskyShapiroOptimisticEstimate2().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PrecisionGain()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        PrecisionGain().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        WRAccAbsoluteValue()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        WRAccAbsoluteValue().compute(3)
        assert (False)
    except TypeError:
        assert (True)
