# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

""" Tests of the functionality contained in the folder 'quality_measures'.
"""

from subgroups.quality_measures._base import QualityMeasure
from subgroups.quality_measures.support import Support
from subgroups.quality_measures.coverage import Coverage
from subgroups.quality_measures.wracc import WRAcc
from subgroups.quality_measures.binomial_test import BinomialTest
from subgroups.quality_measures.qg import Qg
from subgroups.quality_measures.sensitivity import Sensitivity
from subgroups.quality_measures.ppv import PPV
from subgroups.quality_measures.wracc_upper_bound_1 import WRAccUpperBound1
from subgroups.quality_measures.binomial_test_upper_bound_1 import BinomialTestUpperBound1
from subgroups.quality_measures.piatetsky_shapiro import PiatetskyShapiro
from math import sqrt

def test_quality_measures():
    support = Support()
    coverage = Coverage()
    wracc = WRAcc()
    binomial_test = BinomialTest()
    qg = Qg()
    sensitivity = Sensitivity()
    ppv = PPV()
    wracc_upper_bound_1 = WRAccUpperBound1()
    binomial_test_upper_bound_1 = BinomialTestUpperBound1()
    piatetsky_shapiro = PiatetskyShapiro()
    assert (id(support) == id(Support()))
    assert (id(coverage) == id(Coverage()))
    assert (id(wracc) == id(WRAcc()))
    assert (id(binomial_test) == id(BinomialTest()))
    assert (id(qg) == id(Qg()))
    assert (id(sensitivity) == id(Sensitivity()))
    assert (id(ppv) == id(PPV()))
    assert (id(wracc_upper_bound_1) == id(WRAccUpperBound1()))
    assert (id(binomial_test_upper_bound_1) == id(BinomialTestUpperBound1()))
    assert (id(piatetsky_shapiro) == id(PiatetskyShapiro()))
    assert (support.get_name() == "Support")
    assert (coverage.get_name() == "Coverage")
    assert (wracc.get_name() == "WRAcc")
    assert (binomial_test.get_name() == "BinomialTest")
    assert (qg.get_name() == "Qg")
    assert (sensitivity.get_name() == "Sensitivity")
    assert (ppv.get_name() == "PPV")
    assert (wracc_upper_bound_1.get_name() == "WRAccUpperBound1")
    assert (binomial_test_upper_bound_1.get_name() == "BinomialTestUpperBound1")
    assert (piatetsky_shapiro.get_name() == "PiatetskyShapiro")
    assert (len(support.upper_bound_of()) == 0)
    assert (len(coverage.upper_bound_of()) == 0)
    assert (len(wracc.upper_bound_of()) == 0)
    assert (len(binomial_test.upper_bound_of()) == 0)
    assert (len(qg.upper_bound_of()) == 0)
    assert (len(sensitivity.upper_bound_of()) == 0)
    assert (len(ppv.upper_bound_of()) == 0)
    assert (len(wracc_upper_bound_1.upper_bound_of()) == 1)
    assert (len(binomial_test_upper_bound_1.upper_bound_of()) == 1)
    assert (len(piatetsky_shapiro.upper_bound_of()) == 0)

def test_quality_measures_compute():
    tp = 3
    fp = 4
    TP = 5
    FP = 6
    g = 0.1
    n = tp + fp
    N = TP + FP
    p = tp / n # p = tp / ( tp + fp )
    p0 = TP / N # p0 = TP / ( TP + FP 
    dict_of_parameters = dict({QualityMeasure.SUBGROUP_PARAMETER_tp : tp, QualityMeasure.SUBGROUP_PARAMETER_fp : fp, QualityMeasure.SUBGROUP_PARAMETER_TP : TP, QualityMeasure.SUBGROUP_PARAMETER_FP : FP, "g" : g})
    assert (Support()(dict_of_parameters) == (tp / ( TP + FP )))
    assert (Coverage()(dict_of_parameters) == (( tp + fp ) / ( TP + FP )))
    assert (WRAcc()(dict_of_parameters) == (( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )))
    assert (BinomialTest()(dict_of_parameters) == (( ( (p-p0)*sqrt(n) ) / ( sqrt(p0*(1-p0)) ) ) * sqrt( N / ( N - n ) )))
    assert (Qg()(dict_of_parameters) == (tp / ( fp + g )))
    assert (Sensitivity()(dict_of_parameters) == (tp / TP))
    assert (PPV()(dict_of_parameters) == (tp / ( tp + fp )))
    assert (WRAccUpperBound1()(dict_of_parameters) == ( (tp*tp)/(tp+fp) ) * ( 1 - ( TP/(TP+FP) ) ))
    assert (BinomialTestUpperBound1()(dict_of_parameters) == (( sqrt(tp) ) * ( 1 - ( (TP)/(TP+FP) ) )))
    assert (PiatetskyShapiro()(dict_of_parameters) == n*(p-p0))
    assert (Support()(dict_of_parameters) == Support().compute(dict_of_parameters))
    assert (Coverage()(dict_of_parameters) == Coverage().compute(dict_of_parameters))
    assert (WRAcc()(dict_of_parameters) == WRAcc().compute(dict_of_parameters))
    assert (BinomialTest()(dict_of_parameters) == BinomialTest().compute(dict_of_parameters))
    assert (Qg()(dict_of_parameters) == Qg().compute(dict_of_parameters))
    assert (Sensitivity()(dict_of_parameters) == Sensitivity().compute(dict_of_parameters))
    assert (PPV()(dict_of_parameters) == PPV().compute(dict_of_parameters))
    assert (WRAccUpperBound1()(dict_of_parameters) == WRAccUpperBound1().compute(dict_of_parameters))
    assert (BinomialTestUpperBound1()(dict_of_parameters) == BinomialTestUpperBound1().compute(dict_of_parameters))
    assert (PiatetskyShapiro()(dict_of_parameters) == PiatetskyShapiro().compute(dict_of_parameters))
