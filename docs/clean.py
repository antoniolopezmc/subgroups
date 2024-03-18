from sys import argv, stderr
from os import path, remove
from shutil import rmtree

# The parameters passed to the program are the elements to delete.
if __name__ == "__main__":
    # Get the list of elements to delete.
    elements_to_delete = argv[1:] # The first element in "sys.argv" is the program name.
    for elem in elements_to_delete:
        if path.isdir(elem):
            rmtree(elem)
        elif path.isfile(elem):
            remove(elem)

