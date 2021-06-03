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
from subgroups.quality_measures.npv import NPV
from subgroups.quality_measures.absolute_wracc import AbsoluteWRAcc
from subgroups.quality_measures.specificity import Specificity
from subgroups.quality_measures.irr import IRR
from subgroups.quality_measures.f1_score import F1Score
from subgroups.quality_measures.youden import Youden
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
    npv = NPV()
    absolute_wracc = AbsoluteWRAcc()
    specificity = Specificity()
    irr = IRR()
    f1_score = F1Score()
    youden = Youden()
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
    assert (type(npv) == NPV)
    assert (type(absolute_wracc) == AbsoluteWRAcc)
    assert (type(specificity) == Specificity)
    assert (type(irr) == IRR)
    assert (type(f1_score) == F1Score)
    assert (type(youden) == Youden)
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
    assert (id(npv) == id(NPV()))
    assert (id(absolute_wracc) == id(AbsoluteWRAcc()))
    assert (id(wracc) != id(absolute_wracc))
    assert (id(WRAcc()) != id(AbsoluteWRAcc()))
    assert (id(specificity) == id(Specificity()))
    assert (id(irr) == id(IRR()))
    assert (id(f1_score) == id(F1Score()))
    assert (id(youden) == id(Youden()))
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
    assert (npv.get_name() == "NPV")
    assert (absolute_wracc.get_name() == "AbsoluteWRAcc")
    assert (specificity.get_name() == "Specificity")
    assert (irr.get_name() == "IRR")
    assert (f1_score.get_name() == "F1Score")
    assert (youden.get_name() == "Youden")
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
    assert (len(npv.optimistic_estimate_of()) == 0)
    assert (len(absolute_wracc.optimistic_estimate_of()) == 0)
    assert (len(specificity.optimistic_estimate_of()) == 0)
    assert (len(irr.optimistic_estimate_of()) == 0)
    assert (len(f1_score.optimistic_estimate_of()) == 0)
    assert (len(youden.optimistic_estimate_of()) == 0)

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
    tn = FP - fp
    fn = TP - tp
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
    assert (NPV()(dict_of_parameters) == tn/(tn+fn))
    assert (AbsoluteWRAcc()(dict_of_parameters) == abs( (( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )) ))
    assert (AbsoluteWRAcc()(dict_of_parameters) == abs(WRAcc()(dict_of_parameters)))
    assert (Specificity()(dict_of_parameters) == (FP-fp)/FP)
    assert (IRR()(dict_of_parameters) == (tp/n - 1 + (FP-fp)/FP))
    assert (F1Score()(dict_of_parameters) == (2*tp)/(tp+fp+TP))
    assert (Youden()(dict_of_parameters) == (tp/TP) + ((FP-fp)/FP) - 1)
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
    assert (NPV()(dict_of_parameters) == NPV().compute(dict_of_parameters))
    assert (AbsoluteWRAcc()(dict_of_parameters) == AbsoluteWRAcc().compute(dict_of_parameters))
    assert (AbsoluteWRAcc()(dict_of_parameters) == abs(WRAcc().compute(dict_of_parameters)))
    assert (Specificity()(dict_of_parameters) == Specificity().compute(dict_of_parameters))
    assert (IRR()(dict_of_parameters) == IRR().compute(dict_of_parameters))
    assert (F1Score()(dict_of_parameters) == F1Score().compute(dict_of_parameters))
    assert (Youden()(dict_of_parameters) == Youden().compute(dict_of_parameters))
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
        NPV()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        NPV().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        AbsoluteWRAcc()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        AbsoluteWRAcc().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Specificity()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Specificity().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        IRR()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        IRR().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        F1Score()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        F1Score().compute(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Youden()(3)
        assert (False)
    except TypeError:
        assert (True)
    try:
        Youden().compute(3)
        assert (False)
    except TypeError:
        assert (True)
