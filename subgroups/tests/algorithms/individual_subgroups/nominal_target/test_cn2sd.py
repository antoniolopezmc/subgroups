
import pandas
from pandas import DataFrame
from subgroups.algorithms.algorithm import Algorithm
from subgroups.algorithms.individual_subgroups.nominal_target.cn2sd import CN2SD
from subgroups.quality_measures import WRAcc, Support
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.exceptions import EmptyDatasetError
from subgroups.core.pattern import Pattern
from subgroups.core.operator import Operator
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
import unittest as unittestt

class TestCN2SD(unittestt.TestCase):
        def test_SD_obtain_basic_metrics_method_1(self) -> None:
            # Dataset de ejemplo
            input_dataframe = pandas.DataFrame({
            "Age": [25, 35, 40, 50, 30],
            "Gender": ["M", "F", "M", "M", "F"],
            "Class": [0, 1, 1, 1, 0]
            })
            weights = [1,1, 1, 1, 1]            
            algCN2SD = CN2SD("aditive",1) # For this test, the parameters do not matter.
            subg1 = Subgroup(Pattern([Selector("Age", Operator.GREATER, 30) , Selector("Gender", Operator.EQUAL, "F")]), Selector("Class", Operator.EQUAL, 1))           
            print(subg1)
            basicMetrics1 = algCN2SD._obtain_basic_metrics(input_dataframe, weights,subg1)      
            result1 = WRAcc().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            assert(round(result1,2) == round(2/25,2))

        '''def test_SD_obtain_basic_metrics_method_2(self) -> None:
            input_dataframe = pandas.DataFrame({'attr1': [0.2, 0.6, 0.1, 0.8, 0.4, 0.7, 0.9, 0.3], 'attr2': [0.5, 0.9, 0.3, 0.2, 0.7, 0.1, 0.4, 0.8],'attr3': [0.8, 0.4, 0.5, 0.3, 0.6, 0.2, 0.7, 0.1],'attr4': [1, 1, 0, 0, 0, 0, 1, 1]})
            algCN2SD = CN2SD("aditive",1) 
            weights = [1,1,1,1,1,1,1,1]# For this test, the parameters do not matter.
            subg1 = Subgroup(Pattern([Selector("attr2", Operator.GREATER_OR_EQUAL, 0.5)]), Selector("attr2", Operator.GREATER_OR_EQUAL, 0.5))           
            basicMetrics1 = algCN2SD._obtain_basic_metrics(input_dataframe, weights,subg1)      
            result1 = WRAcc().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            assert(round(result1,2) == round(1/12,2))
'''