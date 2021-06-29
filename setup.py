from setuptools import setup, find_packages, Command
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
            py_compile.compile(file, file) # Compile the .py file in the same directory and with the same name (also with .py extension).
    
    @staticmethod
    def _rename_all_py_files_to_pyc_in_the_build_directory(build_directory):
        # All .py files under "build" directory.
        final_path_for_glob = os.path.join(build_directory, "subgroups", "**", "*.py")
        list_of_py_files = glob.glob( final_path_for_glob, recursive=True)
        for file in list_of_py_files:
            os.rename(file, file+"c")
    
    def run(self):
        # First, we delete all "__pycache__" directories.
        self.run_command("remove_all_pycache_directories")
        # Directory to build.
        build_directory = self.build_lib
        tests_dir_in_build_directory = os.path.join(build_directory, "subgroups", "tests")
        # Make a backup of the original directory (the directory with the .py files).
        shutil.copytree("subgroups", "subgroups_original")
        # Compile all the .py files (generating .pyc files).
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

class remove_all_pycache_directories(Command):
    """Command to remove all '__pycache__' directories."""
    
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
        if os.path.isdir("build"):
            shutil.rmtree("build")
        if os.path.isdir("dist"):
            shutil.rmtree("dist")
        if os.path.isdir("subgroups.egg-info"):
            shutil.rmtree("subgroups.egg-info")

# Entry point of the python script.
if __name__ == "__main__":
    # Read the long description of the project (stored in the README.md file).
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    # Project properties.
    setup(
        name="subgroups",
        version="0.0.1",
        author="Antonio López Martínez-Carrasco",
        author_email="antoniolopezmc1995@gmail.com",
        description="subgroups is a python library which contains a collection of subgroup discovery algorithms and other data analysis utilities.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/antoniolopezmc/subgroups",
        packages=find_packages(where='.', exclude=("build*", "dist*", "docs*")),
        install_requires=[
            'pandas>=1.1.3',
            'bitarray>=1.6.1'
        ],
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.8.5',
        cmdclass = {
            "build_py" : custom_build_py,
            "remove_all_pycache_directories" : remove_all_pycache_directories,
            "clean" : custom_clean_command
        },
    )
