
from os import remove
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
        

    '''        
        def test_CN2SD_obtain_basic_metrics_method_1(self) -> None:
            # Dataset de ejemplo
            input_dataframe = pandas.DataFrame({
            "Age": [25, 35, 40, 50, 30],
            "Gender": ["M", "F", "M", "M", "F"],
            "Class": [0, 1, 1, 1, 0]
            })
            weights = [1,1,1,1,1]            
            algCN2SD = CN2SD("aditive",1) # For this test, the parameters do not matter.
            subg1 = Subgroup(Pattern([Selector("Age", Operator.GREATER, 30) , Selector("Gender", Operator.EQUAL, "F")]), Selector("Class", Operator.EQUAL, 1))           
            print(subg1)
            basicMetrics1 = algCN2SD._obtain_basic_metrics(input_dataframe, weights,subg1)      
            result1 = WRAcc().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            assert(round(result1,2) == round(2/25,2))

        def test_CN2SD_obtain_basic_metrics_method_2(self) -> None:
            input_dataframe = pandas.DataFrame({
            "Age": [25, 35, 40, 50, 30],
            "Gender": ["M", "F", "M", "M", "F"],
            "Class": [0, 1, 1, 1, 0]
            })
            weights = [1,1, 1, 1, 1]           
            algCN2SD = CN2SD("aditive",1) 
            subg1 = Subgroup(Pattern([Selector("Age", Operator.GREATER_OR_EQUAL, 25)]), Selector("Class", Operator.EQUAL, 1))           
            basicMetrics1 = algCN2SD._obtain_basic_metrics(input_dataframe, weights,subg1)      
            print(basicMetrics1)
            result1 = WRAcc().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            assert(round(result1,2) == round(0.0))

        def test_CN2SD_obtain_basic_metrics_method_3(self) -> None:
            input_dataframe = pandas.DataFrame({
            "Age": [25, 35, 40, 50, 30],
            "Gender": ["M", "F", "M", "M", "F"],
            "Class": [0, 1, 1, 1, 0]
            })
            weights = [1,1, 1, 1, 1]           
            algCN2SD = CN2SD("aditive",1) 
            subg1 = Subgroup(Pattern([Selector("Age", Operator.GREATER_OR_EQUAL, 25), Selector("Gender", Operator.EQUAL, "M")] ), Selector("Class", Operator.EQUAL, 0))           
            basicMetrics1 = algCN2SD._obtain_basic_metrics(input_dataframe, weights,subg1)      
            print(basicMetrics1)
            result1 = WRAcc().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            assert(round(result1,2) == round(-4/100,2))

        def test_CN2SD_obtain_basic_metrics_method_4(self) -> None:
            input_dataframe = pandas.DataFrame({
            "Age": [25, 35, 40, 50, 30],
            "Gender": ["M", "F", "M", "M", "F"],
            "Class": [0, 1, 1, 1, 0]
            })
            weights = [1,1, 1, 1, 1]           
            algCN2SD = CN2SD("aditive",1) 
            subg1 = Subgroup(Pattern([Selector("Age", Operator.LESS, 40), Selector("Age", Operator.GREATER, 30)] ), Selector("Gender", Operator.EQUAL, "F"))           
            basicMetrics1 = algCN2SD._obtain_basic_metrics(input_dataframe, weights,subg1)      
            print(basicMetrics1)
            result1 = WRAcc().compute({QualityMeasure.TRUE_POSITIVES : basicMetrics1[0], QualityMeasure.FALSE_POSITIVES : basicMetrics1[1], QualityMeasure.TRUE_POPULATION : basicMetrics1[2],  QualityMeasure.FALSE_POPULATION : basicMetrics1[3]})
            assert(round(result1,2) == round(12/100,2))
   
        def test_CN2SD_fit_method_1(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "A", "B", "B", "B", "A"]})
            target = ("class")
            cn2sd = CN2SD(beam_width = 3, weighting_scheme = 'multiplicative', gamma = 0, max_rule_length = 3,write_results_in_file=True,file_path="./results.txt")
            result = cn2sd.fit(input_dataframe, target)
            #self.assertEqual(cn2sd._get_selected_subgroups(), 7)
            #self.assertEqual(cn2sd._get_unselected_subgroups(), 10)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [attr1 = 'v3'], Target: class = 'A', 0.17", list_of_written_results)
            self.assertIn("Description: [attr2 = '2'], Target: class = 'A', 0.19", list_of_written_results)
            self.assertIn("Description: [attr1 != 'v3', attr2 != '2'], Target: class = 'B', 0.25", list_of_written_results)
            file_to_read.close()
            remove("./results.txt")
            
        def test_CN2SD_fit_method_2(self) -> None:
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "A", "B", "B", "B", "A"]})
            target = ("class")
            cn2sd = CN2SD(beam_width = 5, weighting_scheme = 'aditive', max_rule_length = 3,write_results_in_file=True,file_path="./results.txt")
            result = cn2sd.fit(input_dataframe, target)
            #self.assertEqual(cn2sd._get_selected_subgroups(), 7)
            #self.assertEqual(cn2sd._get_unselected_subgroups(), 10)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [attr1 = 'v3'], Target: class = 'A', 0.17", list_of_written_results)
            self.assertIn("Description: [attr1 != 'v1', attr1 != 'v2', attr2 != '-12'], Target: class = 'A', 0.24", list_of_written_results)
            self.assertIn("Description: [attr2 = '2'], Target: class = 'A', 0.04", list_of_written_results)
            self.assertIn("Description: [attr1 != 'v3', attr2 != '2'], Target: class = 'B', 0.25", list_of_written_results)
            file_to_read.close()
            remove("./results.txt")

        def test_CN2SD_fit_method_3(self) -> None: 
            input_dataframe = DataFrame({'attr1': ["v3", "v3", "v1", "v4", "v2", "v4"], 'attr2': ["3", "4", "45", "-12", "63", "2"], 'attr3' : ["2.23", "5.98", "-4.268", "12.576", "152.23", "-25.2"], "class" : ["A", "A", "B", "B", "B", "A"]})
            target = ("class")
            cn2sd = CN2SD(beam_width = 10, weighting_scheme = 'multiplicative', gamma = 0.35, max_rule_length = 5,write_results_in_file=True,file_path="./results.txt")
            result = cn2sd.fit(input_dataframe, target)
            #self.assertEqual(cn2sd._get_selected_subgroups(), 7)
            #self.assertEqual(cn2sd._get_unselected_subgroups(), 10)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [attr1 != 'v1', attr1 != 'v2', attr2 != '-12'], Target: class = 'A', 0.25", list_of_written_results)
            self.assertIn("Description: [attr1 != 'v3', attr2 != '2'], Target: class = 'B', 0.25", list_of_written_results)
            file_to_read.close()
            remove("./results.txt")      

        def test_CN2SD_fit_method_4(self) -> None:
            input_dataframe = pandas.read_csv("../../../../datasets/csv/shop.csv") 
            target = ("diaper")
            cn2sd = CN2SD(beam_width = 3, weighting_scheme = 'multiplicative', gamma = 0,write_results_in_file=True,file_path="./results.txt")
            binary_attributes = ["bread", "milk", "coke","beer"] 
            result = cn2sd.fit(input_dataframe, target,binary_attributes)
            #self.assertEqual(cn2sd._get_selected_subgroups(), 7)
            #self.assertEqual(cn2sd._get_unselected_subgroups(), 10)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [beer = 'no', coke = 'no'], Target: diaper = 'no', 0.12", list_of_written_results)
            self.assertIn("Description: [beer = 'yes'], Target: diaper = 'yes', 0.08", list_of_written_results)
            self.assertIn("Description: [coke = 'yes'], Target: diaper = 'yes', 0.22", list_of_written_results)
            file_to_read.close()
            remove("./results.txt")      
        
        def test_CN2SD_fit_method_5(self) -> None:
            input_dataframe = pandas.read_csv("../../../../datasets/csv/shop.csv") 
            target = ("diaper")
            cn2sd = CN2SD(beam_width = 3, weighting_scheme = 'multiplicative', gamma = 0.5,write_results_in_file=True,file_path="./results.txt")
            binary_attributes = ["bread", "milk", "coke","beer"] 
            result = cn2sd.fit(input_dataframe, target,binary_attributes)
            #self.assertEqual(cn2sd._get_selected_subgroups(), 7)
            #self.assertEqual(cn2sd._get_unselected_subgroups(), 10)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [beer = 'no', coke = 'no'], Target: diaper = 'no', 0.12", list_of_written_results)
            self.assertIn("Description: [beer = 'yes'], Target: diaper = 'yes', 0.08", list_of_written_results)
            self.assertIn("Description: [coke = 'yes'], Target: diaper = 'yes', 0.1", list_of_written_results)
            file_to_read.close()
            remove("./results.txt") 

        def test_CN2SD_fit_method_6(self) -> None : 
            input_dataframe = pandas.read_csv("../../../../datasets/csv/shop.csv") 
            target = ("diaper")
            cn2sd = CN2SD(beam_width = 3, weighting_scheme = 'aditive',write_results_in_file=True,file_path="./results.txt")
            binary_attributes = ["bread", "milk", "coke","beer"] 
            result = cn2sd.fit(input_dataframe, target,binary_attributes)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [beer = 'no', coke = 'no'], Target: diaper = 'no', 0.12", list_of_written_results)
            self.assertIn("Description: [beer = 'yes'], Target: diaper = 'yes', 0.08", list_of_written_results)
            self.assertIn("Description: [coke = 'yes'], Target: diaper = 'yes', 0.1", list_of_written_results)
            file_to_read.close()
            remove("./results.txt")

     
        def test_CN2SD_fit_method_7(self) -> None : 
            input_dataframe = pandas.read_csv("../../../../datasets/csv/lenses.csv") 
            target = ("class")
            cn2sd = CN2SD(beam_width = 3, max_rule_length= 3, weighting_scheme = 'multiplicative',gamma = 0, write_results_in_file=True,file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = cn2sd.fit(input_dataframe, target,binary_attributes)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            print(list_of_written_results)
            self.assertIn("Description: [tear-production-rate = 'REDUCED'], Target: class = 'NO-CONTACT-LENSES', 0.19", list_of_written_results)
            self.assertIn("Description: [age != 'YOUNG', astigmatic = 'YES', spectacle-prescription = 'HYPERMETROPE'], Target: class = 'NO-CONTACT-LENSES', 0.12", list_of_written_results)
            self.assertIn("Description: [age = 'PRESBYOPIC', astigmatic = 'NO', spectacle-prescription = 'MYOPE'], Target: class = 'NO-CONTACT-LENSES', 0.09", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.16", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'YES', tear-production-rate = 'NORMAL'], Target: class = 'HARD-CONTACT-LENSES', 0.12", list_of_written_results)
            file_to_read.close()
            remove("./results.txt")
        
        

        def test_CN2SD_fit_method_8(self) -> None : 
            input_dataframe = pandas.read_csv("../../../../datasets/csv/lenses.csv") 
            target = ("class")
            cn2sd = CN2SD(beam_width = 3, weighting_scheme = 'multiplicative', gamma = 0, max_rule_length = 3 , write_results_in_file=True,file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = cn2sd.fit(input_dataframe, target,binary_attributes)
            print("Selected groups :", cn2sd._get_selected_subgroups())
            print("Unselected groups :",cn2sd._get_unselected_subgroups())
            list_of_written_results = []
            file_to_read = open("./results.txt", "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [tear-production-rate = 'REDUCED'], Target: class = 'NO-CONTACT-LENSES', 0.19", list_of_written_results)
            self.assertIn("Description: [age != 'YOUNG', astigmatic = 'YES', spectacle-prescription = 'HYPERMETROPE'], Target: class = 'NO-CONTACT-LENSES', 0.12", list_of_written_results)
            self.assertIn("Description: [age = 'PRESBYOPIC', astigmatic = 'NO', spectacle-prescription = 'MYOPE'], Target: class = 'NO-CONTACT-LENSES', 0.09", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.16", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'YES', tear-production-rate = 'NORMAL'], Target: class = 'HARD-CONTACT-LENSES', 0.12", list_of_written_results)
            file_to_read.close()
'''
    def test_CN2SD_fit_method_9(self) -> None : 
                input_dataframe = pandas.read_csv("../../../../datasets/csv/lenses.csv") 
                target = ("class")
                cn2sd = CN2SD(beam_width = 3, max_rule_length= 3, weighting_scheme = 'aditive',write_results_in_file=True,file_path="./results.txt")
                binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
                result = cn2sd.fit(input_dataframe, target,binary_attributes)
                print("Selected groups :", cn2sd._get_selected_subgroups())
                print("Unselected groups :",cn2sd._get_unselected_subgroups())
                list_of_written_results = []
                file_to_read = open("./results.txt", "r")
                for [a,b] in result:
                    list_of_written_results.append(str(a) + ", " + str(b))
                self.assertIn("Description: [tear-production-rate = 'REDUCED'], Target: class = 'NO-CONTACT-LENSES', 0.19", list_of_written_results)
                self.assertIn("Description: [age = 'PRESBYOPIC'], Target: class = 'NO-CONTACT-LENSES', 0.07", list_of_written_results)
                self.assertIn("Description: [age = 'PRESBYOPIC', astigmatic = 'NO', spectacle-prescription = 'MYOPE'], Target: class = 'NO-CONTACT-LENSES', 0.02", list_of_written_results)
                self.assertIn("Description: [age = 'PRE-PRESBYOPIC', astigmatic = 'YES', spectacle-prescription = 'HYPERMETROPE'], Target: class = 'NO-CONTACT-LENSES', 0.01", list_of_written_results)
                self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.16", list_of_written_results)
                self.assertIn("Description: [astigmatic = 'YES', tear-production-rate = 'NORMAL'], Target: class = 'HARD-CONTACT-LENSES', 0.12", list_of_written_results)
                file_to_read.close()
                remove("./results.txt")
       




        

            