from setuptools import setup, Command
from setuptools.command.build_py import build_py
from distutils.command.clean import clean
import shutil
import glob
import py_compile
import os

class custom_build_py(build_py):
    """Custom 'build_py' command.
    
    This version of the 'build_py' command adds only the .pyc files to the build folder, but it adds the tests .py files.
    """
    
    @staticmethod
    def _compile_all():
        # All .py files under "subgroups" directory.
        list_of_py_files = glob.glob("subgroups/**/*.py", recursive=True)
        # Iterate throughout them.
        for file in list_of_py_files:
            # Compile the .py file in the same directory and with the same name (also with .py extension).
            py_compile.compile(file, file, optimize=2)
    
    @staticmethod
    def _rename_all_py_files_to_pyc_in_the_build_directory(build_directory):
        # All .py files under "build" directory.
        final_path_for_glob = os.path.join(build_directory, "subgroups", "**", "*.py")
        list_of_py_files = glob.glob( final_path_for_glob, recursive=True)
        for file in list_of_py_files:
            os.rename(file, file+"c")
    
    def run(self):
        # First, we delete all "__pycache__" directories.
        self.run_command("clean_pycache")
        # Directory to build.
        build_directory = self.build_lib
        tests_dir_in_build_directory = os.path.join(build_directory, "subgroups", "tests")
        # Make a backup of the original directory (the directory with the .py files).
        shutil.copytree("subgroups", "subgroups_original")
        # Compile all .py files (generating .pyc files).
        # - IMPORTANT: the extension will be still .py and the original file will be overwritten.
        custom_build_py._compile_all()
        # Run the "build_py" command.
        self.compile = 0 # Force to no-compile option, no matter the specified by the user.
        super().run()
        # Delete the directory with the .pyc files.
        shutil.rmtree("subgroups")
        # Restore the original directory.
        shutil.move("subgroups_original", "subgroups")
        # Delete "tests" subdirectory located in the build directory.
        shutil.rmtree(tests_dir_in_build_directory)
        # Rename all generated .py files (which are actually the bytecodes) to .pyc.
        # - IMPORTANT: the generated files are in the build directory.
        custom_build_py._rename_all_py_files_to_pyc_in_the_build_directory(build_directory)
        # Add "tests" subdirectory to the build (because we want to include the source code of the test files).
        # - IMPORTANT: this copy must be done after renaming the .py files to .pyc.
        shutil.copytree("subgroups/tests", tests_dir_in_build_directory)

class clean_pycache(Command):
    """Command to remove all '__pycache__' directories.
    """
    
    # This command has no user options.
    user_options = []
    
    def run(self):
        # All "__pycache__" directories under ".".
        list_of_directories = glob.glob("**/__pycache__", recursive=True)
        for directory in list_of_directories:
            shutil.rmtree(directory)
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

class custom_clean_command(clean):
    """Custom 'clean' command.
    
    This version of the 'clean' command also removes the following directories: "./build", "./dist" and "./subgroups.egg-info".
    """
    
    def run(self):
        super().run()
        self.run_command("clean_pycache")
        if os.path.isdir("build"):
            shutil.rmtree("build")
        if os.path.isdir("dist"):
            shutil.rmtree("dist")
        if os.path.isdir("subgroups.egg-info"):
            shutil.rmtree("subgroups.egg-info")

# Entry point of the python script.
if __name__ == "__main__":
    # Setup function.
    setup(
        cmdclass = {
            #"build_py" : custom_build_py,
            "clean_pycache" : clean_pycache,
            "clean" : custom_clean_command
        },
    )
