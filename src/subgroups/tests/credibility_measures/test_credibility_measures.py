# -*- coding: utf-8 -*-

# Contributors:
#    Francisco Mora-Caselles: <franciscojose.morac@um.es>

"""Tests of the functionality contained in the folder 'credibility_measures'.
"""

from subgroups.credibility_measures.selector_contribution import SelectorContribution
from subgroups.credibility_measures.odds_ratio_glm import OddsRatioGLM
from subgroups.credibility_measures.p_value_glm import PValueGLM
from subgroups.credibility_measures.odds_ratio_stat import OddsRatioStatistic
from subgroups.credibility_measures.p_value_independence import PValueIndependence
from subgroups.exceptions import ParameterNotFoundError
from subgroups.core.selector import Selector
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from pandas import Series
import statsmodels.api as sm
import unittest

class TestCredibilityMeasures(unittest.TestCase):
    def test_credibility_measures_general(self) -> None:
        selector_contribution = SelectorContribution()
        odds_ratio_glm = OddsRatioGLM()
        p_value_glm = PValueGLM()
        odds_ratio_stat = OddsRatioStatistic()
        p_value_independence = PValueIndependence()
        # --------------------------------------------------
        self.assertIs(type(selector_contribution), SelectorContribution)
        self.assertIs(type(odds_ratio_glm), OddsRatioGLM)
        self.assertIs(type(p_value_glm), PValueGLM)
        self.assertIs(type(odds_ratio_stat), OddsRatioStatistic)
        self.assertIs(type(p_value_independence), PValueIndependence)
        # --------------------------------------------------
        self.assertEqual(id(selector_contribution), id(SelectorContribution()))
        self.assertEqual(id(odds_ratio_glm), id(OddsRatioGLM()))
        self.assertEqual(id(p_value_glm), id(PValueGLM()))
        self.assertEqual(id(odds_ratio_stat), id(OddsRatioStatistic()))
        self.assertEqual(id(p_value_independence), id(PValueIndependence()))
        # --------------------------------------------------
        self.assertIs(selector_contribution, SelectorContribution())
        self.assertIs(odds_ratio_glm, OddsRatioGLM())
        self.assertIs(p_value_glm, PValueGLM())
        self.assertIs(odds_ratio_stat, OddsRatioStatistic())
        self.assertIs(p_value_independence, PValueIndependence())
        # --------------------------------------------------
        self.assertEqual(selector_contribution.get_name(), "SelectorContribution")
        self.assertEqual(odds_ratio_glm.get_name(), "OddsRatioGLM")
        self.assertEqual(p_value_glm.get_name(), "PValueGLM")
        self.assertEqual(odds_ratio_stat.get_name(), "OddsRatioStatistic")
        self.assertEqual(p_value_independence.get_name(), "PValueIndependence")

    def test_selector_contribution(self) -> None:
        selector_contribution = SelectorContribution()
        with self.assertRaises(TypeError):
            selector_contribution.compute(1)
        # Either 'odds_ratios' or 'selector_appearances' and 'target_appearance' must be included.
        with self.assertRaises(ParameterNotFoundError):
            selector_contribution.compute({})
        # Target appearance is not included.
        with self.assertRaises(ParameterNotFoundError):
            selector_contribution.compute({"selector_appearances": 1})
        # Odds ratio definition is not included.
        with self.assertRaises(ParameterNotFoundError):
            selector_contribution.compute({"selector_appearances": 1, "target_appearance": 1})
        # Pattern is not included.
        with self.assertRaises(ParameterNotFoundError):
            selector_contribution.compute({"selector_appearances": 1, "target_appearance": 1, "odds_ratio_definition": "glm"})
        # Odds ratio definition is not 'glm' or 'statistic'.
        with self.assertRaises(ValueError):
            selector_contribution.compute({"selector_appearances": 1, "target_appearance": 1, "odds_ratio_definition": "other", "pattern": 1})
        # Pattern is empty.
        self.assertEqual(selector_contribution.compute({"selector_appearances": 1, "target_appearance": 1, "odds_ratio_definition": "glm", "pattern": Pattern([])}), (0, 0))
        # Pattern is a single selector.
        sel = Selector("a", Operator.EQUAL, 1)
        self.assertEqual(selector_contribution.compute({"selector_appearances": 1, "target_appearance": 1, "odds_ratio_definition": "glm", "pattern": Pattern([sel])}), (1, 1))
        # Pattern is not empty and is not a single selector.
        sel1 = Selector("a", Operator.EQUAL, 1)
        sel2 = Selector("b", Operator.EQUAL, 2)
        odds_ratios = {str(Pattern([sel1])): 1, str(Pattern([sel2])): 1, str(Pattern([sel1, sel2])): 2}
        self.assertEqual(selector_contribution.compute({"selector_appearances": 1, "target_appearance": 1, "odds_ratio_definition": "glm", "pattern": Pattern([sel1, sel2]), "odds_ratios": odds_ratios}), (2, 1))

    def test_odds_ratio_glm(self) -> None:
        odds_ratio_glm = OddsRatioGLM()
        with self.assertRaises(TypeError):
            odds_ratio_glm.compute(1)
        # Either 'appearance' and 'target_appearance' or 'glm' must be included.
        with self.assertRaises(ParameterNotFoundError):
            odds_ratio_glm.compute({})
        # appearance is included but target_appearance is not.
        with self.assertRaises(ParameterNotFoundError):
            odds_ratio_glm.compute({"appearance": 1})
        pattern = Series([0,0,1,1,0,1])
        target = Series([1,0,1,1,1,0])
        glm = sm.GLM(target, pattern, family=sm.families.Binomial()).fit()
        self.assertAlmostEqual(odds_ratio_glm.compute({"appearance": pattern, "target_appearance": target}), 2.0)
        self.assertAlmostEqual(odds_ratio_glm.compute({"glm": glm}), 2.0)
    
    def test_p_value_glm(self) -> None:
        p_value_glm = PValueGLM()
        with self.assertRaises(TypeError):
            p_value_glm.compute(1)
        # Either 'appearance' and 'target_appearance' or 'glm' must be included.
        with self.assertRaises(ParameterNotFoundError):
            p_value_glm.compute({})
        # appearance is included but target_appearance is not.
        with self.assertRaises(ParameterNotFoundError):
            p_value_glm.compute({"appearance": 1})
        pattern = Series([0,0,1,1,0,1])
        target = Series([1,0,1,1,1,0])
        glm = sm.GLM(target, pattern, family=sm.families.Binomial()).fit()
        self.assertEqual(round(p_value_glm.compute({"appearance": pattern, "target_appearance": target}),2), 0.57)
        self.assertEqual(round(p_value_glm.compute({"glm": glm}),2), 0.57)

    def test_odds_ratio_stat(self) -> None:
        odds_ratio_stat = OddsRatioStatistic()
        with self.assertRaises(TypeError):
            odds_ratio_stat.compute(1)
        # Either 'appearance' and 'target_appearance' or 'tp', 'fp', 'TP' and 'FP' must be included.
        with self.assertRaises(ParameterNotFoundError):
            odds_ratio_stat.compute({})
        # appearance is included but target_appearance is not.
        with self.assertRaises(ParameterNotFoundError):
            odds_ratio_stat.compute({"appearance": 1})
        # tp is included but fp, TP, and FP are not.
        with self.assertRaises(ParameterNotFoundError):
            odds_ratio_stat.compute({"tp": 1})
        # tp and fp are included but TP and FP are not.
        with self.assertRaises(ParameterNotFoundError):
            odds_ratio_stat.compute({"tp": 1, "fp": 1})
        TP = 4
        FP = 4
        self.assertEqual(odds_ratio_stat.compute({"tp": 4, "fp": 4, "TP": TP, "FP": FP}), 0)
        self.assertEqual(odds_ratio_stat.compute({"tp": 4, "fp": 0, "TP": TP, "FP": FP}), float('inf'))
        self.assertEqual(odds_ratio_stat.compute({"tp": 0, "fp": 4, "TP": TP, "FP": FP}), 0)
        self.assertEqual(odds_ratio_stat.compute({"tp": 0, "fp": 0, "TP": TP, "FP": FP}), 0)
        self.assertEqual(odds_ratio_stat.compute({"tp": 3, "fp": 0, "TP": TP, "FP": FP}), float('inf'))
        self.assertEqual(odds_ratio_stat.compute({"tp": 2, "fp": 1, "TP": TP, "FP": FP}), 3)

    def test_p_value_independence(self) -> None:
        p_value_independence = PValueIndependence()
        with self.assertRaises(TypeError):
            p_value_independence.compute(1)
        #'tp', 'fp', 'TP' and 'FP' must be included.
        with self.assertRaises(ParameterNotFoundError):
            p_value_independence.compute({})
        # tp is included but fp, TP, and FP are not.
        with self.assertRaises(ParameterNotFoundError):
            p_value_independence.compute({"tp": 1})
        # tp and fp are included but TP and FP are not.
        with self.assertRaises(ParameterNotFoundError):
            p_value_independence.compute({"tp": 1, "fp": 1})
        TP = 4
        FP = 4
        self.assertEqual(p_value_independence.compute({"tp": 4, "fp": 4, "TP": TP, "FP": FP}), 1)
        self.assertEqual(p_value_independence.compute({"tp": 0, "fp": 0, "TP": TP, "FP": FP}), 1)
        self.assertEqual(round(p_value_independence.compute({"tp": 2, "fp": 1, "TP": TP, "FP": FP}),2), 0.56)