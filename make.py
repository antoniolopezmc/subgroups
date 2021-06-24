import glob
import shutil
import os
import sys

def clean_all_except_whl():
    dir_names = glob.glob('./*.egg-info')
    for elem in dir_names:
        shutil.rmtree(elem)
    file_names = glob.glob('./dist/*.tar.gz')
    for elem in file_names:
        os.remove(elem)

def clean_all():
    dir_names = glob.glob('./*.egg-info')
    for elem in dir_names:
        shutil.rmtree(elem)
    dist_path = "./dist"
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

# Entry point.
if __name__ == "__main__":
    function_name = sys.argv[1]
    if function_name == "clean_all_except_whl":
        clean_all_except_whl()
    elif function_name == "clean_all":
        clean_all()
    else:
        raise ValueError("Unknown instruction.")
