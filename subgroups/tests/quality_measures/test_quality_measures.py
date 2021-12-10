# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""Tests of the functionality contained in the folder 'quality_measures'.
"""

from subgroups.quality_measures.quality_measure import QualityMeasure
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
import unittest

class TestQualityMeasures(unittest.TestCase):

    def test_quality_measures_value_of_class_variables(self) -> None:
        self.assertEqual(QualityMeasure.TRUE_POSITIVES, "tp")
        self.assertEqual(QualityMeasure.FALSE_POSITIVES, "fp")
        self.assertEqual(QualityMeasure.TRUE_POPULATION, "TP")
        self.assertEqual(QualityMeasure.FALSE_POPULATION, "FP")

    def test_quality_measures_general(self) -> None:
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
        self.assertIs(type(support), Support)
        self.assertIs(type(coverage), Coverage)
        self.assertIs(type(wracc), WRAcc)
        self.assertIs(type(binomial_test), BinomialTest)
        self.assertIs(type(qg), Qg)
        self.assertIs(type(sensitivity), Sensitivity)
        self.assertIs(type(ppv), PPV)
        self.assertIs(type(wracc_optimistic_estimate_1), WRAccOptimisticEstimate1)
        self.assertIs(type(binomial_test_optimistic_estimate_1), BinomialTestOptimisticEstimate1)
        self.assertIs(type(piatetsky_shapiro), PiatetskyShapiro)
        self.assertIs(type(piatetsky_shapiro_optimistic_estimate_1), PiatetskyShapiroOptimisticEstimate1)
        self.assertIs(type(piatetsky_shapiro_optimistic_estimate_2), PiatetskyShapiroOptimisticEstimate2)
        self.assertIs(type(npv), NPV)
        self.assertIs(type(absolute_wracc), AbsoluteWRAcc)
        self.assertIs(type(specificity), Specificity)
        self.assertIs(type(irr), IRR)
        self.assertIs(type(f1_score), F1Score)
        self.assertIs(type(youden), Youden)
        # --------------------------------------------------
        self.assertEqual(id(support), id(Support()))
        self.assertEqual(id(coverage), id(Coverage()))
        self.assertEqual(id(wracc), id(WRAcc()))
        self.assertEqual(id(binomial_test), id(BinomialTest()))
        self.assertEqual(id(qg), id(Qg()))
        self.assertEqual(id(sensitivity), id(Sensitivity()))
        self.assertEqual(id(ppv), id(PPV()))
        self.assertEqual(id(wracc_optimistic_estimate_1), id(WRAccOptimisticEstimate1()))
        self.assertEqual(id(binomial_test_optimistic_estimate_1), id(BinomialTestOptimisticEstimate1()))
        self.assertEqual(id(piatetsky_shapiro), id(PiatetskyShapiro()))
        self.assertEqual(id(piatetsky_shapiro_optimistic_estimate_1), id(PiatetskyShapiroOptimisticEstimate1()))
        self.assertEqual(id(piatetsky_shapiro_optimistic_estimate_2), id(PiatetskyShapiroOptimisticEstimate2()))
        self.assertEqual(id(npv), id(NPV()))
        self.assertEqual(id(absolute_wracc), id(AbsoluteWRAcc()))
        self.assertNotEqual(id(wracc), id(absolute_wracc))
        self.assertNotEqual(id(WRAcc()), id(AbsoluteWRAcc()))
        self.assertEqual(id(specificity), id(Specificity()))
        self.assertEqual(id(irr), id(IRR()))
        self.assertEqual(id(f1_score), id(F1Score()))
        self.assertEqual(id(youden), id(Youden()))
        # --------------------------------------------------
        self.assertIs(support, Support())
        self.assertIs(coverage, Coverage())
        self.assertIs(wracc, WRAcc())
        self.assertIs(binomial_test, BinomialTest())
        self.assertIs(qg, Qg())
        self.assertIs(sensitivity, Sensitivity())
        self.assertIs(ppv, PPV())
        self.assertIs(wracc_optimistic_estimate_1, WRAccOptimisticEstimate1())
        self.assertIs(binomial_test_optimistic_estimate_1, BinomialTestOptimisticEstimate1())
        self.assertIs(piatetsky_shapiro, PiatetskyShapiro())
        self.assertIs(piatetsky_shapiro_optimistic_estimate_1, PiatetskyShapiroOptimisticEstimate1())
        self.assertIs(piatetsky_shapiro_optimistic_estimate_2, PiatetskyShapiroOptimisticEstimate2())
        self.assertIs(npv, NPV())
        self.assertIs(absolute_wracc, AbsoluteWRAcc())
        self.assertIsNot(wracc, absolute_wracc)
        self.assertIsNot(WRAcc(), AbsoluteWRAcc())
        self.assertIs(specificity, Specificity())
        self.assertIs(irr, IRR())
        self.assertIs(f1_score, F1Score())
        self.assertIs(youden, Youden())
        # --------------------------------------------------
        self.assertEqual(support.get_name(), "Support")
        self.assertEqual(coverage.get_name(), "Coverage")
        self.assertEqual(wracc.get_name(), "WRAcc")
        self.assertEqual(binomial_test.get_name(), "BinomialTest")
        self.assertEqual(qg.get_name(), "Qg")
        self.assertEqual(sensitivity.get_name(), "Sensitivity")
        self.assertEqual(ppv.get_name(), "PPV")
        self.assertEqual(wracc_optimistic_estimate_1.get_name(), "WRAccOptimisticEstimate1")
        self.assertEqual(binomial_test_optimistic_estimate_1.get_name(), "BinomialTestOptimisticEstimate1")
        self.assertEqual(piatetsky_shapiro.get_name(), "PiatetskyShapiro")
        self.assertEqual(piatetsky_shapiro_optimistic_estimate_1.get_name(), "PiatetskyShapiroOptimisticEstimate1")
        self.assertEqual(piatetsky_shapiro_optimistic_estimate_2.get_name(), "PiatetskyShapiroOptimisticEstimate2")
        self.assertEqual(npv.get_name(), "NPV")
        self.assertEqual(absolute_wracc.get_name(), "AbsoluteWRAcc")
        self.assertEqual(specificity.get_name(), "Specificity")
        self.assertEqual(irr.get_name(), "IRR")
        self.assertEqual(f1_score.get_name(), "F1Score")
        self.assertEqual(youden.get_name(), "Youden")
        # --------------------------------------------------
        self.assertEqual(len(support.optimistic_estimate_of()), 0)
        self.assertEqual(len(coverage.optimistic_estimate_of()), 0)
        self.assertEqual(len(wracc.optimistic_estimate_of()), 0)
        self.assertEqual(len(binomial_test.optimistic_estimate_of()), 0)
        self.assertEqual(len(qg.optimistic_estimate_of()), 0)
        self.assertEqual(len(sensitivity.optimistic_estimate_of()), 0)
        self.assertEqual(len(ppv.optimistic_estimate_of()), 0)
        self.assertEqual(len(wracc_optimistic_estimate_1.optimistic_estimate_of()), 1)
        self.assertEqual(len(binomial_test_optimistic_estimate_1.optimistic_estimate_of()), 1)
        self.assertEqual(len(piatetsky_shapiro.optimistic_estimate_of()), 0)
        self.assertEqual(len(piatetsky_shapiro_optimistic_estimate_1.optimistic_estimate_of()), 1)
        self.assertEqual(len(piatetsky_shapiro_optimistic_estimate_2.optimistic_estimate_of()), 1)
        self.assertEqual(len(npv.optimistic_estimate_of()), 0)
        self.assertEqual(len(absolute_wracc.optimistic_estimate_of()), 0)
        self.assertEqual(len(specificity.optimistic_estimate_of()), 0)
        self.assertEqual(len(irr.optimistic_estimate_of()), 0)
        self.assertEqual(len(f1_score.optimistic_estimate_of()), 0)
        self.assertEqual(len(youden.optimistic_estimate_of()), 0)

    def test_quality_measures_compute(self) -> None:
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
        dict_of_parameters = dict({QualityMeasure.TRUE_POSITIVES : tp, QualityMeasure.FALSE_POSITIVES : fp, QualityMeasure.TRUE_POPULATION : TP, QualityMeasure.FALSE_POPULATION : FP, "g" : g})
        # --------------------------------------------------
        self.assertEqual(Support()(dict_of_parameters), (tp / ( TP + FP )))
        self.assertEqual(Coverage()(dict_of_parameters), (( tp + fp ) / ( TP + FP )))
        self.assertEqual(WRAcc()(dict_of_parameters), (( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )))
        self.assertEqual(BinomialTest()(dict_of_parameters), (( ( (p-p0)*sqrt(n) ) / ( sqrt(p0*(1-p0)) ) ) * sqrt( N / ( N - n ) )))
        self.assertEqual(Qg()(dict_of_parameters), (tp / ( fp + g )))
        self.assertEqual(Sensitivity()(dict_of_parameters), (tp / TP))
        self.assertEqual(PPV()(dict_of_parameters), (tp / ( tp + fp )))
        self.assertEqual(WRAccOptimisticEstimate1()(dict_of_parameters), ( (tp*tp)/(tp+fp) ) * ( 1 - ( TP/(TP+FP) ) ))
        self.assertEqual(BinomialTestOptimisticEstimate1()(dict_of_parameters), (( sqrt(tp) ) * ( 1 - ( (TP)/(TP+FP) ) )))
        self.assertEqual(PiatetskyShapiro()(dict_of_parameters), n*(p-p0))
        self.assertEqual(PiatetskyShapiroOptimisticEstimate1()(dict_of_parameters), n*(1-p0))
        self.assertEqual(PiatetskyShapiroOptimisticEstimate2()(dict_of_parameters), n*p*(1-p0))
        self.assertEqual(NPV()(dict_of_parameters), tn/(tn+fn))
        self.assertEqual(AbsoluteWRAcc()(dict_of_parameters), abs( (( (tp+fp) / (TP+FP) ) * ( ( tp / (tp+fp) ) - ( TP / (TP+FP) ) )) ))
        self.assertEqual(AbsoluteWRAcc()(dict_of_parameters), abs(WRAcc()(dict_of_parameters)))
        self.assertEqual(Specificity()(dict_of_parameters), (FP-fp)/FP)
        self.assertEqual(IRR()(dict_of_parameters), (tp/n - 1 + (FP-fp)/FP))
        self.assertEqual(F1Score()(dict_of_parameters), (2*tp)/(tp+fp+TP))
        self.assertEqual(Youden()(dict_of_parameters), (tp/TP) + ((FP-fp)/FP) - 1)
        # --------------------------------------------------
        self.assertEqual(Support()(dict_of_parameters), Support().compute(dict_of_parameters))
        self.assertEqual(Coverage()(dict_of_parameters), Coverage().compute(dict_of_parameters))
        self.assertEqual(WRAcc()(dict_of_parameters), WRAcc().compute(dict_of_parameters))
        self.assertEqual(BinomialTest()(dict_of_parameters), BinomialTest().compute(dict_of_parameters))
        self.assertEqual(Qg()(dict_of_parameters), Qg().compute(dict_of_parameters))
        self.assertEqual(Sensitivity()(dict_of_parameters), Sensitivity().compute(dict_of_parameters))
        self.assertEqual(PPV()(dict_of_parameters), PPV().compute(dict_of_parameters))
        self.assertEqual(WRAccOptimisticEstimate1()(dict_of_parameters), WRAccOptimisticEstimate1().compute(dict_of_parameters))
        self.assertEqual(BinomialTestOptimisticEstimate1()(dict_of_parameters), BinomialTestOptimisticEstimate1().compute(dict_of_parameters))
        self.assertEqual(PiatetskyShapiro()(dict_of_parameters), PiatetskyShapiro().compute(dict_of_parameters))
        self.assertEqual(PiatetskyShapiroOptimisticEstimate1()(dict_of_parameters), PiatetskyShapiroOptimisticEstimate1().compute(dict_of_parameters))
        self.assertEqual(PiatetskyShapiroOptimisticEstimate2()(dict_of_parameters), PiatetskyShapiroOptimisticEstimate2().compute(dict_of_parameters))
        self.assertEqual(NPV()(dict_of_parameters), NPV().compute(dict_of_parameters))
        self.assertEqual(AbsoluteWRAcc()(dict_of_parameters), AbsoluteWRAcc().compute(dict_of_parameters))
        self.assertEqual(AbsoluteWRAcc()(dict_of_parameters), abs(WRAcc().compute(dict_of_parameters)))
        self.assertEqual(Specificity()(dict_of_parameters), Specificity().compute(dict_of_parameters))
        self.assertEqual(IRR()(dict_of_parameters), IRR().compute(dict_of_parameters))
        self.assertEqual(F1Score()(dict_of_parameters), F1Score().compute(dict_of_parameters))
        self.assertEqual(Youden()(dict_of_parameters), Youden().compute(dict_of_parameters))
        # --------------------------------------------------
        self.assertRaises(TypeError, Support(), 3)
        self.assertRaises(TypeError, Support().compute, 3)
        self.assertRaises(TypeError, Coverage(), 3)
        self.assertRaises(TypeError, Coverage().compute, 3)
        self.assertRaises(TypeError, WRAcc(), 3)
        self.assertRaises(TypeError, WRAcc().compute, 3)
        self.assertRaises(TypeError, BinomialTest(), 3)
        self.assertRaises(TypeError, BinomialTest().compute, 3)
        self.assertRaises(TypeError, Qg(), 3)
        self.assertRaises(TypeError, Qg().compute, 3)
        self.assertRaises(TypeError, Sensitivity(), 3)
        self.assertRaises(TypeError, Sensitivity().compute, 3)
        self.assertRaises(TypeError, PPV(), 3)
        self.assertRaises(TypeError, PPV().compute, 3)
        self.assertRaises(TypeError, WRAccOptimisticEstimate1(), 3)
        self.assertRaises(TypeError, WRAccOptimisticEstimate1().compute, 3)
        self.assertRaises(TypeError, BinomialTestOptimisticEstimate1(), 3)
        self.assertRaises(TypeError, BinomialTestOptimisticEstimate1().compute, 3)
        self.assertRaises(TypeError, PiatetskyShapiro(), 3)
        self.assertRaises(TypeError, PiatetskyShapiro().compute, 3)
        self.assertRaises(TypeError, PiatetskyShapiroOptimisticEstimate1(), 3)
        self.assertRaises(TypeError, PiatetskyShapiroOptimisticEstimate1().compute, 3)
        self.assertRaises(TypeError, PiatetskyShapiroOptimisticEstimate2(), 3)
        self.assertRaises(TypeError, PiatetskyShapiroOptimisticEstimate2().compute, 3)
        self.assertRaises(TypeError, NPV(), 3)
        self.assertRaises(TypeError, NPV().compute, 3)
        self.assertRaises(TypeError, AbsoluteWRAcc(), 3)
        self.assertRaises(TypeError, AbsoluteWRAcc().compute, 3)
        self.assertRaises(TypeError, Specificity(), 3)
        self.assertRaises(TypeError, Specificity().compute, 3)
        self.assertRaises(TypeError, IRR(), 3)
        self.assertRaises(TypeError, IRR().compute, 3)
        self.assertRaises(TypeError, F1Score(), 3)
        self.assertRaises(TypeError, F1Score().compute, 3)
        self.assertRaises(TypeError, Youden(), 3)
        self.assertRaises(TypeError, Youden().compute, 3)
