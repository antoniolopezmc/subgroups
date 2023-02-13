import unittest
from pandas import DataFrame, read_csv
#import sys
#sys.path.insert(1,"C:\\Users\\PC\\Documents\\GitHub\\subgroups")
from subgroups.algorithms.algorithm import Algorithm
from subgroups.core.operator import Operator
from subgroups.core.pattern import Pattern
from subgroups.core.selector import Selector
from subgroups.core.subgroup import Subgroup
from subgroups.quality_measures.qg import Qg
from subgroups.quality_measures.quality_measure import QualityMeasure
from subgroups.algorithms.individual_subgroups.nominal_target.sd_nominal import SD
from subgroups.exceptions import AbstractClassError
from subgroups.quality_measures.support import Support
class TestSD(unittest.TestCase):





    def test_SD(self):
        # - TESTS OF METHOD '_obtain_basic_metrics'.
        print("#######################SD########################")
        input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
        g_parameter = 27.12
        algSD = SD(0, 0, 1,Qg(),0) # For this test, the parameters do not matter.
        subg1 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10)]), Selector("attr1", Operator.EQUAL, "v3"))
        print(subg1.description)
        print(subg1.target)
        basicMetrics1 = algSD._obtain_basic_metrics(input_dataframe, subg1)      
        print(basicMetrics1)
        result1 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
        print(result1)
        assert(round(result1,2) == round(2/6,2))
        subg2 = Subgroup(Pattern([Selector("attr1", Operator.EQUAL, "v1"), Selector("attr2", Operator.GREATER, 1000)]), Selector("attr1", Operator.EQUAL, "v1"))
        basicMetrics2 = algSD._obtain_basic_metrics(input_dataframe, subg2)
        result2 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics2[0], QualityMeasure.FALSE_POSITIVES : basicMetrics2[1], QualityMeasure.TRUE_POPULATION : basicMetrics2[2],  QualityMeasure.FALSE_POPULATION : basicMetrics2[3]})
        assert(result2 == 0)
        subg3 = Subgroup(Pattern([Selector("attr5", Operator.EQUAL, "value25")]), Selector("attr2", Operator.LESS, 10))
        basicMetrics3 = algSD._obtain_basic_metrics(input_dataframe, subg3)
        result3 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics3[0], QualityMeasure.FALSE_POSITIVES : basicMetrics3[1], QualityMeasure.TRUE_POPULATION : basicMetrics3[2], QualityMeasure.FALSE_POPULATION : basicMetrics3[3]})
        assert(result3 == 0)
        subg4 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10)]), Selector("attr2", Operator.GREATER, 50))
        basicMetrics4 = algSD._obtain_basic_metrics(input_dataframe, subg4)
        result4 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics4[0], QualityMeasure.FALSE_POSITIVES : basicMetrics4[1], QualityMeasure.TRUE_POPULATION : basicMetrics4[2], QualityMeasure.FALSE_POPULATION : basicMetrics4[3]})
        assert(result4 == 0)
        subg5 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 50)]), Selector("attr3", Operator.LESS, 100.0))
        basicMetrics5 = algSD._obtain_basic_metrics(input_dataframe, subg5)
        result5 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics5[0], QualityMeasure.FALSE_POSITIVES : basicMetrics5[1], QualityMeasure.TRUE_POPULATION : basicMetrics5[2], QualityMeasure.FALSE_POPULATION : basicMetrics5[3]})
        assert(round(result5,2) == round(5/6,2))
        subg6 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10)]), Selector("attr1", Operator.EQUAL, "v3"))
        basicMetrics6 = algSD._obtain_basic_metrics(input_dataframe, subg6)
        result6 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics6[0], QualityMeasure.FALSE_POSITIVES : basicMetrics6[1], QualityMeasure.TRUE_POPULATION : basicMetrics6[2],QualityMeasure.FALSE_POPULATION : basicMetrics5[3],"g": g_parameter})
        assert(round(result6,2) == round(2/(2+g_parameter),2))
        subg7 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10), Selector("attr1", Operator.EQUAL, "v3")]), Selector("attr5", Operator.EQUAL, "value25"))
        basicMetrics7 = algSD._obtain_basic_metrics(input_dataframe, subg7)
        result7 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics7[0],QualityMeasure.FALSE_POSITIVES : basicMetrics7[1], QualityMeasure.TRUE_POPULATION : basicMetrics7[2], QualityMeasure.FALSE_POPULATION : basicMetrics7[3],"g": g_parameter})
        assert(round(result7,2) == 0)
        subg8 = Subgroup(Pattern([Selector("attr1", Operator.EQUAL, "v1"), Selector("attr2", Operator.GREATER, 1000)]), Selector("attr1", Operator.NOT_EQUAL, "v1"))
        basicMetrics8 = algSD._obtain_basic_metrics(input_dataframe, subg8)
        result8 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics8[0],QualityMeasure.FALSE_POSITIVES : basicMetrics8[1], QualityMeasure.TRUE_POPULATION : basicMetrics8[2],QualityMeasure.FALSE_POPULATION : basicMetrics8[3],"g": g_parameter})
        assert(round(result8,2) == 0)
        subg9 = Subgroup(Pattern([Selector("attr1", Operator.EQUAL, "v1"), Selector("attr2", Operator.LESS, 1000), Selector("attr1", Operator.EQUAL, "v1")]), Selector("attr3", Operator.LESS, 0.0))
        basicMetrics9 = algSD._obtain_basic_metrics(input_dataframe, subg9)
        result9 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics9[0], QualityMeasure.FALSE_POSITIVES : basicMetrics9[1], QualityMeasure.TRUE_POPULATION : basicMetrics9[2],QualityMeasure.FALSE_POPULATION : basicMetrics9[3],"g": g_parameter})
        assert(round(result9,2) == round(1/(0+g_parameter),2))
        
        # TESTS OF ALGORITHM SD.
        input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "A", "B", "B", "B", "A"]})
        input_dataframe_2 = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "C", "B", "C", "B", "A"]})
        input_dataframe_3 = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2], "class" : ["A", "A", "B", "C", "B", "A"]})
        algSD_1 = SD(2, 0.35, 5,Support(),0)
        set_l_1 = algSD_1._generate_set_l(input_dataframe, ("class", "B"))
        result_1 = algSD_1.fit(input_dataframe, ("class", "B"))
        print("** SET L 1 **")
        for i in set_l_1:
            print(i)
        print("** BEAM RESULT 1 **")
        for [a,b] in result_1:
            print(str(a) + ", " + str(b))
        algSD_2 = SD(5, 0, 7,Support(),0)
        set_l_2 = algSD_2._generate_set_l(input_dataframe_2, ("class", "C"))
        result_2 = algSD_2.fit(input_dataframe_2, ("class", "C"))
        print("** SET L 2 **")
        for i in set_l_2:
            print(i)
        print("** BEAM RESULT 2 **")
        for [a,b] in result_2:
            print(str(a) + ", " + str(b))
        algSD_3 = SD(2.5, 0.4, 6,Support(),0)
        set_l_3 = algSD_3._generate_set_l(input_dataframe_3, ("class", "A"))
        result_3 = algSD_3.fit(input_dataframe_3, ("class", "A"))
        print("** SET L 3 **")
        for i in set_l_3:
            print(i)
        print("** BEAM RESULT 3 **")
        for [a,b] in result_3:
            print(str(a) + ", " + str(b))
        print("#######################")
        titanic = read_csv("C:/Users/PC/Desktop/CloudStation/Cosas personales/Beca/TFS/TFG-2020-EnriqueValero-AlgoritmosSubgroup/subgpylib/datasets/titanic_sg.csv")
        titanic = titanic[["Survived","Pclass","Sex"]]
        algSD_4 = SD(2, 0.35, 5,Support(),0)
        set_l_4 = algSD_4._generate_set_l(titanic, ("Survived", "No"))
        result_4 = algSD_4.fit(titanic, ("Survived", "No"))
        print("** SET L 4 **")
        for i in set_l_4:
            print(i)
        print("** BEAM RESULT 4 **")
        for [a,b] in result_4:
            print(str(a) + ", " + str(b))
        print("#######################")
        titanic = read_csv("C:/Users/PC/Desktop/CloudStation/Cosas personales/Beca/TFS/TFG-2020-EnriqueValero-AlgoritmosSubgroup/subgpylib/datasets/titanic_sg.csv")
        titanic = titanic[["Survived","Sex"]]
        algSD_5 = SD(2, 0.35, 5,Support(),0)
        set_l_5 = algSD_5._generate_set_l(titanic, ("Survived", "No"))
        result_5 = algSD_5.fit(titanic, ("Survived", "No"))
        print("** SET L 4 **")
        for i in set_l_5:
            print(i)
        print("** BEAM RESULT 4 **")
        for [a,b] in result_5:
            print(str(a) + ", " + str(b))
        print("#######################")
        print("* Set L of titanic. Sort by value.")
        algSD_4._sort_set_l(set_l_4, criterion = 'byValue')
        for i in set_l_4:
            print(i)
        print("* Set L of titanic. Sort by attribute.")
        algSD_4._sort_set_l(set_l_4, criterion = 'byAttribute')
        for i in set_l_4:
            print(i)
        print("* Set L of titanic. Sort by operator.")
        algSD_4._sort_set_l(set_l_4, criterion = 'byOperator')
        for i in set_l_4:
            print(i)
        print("* Set L of titanic. Sort by complete selector.")
        algSD_4._sort_set_l(set_l_4)
        for i in set_l_4:
            print(i)
        print("#######################")
        titanic = read_csv("C:/Users/PC/Desktop/CloudStation/Cosas personales/Beca/TFS/TFG-2020-EnriqueValero-AlgoritmosSubgroup/subgpylib/datasets/titanic_sg.csv")
        titanic = titanic[["Survived","Pclass","Sex"]]
        algSD_4 = SD(2, 0.35, 5,Support(),0)
        set_l_4 = algSD_4._generate_set_l(titanic, ("Survived", "No"))
        set_l_4 = algSD_4._sort_set_l(set_l_4, criterion = 'byOperator')
        result_4 = algSD_4.fit(titanic, ("Survived", "No"))
        print("** SET L 4 **")
        for i in set_l_4:
            print(i)
        print("** BEAM RESULT 4 **")
        for [a,b] in result_4:
            print(str(a) + ", " + str(b))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)