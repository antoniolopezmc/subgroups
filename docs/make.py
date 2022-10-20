from subprocess import run
from sys import argv
from os import path
from shutil import rmtree

# Constants for the source directory path and for the build directory path.
SOURCEDIR = "source"
BUILDDIR = "build"

def _run_os_command(command_and_args):
    run(command_and_args, check=True, shell=True)

def clean_command():
    # Delete SOURCEDIR/project_files subdirectory.
    if path.isdir(SOURCEDIR + "/project_files"):
        rmtree(SOURCEDIR + "/project_files")
    # Delete build subdirectory.
    if path.isdir(BUILDDIR):
        rmtree(BUILDDIR)

def sphinx_build_command(M_option_value):
    # The "M_option_value" parameter cannot be an empty string.
    if not M_option_value: # If empty string.
        raise ValueError("The 'M_option_value' parameter cannot be an empty string.")
    # Run the corresponding command.
    command = "sphinx-build -M " + str(M_option_value) + " " + SOURCEDIR + " " + BUILDDIR
    _run_os_command(command)

# Entry point of the python script.
if __name__ == "__main__":
    # Get the command and the arguments.
    arguments_without_program_name = argv[1:] # The first element in "sys.argv" is the program name.
    # Parse them.
    if (len(arguments_without_program_name) >= 1):
        if (arguments_without_program_name[0] == "clean"): # clean command.
            clean_command()
        else: # sphinx-build with a value for -M option (maybe valid or maybe not).
            sphinx_build_command(arguments_without_program_name[0])
    else: # The script has been called without arguments.
        sphinx_build_command("help")
