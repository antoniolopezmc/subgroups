import os
import unittest
from pandas import DataFrame
import pandas

from subgroups.algorithms.individual_subgroups.nominal_target.sd import SD

class TestSD(unittest.TestCase):

        def test_SD_fit_method_1(self) -> None : 
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/shop.csv")
            target = ("diaper", "yes")
            sd = SD(minimum_quality_measure_value= 0.57, g_parameter= 1,beam_width = 2, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["bread", "milk", "beer", "coke", "diaper"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [beer = 'yes'], Target: diaper = 'yes', 4.0", list_of_written_results)
            self.assertIn("Description: [milk = 'yes'], Target: diaper = 'yes', 2.5", list_of_written_results)
            self.assertEqual(sd._get_selected_subgroups(), 45)
            self.assertEqual(sd._get_unselected_subgroups(), 30)
            self.assertEqual(sd._get_visited_nodes(), 75)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)

        

        def test_SD_fit_method_2(self) -> None:
            input_dataframe = DataFrame({'att1': ['v3', 'v2', 'v1', 'v3', 'v4', 'v4'], 'att2': ['1', '2', '3', '3', '5', '6'], 'att3': ['B', 'A', 'A', 'B', 'A', 'B'], 'class': ['0', '1', '0', '0', '1', '1']})
            target = ("class", "1")
            sd = SD(minimum_quality_measure_value= (2/6), g_parameter= 1 ,beam_width = 2, write_results_in_file=True, file_path="./results.txt") 
            result = sd.fit(input_dataframe, target)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertEqual(sd._get_selected_subgroups(), 107)
            self.assertEqual(sd._get_unselected_subgroups(), 67)
            self.assertEqual(sd._get_visited_nodes(), 174)
            self.assertIn("Description: [att1 != 'v1', att1 != 'v3'], Target: class = '1', 3.0", list_of_written_results)
            self.assertIn("Description: [att1 != 'v3', att2 != '3'], Target: class = '1', 3.0", list_of_written_results)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)

        def test_SD_fit_method_3(self) -> None:
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/lenses.csv") 
            target = ("class", "SOFT-CONTACT-LENSES")
            sd = SD(minimum_quality_measure_value= 0, g_parameter= 1,beam_width = 3, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertEqual(sd._get_selected_subgroups(), 318)
            self.assertEqual(sd._get_unselected_subgroups(), 0)
            self.assertEqual(sd._get_visited_nodes(), 318)
            self.assertIn("Description: [age != 'PRESBYOPIC', astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 4.0", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', spectacle-prescription = 'HYPERMETROPE', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 3.0", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 2.5", list_of_written_results)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)

          
   
        def test_SD_fit_method_4(self) -> None:
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/lenses.csv") 
            target = ("class", "SOFT-CONTACT-LENSES")
            sd = SD(minimum_quality_measure_value= 0.1, g_parameter= 1,beam_width = 3, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            file_to_read = open(sd._file_path, "r")            
            list_of_written_results = []
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertEqual(sd._get_selected_subgroups(), 193)
            self.assertEqual(sd._get_unselected_subgroups(), 122)
            self.assertEqual(sd._get_visited_nodes(), 315)
            self.assertIn("Description: [age != 'PRESBYOPIC', astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 4.0", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', spectacle-prescription = 'HYPERMETROPE', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 3.0", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 2.5", list_of_written_results)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)

            
        
        def test_SD_fit_method_5(self) -> None:
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/lenses.csv") 
            target = ("class", "SOFT-CONTACT-LENSES")
            sd = SD(minimum_quality_measure_value= 0.2, g_parameter= 1,beam_width = 3, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertEqual(sd._get_selected_subgroups(), 105)
            self.assertEqual(sd._get_unselected_subgroups(), 126)
            self.assertEqual(sd._get_visited_nodes(), 231)
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 2.5", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO'], Target: class = 'SOFT-CONTACT-LENSES', 0.62", list_of_written_results)
            self.assertIn("Description: [tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.62", list_of_written_results)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)

            
        
        def test_SD_fit_method_6(self) -> None:
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/lenses.csv") 
            target = ("class", "SOFT-CONTACT-LENSES")
            sd = SD(minimum_quality_measure_value= 0, g_parameter= 5,beam_width = 3, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertEqual(sd._get_selected_subgroups(), 317)
            self.assertEqual(sd._get_unselected_subgroups(), 0)
            self.assertEqual(sd._get_visited_nodes(), 317)            
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.83", list_of_written_results)
            self.assertIn("Description: [age != 'PRESBYOPIC', astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.8", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', spectacle-prescription = 'HYPERMETROPE', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.6", list_of_written_results)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)

            
        
        def test_SD_fit_method_7(self) -> None:
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/lenses.csv") 
            target = ("class", "SOFT-CONTACT-LENSES")
            sd = SD(minimum_quality_measure_value= 0.1, g_parameter= 5,beam_width = 3, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["astigmatic", "spectacle-prescription", "tear-production-rate"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertEqual(sd._get_selected_subgroups(), 189)
            self.assertEqual(sd._get_unselected_subgroups(), 125)
            self.assertEqual(sd._get_visited_nodes(), 314)
            self.assertIn("Description: [astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.83", list_of_written_results)
            self.assertIn("Description: [age != 'PRESBYOPIC', astigmatic = 'NO', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.8", list_of_written_results)
            self.assertIn("Description: [astigmatic = 'NO', spectacle-prescription = 'HYPERMETROPE', tear-production-rate = 'NORMAL'], Target: class = 'SOFT-CONTACT-LENSES', 0.6", list_of_written_results)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)


        def test_SD_fit_method_8(self) -> None : 
            input_dataframe = pandas.read_csv("subgroups/datasets/csv/shop.csv")
            target = ("diaper", "yes")
            sd = SD(minimum_quality_measure_value= 0.57, g_parameter= 1,beam_width = 2, write_results_in_file=True, file_path="./results.txt")
            binary_attributes = ["bread", "milk", "beer", "coke", "diaper"] 
            result = sd.fit(input_dataframe, target, binary_attributes)
            list_of_written_results = []
            file_to_read = open(sd._file_path, "r")
            for [a,b] in result:
                list_of_written_results.append(str(a) + ", " + str(b))
            self.assertIn("Description: [beer = 'yes'], Target: diaper = 'yes', 4.0", list_of_written_results)
            self.assertIn("Description: [milk = 'yes'], Target: diaper = 'yes', 2.5", list_of_written_results)
            self.assertEqual(sd._get_selected_subgroups(), 45)
            self.assertEqual(sd._get_unselected_subgroups(), 30)
            self.assertEqual(sd._get_visited_nodes(), 75)
            file_to_read.close()
            if sd._file_path is not None : 
                if os.path.isfile(sd._file_path) :
                    os.remove(sd._file_path)