from sys import argv
from os import path, remove
from shutil import rmtree

# This script deletes the elements whose path is passed by parameter.
if __name__ == "__main__":
    elements_to_delete = argv[1:] # The first element in "sys.argv" is the program name.
    for elem in elements_to_delete:
        if path.isdir(elem):
            rmtree(elem)
        elif path.isfile(elem):
            remove(elem)

