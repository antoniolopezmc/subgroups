from os.path import dirname
from pandas import read_csv, DataFrame

current_folder_path = dirname(__file__)

def load_ballons_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/ballons.csv")

def load_car_evaluation_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/car-evaluation.csv")

def load_covid_sp_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/covid-sp.csv")

def load_credit_g_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/credit-g.csv")

def load_heart_disease_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/heart-disease.csv")

def load_income_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/income.csv")

def load_lenses_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/lenses.csv")

def load_lymph_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/lymph.csv")

def load_mushroom_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/mushroom.csv")

def load_shop_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/shop.csv")

def load_sick_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/sick.csv")

def load_tic_tac_toe_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/tic-tac-toe.csv")

def load_vote_csv() -> DataFrame:
    return read_csv(current_folder_path + "/csv/vote.csv")
