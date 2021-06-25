# -*- coding: utf-8 -*-

# Contributors:
#    Antonio López Martínez-Carrasco <antoniolopezmc1995@gmail.com>

"""This file contains certain functions used in the packaging process of the library.
"""

import glob
import shutil
import os
import sys

# Clean all directories and files generated during the build process, except the .whl file.
def clean_all_except_whl():
    dir_names = glob.glob('./*.egg-info')
    for elem in dir_names:
        shutil.rmtree(elem)
    file_names = glob.glob('./dist/*.tar.gz')
    for elem in file_names:
        os.remove(elem)

# Clean all directories and files generated during the build process.
def clean_all():
    dir_names = glob.glob('./*.egg-info')
    for elem in dir_names:
        shutil.rmtree(elem)
    dist_path = "./dist"
    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

# Entry point.
if __name__ == "__main__":
    # Check whether, when calling to this script, an additional argument (the name of the instruction) was passed.
    if len(sys.argv) < 2:
        raise SyntaxError("SyntaxError: Usage: python make.py <instruction_name>")
    # Execute the correponding function.
    instruction_name = sys.argv[1]
    if instruction_name == "clean_all_except_whl":
        clean_all_except_whl()
    elif instruction_name == "clean_all":
        clean_all()
    else:
        raise ValueError("Unknown instruction.")
