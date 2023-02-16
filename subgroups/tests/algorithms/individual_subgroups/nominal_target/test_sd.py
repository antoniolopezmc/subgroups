from os import remove
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

 # - TESTS OF METHOD '_obtain_basic_metrics'.
 # - For this kind of test, the algorithm parameters doesn´t matter
        def test_SD_obtain_basic_metrics_method_1(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1) # For this test, the parameters do not matter.
            subg1 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10)]), Selector("attr1", Operator.EQUAL, "v3"))
            basicMetrics1 = algSD._obtain_basic_metrics(input_dataframe, subg1)      
            print(basicMetrics1)
            result1 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            print(result1)
            assert(round(result1,2) == round(2/6,2))

        def test_SD_obtain_basic_metrics_method_2(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)     
            subg2 = Subgroup(Pattern([Selector("attr1", Operator.EQUAL, "v1"), Selector("attr2", Operator.GREATER, 1000)]), Selector("attr1", Operator.EQUAL, "v1"))
            basicMetrics2 = algSD._obtain_basic_metrics(input_dataframe, subg2)
            result2 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics2[0], QualityMeasure.FALSE_POSITIVES : basicMetrics2[1], QualityMeasure.TRUE_POPULATION : basicMetrics2[2],  QualityMeasure.FALSE_POPULATION : basicMetrics2[3]})
            assert(result2 == 0)
             
        def test_SD_obtain_basic_metrics_method_3(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)  
            subg3 = Subgroup(Pattern([Selector("attr5", Operator.EQUAL, "value25")]), Selector("attr2", Operator.LESS, 10))
            basicMetrics3 = algSD._obtain_basic_metrics(input_dataframe, subg3)
            result3 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics3[0], QualityMeasure.FALSE_POSITIVES : basicMetrics3[1], QualityMeasure.TRUE_POPULATION : basicMetrics3[2], QualityMeasure.FALSE_POPULATION : basicMetrics3[3]})
            assert(result3 == 0)
               
        def test_SD_obtain_basic_metrics_method_4(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)  
            subg4 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10)]), Selector("attr2", Operator.GREATER, 50))
            basicMetrics4 = algSD._obtain_basic_metrics(input_dataframe, subg4)
            result4 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics4[0], QualityMeasure.FALSE_POSITIVES : basicMetrics4[1], QualityMeasure.TRUE_POPULATION : basicMetrics4[2], QualityMeasure.FALSE_POPULATION : basicMetrics4[3]})
            assert(result4 == 0)

        def test_SD_obtain_basic_metrics_method_5(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)
            subg5 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 50)]), Selector("attr3", Operator.LESS, 100.0))
            basicMetrics5 = algSD._obtain_basic_metrics(input_dataframe, subg5)
            result5 = Support().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics5[0], QualityMeasure.FALSE_POSITIVES : basicMetrics5[1], QualityMeasure.TRUE_POPULATION : basicMetrics5[2], QualityMeasure.FALSE_POPULATION : basicMetrics5[3]})
            assert(round(result5,2) == round(5/6,2))
       
        def test_SD_obtain_basic_metrics_method_6(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)
            g_parameter = 27.17
            subg6 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10)]), Selector("attr1", Operator.EQUAL, "v3"))
            basicMetrics6 = algSD._obtain_basic_metrics(input_dataframe, subg6)
            result6 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics6[0], QualityMeasure.FALSE_POSITIVES : basicMetrics6[1], QualityMeasure.TRUE_POPULATION : basicMetrics6[2],QualityMeasure.FALSE_POPULATION : basicMetrics6[3],"g": g_parameter})
            assert(round(result6,2) == round(2/(2+g_parameter),2))
        
        def test_SD_obtain_basic_metrics_method_7(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)
            g_parameter = 27.17
            subg7 = Subgroup(Pattern([Selector("attr2", Operator.LESS, 10), Selector("attr1", Operator.EQUAL, "v3")]), Selector("attr5", Operator.EQUAL, "value25"))
            basicMetrics7 = algSD._obtain_basic_metrics(input_dataframe, subg7)
            result7 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics7[0],QualityMeasure.FALSE_POSITIVES : basicMetrics7[1], QualityMeasure.TRUE_POPULATION : basicMetrics7[2], QualityMeasure.FALSE_POPULATION : basicMetrics7[3],"g": g_parameter})
            assert(round(result7,2) == 0)

        def test_SD_obtain_basic_metrics_method_8(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)
            g_parameter = 27.17
            subg8 = Subgroup(Pattern([Selector("attr1", Operator.EQUAL, "v1"), Selector("attr2", Operator.GREATER, 1000)]), Selector("attr1", Operator.NOT_EQUAL, "v1"))
            basicMetrics8 = algSD._obtain_basic_metrics(input_dataframe, subg8)
            result8 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics8[0],QualityMeasure.FALSE_POSITIVES : basicMetrics8[1], QualityMeasure.TRUE_POPULATION : basicMetrics8[2],QualityMeasure.FALSE_POPULATION : basicMetrics8[3],"g": g_parameter})
            assert(round(result8,2) == 0)

        def test_SD_obtain_basic_metrics_method_9(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2]})
            algSD = SD(0, 0, 1)
            g_parameter = 27.17
            subg9 = Subgroup(Pattern([Selector("attr1", Operator.EQUAL, "v1"), Selector("attr2", Operator.LESS, 1000), Selector("attr1", Operator.EQUAL, "v1")]), Selector("attr3", Operator.LESS, 0.0))
            basicMetrics9 = algSD._obtain_basic_metrics(input_dataframe, subg9)
            result9 = Qg().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics9[0], QualityMeasure.FALSE_POSITIVES : basicMetrics9[1], QualityMeasure.TRUE_POPULATION : basicMetrics9[2],QualityMeasure.FALSE_POPULATION : basicMetrics9[3],"g": g_parameter})
            assert(round(result9,2) == round(1/(0+g_parameter),2))


        def test_SD_fit_method_1(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "A", "B", "B", "B", "A"]})
            target = ("class", "B")
            sd = SD(2, 0.35, 5, True,"./results.txt")
            result = sd.fit(input_dataframe, target)
            self.assertEqual(sd._get_selected_subgroups(), 7)
            self.assertEqual(sd._get_unselected_subgroups(), 10)
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            print(list_of_written_results)
            list_of_subgroups = [Subgroup.generate_from_str(elem) for elem in list_of_written_results]
            print(list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v3', attr2 != '2'], Target: class = 'B', 1.5"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v3', attr3 != '-25.2'], Target: class = 'B', 1.5"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v3', attr2 != '2', attr2 != '3'], Target: class = 'B', 1.5"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v3', attr2 != '2', attr2 != '4'], Target: class = 'B', 1.5"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v3', attr2 != '2', attr3 != '2.23'], Target: class = 'B', 1.5"), list_of_subgroups)
            file_to_read.close()
            remove("./results.txt")

        def test_SD_fit_method_2(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "C", "B", "C", "B", "A"]})
            target = ("class", "C")
            sd = SD(5, 0, 7, True,"./results.txt")
            result = sd.fit(input_dataframe, target)
            self.assertEqual(sd._get_selected_subgroups(), 18)
            self.assertEqual(sd._get_unselected_subgroups(), 0)
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            print(list_of_written_results)
            list_of_subgroups = [Subgroup.generate_from_str(elem) for elem in list_of_written_results]
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr1 != 'v2', attr2 != '2', attr2 != '3'], Target: class = 'C', 0.4"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr1 != 'v2', attr2 != '3', attr3 != '-25.2'], Target: class = 'C', 0.4"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr1 != 'v2', attr2 != '2', attr3 != '2.23'], Target: class = 'C', 0.4"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr1 != 'v2', attr3 != '-25.2', attr3 != '2.23'], Target: class = 'C', 0.4"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr2 != '2', attr2 != '3', attr2 != '63'], Target: class = 'C', 0.4"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr2 != '3', attr2 != '63', attr3 != '-25.2'], Target: class = 'C', 0.4"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr1 != 'v1', attr2 != '2', attr2 != '3', attr3 != '152.23'], Target: class = 'C', 0.4"), list_of_subgroups)
            file_to_read.close()
            remove("./results.txt")
        
        def test_SD_fit_method_3(self) -> None:
                   # TESTS OF ALGORITHM SD.
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': [3, 4, 45, -12, 63, 2], 'attr3' : [2.23, 5.98, -4.268, 12.576, 152.23, -25.2], "class" : ["A", "A", "B", "C", "B", "A"]})
            sd = SD(2.5, 0.4, 6,True,"./results.txt")
            target = ("class", "A")
            result = sd.fit(input_dataframe, target)
            self.assertEqual(sd._get_selected_subgroups(),19)
            self.assertEqual(sd._get_unselected_subgroups(),28)
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            list_of_subgroups = [Subgroup.generate_from_str(elem) for elem in list_of_written_results]
            self.assertIn(Subgroup.generate_from_str("Description: [attr2 > -4.5, attr2 <= 24.0], Target: class = 'A', 1.2"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr2 != -12, attr2 <= 24.0], Target: class = 'A', 1.2"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr2 > -4.0, attr2 <= 24.0], Target: class = 'A', 1.2"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr2 > -5.0, attr2 <= 24.0], Target: class = 'A', 1.2"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr2 <= 24.0, attr3 <= 7.4030000000000005], Target: class = 'A', 1.2"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [attr2 <= 24.0, attr3 <= 9.278], Target: class = 'A', 1.2"), list_of_subgroups)
            file_to_read.close()
            remove("./results.txt")
                
        def test_SD_fit_method_4(self) -> None:
            dataset = read_csv("../../../../datasets/csv/titanic.csv")
            dataset = dataset[["Survived","Pclass","Sex"]]
            sd = SD(2, 0.35, 5,True,"./results.txt")
            result = sd.fit(dataset, ("Survived", "No"))
            self.assertEqual(sd._get_selected_subgroups(),10)
            self.assertEqual(sd._get_unselected_subgroups(),10)
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            list_of_subgroups = [Subgroup.generate_from_str(elem) for elem in list_of_written_results]
            self.assertIn(Subgroup.generate_from_str("Description: [Pclass != 1, Sex = 'male'], Target: Survived = 'No', 5.863636363636363"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [Pclass > 1.0, Sex = 'male'], Target: Survived = 'No', 5.863636363636363"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [Pclass > 1.5, Sex = 'male'], Target: Survived = 'No', 5.863636363636363"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [Pclass != 1, Sex != 'female'], Target: Survived = 'No', 5.863636363636363"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [Pclass > 1.0, Sex != 'female'], Target: Survived = 'No', 5.863636363636363"), list_of_subgroups)
            file_to_read.close()
            remove("./results.txt")
           
        def test_SD_fit_method_5(self) -> None:
            dataset = read_csv("../../../../datasets/csv/titanic.csv")
            dataset = dataset[["Survived","Sex"]]
            target = ("Survived", "No")
            sd = SD(2, 0.35, 5,True,"./results.txt")
            result = sd.fit(dataset, target)
            self.assertEqual(sd._get_selected_subgroups(),2)
            self.assertEqual(sd._get_unselected_subgroups(),2)
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            list_of_subgroups = [Subgroup.generate_from_str(elem) for elem in list_of_written_results]
            self.assertIn(Subgroup.generate_from_str("Description: [Sex = 'male'], Target: Survived = 'No', 4.18018018018018"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [Sex != 'female'], Target: Survived = 'No', 4.18018018018018"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [Sex = 'male', Sex != 'female'], Target: Survived = 'No', 4.18018018018018"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [], Target: Survived = 'No', 0"), list_of_subgroups)
            self.assertIn(Subgroup.generate_from_str("Description: [], Target: Survived = 'No', 0"), list_of_subgroups)
            file_to_read.close()
            remove("./results.txt")    


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)