from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import shutil
import glob
import py_compile
import os

class custom_build_py(build_py):
    """Custom build_py command."""
    
    @staticmethod
    def _compile_all():
        # All .py files under "subgroups" directory.
        list_of_py_files = glob.glob("subgroups/**/*.py", recursive=True)
        # Iterate throughout them.
        for file in list_of_py_files:
            py_compile.compile(file, file) # Compile the .py file in the same directory and with the same name (also with .py extension).
    
    @staticmethod
    def _rename_all_py_files_to_pyc():
        # All .py files under "build" directory.
        list_of_py_files = glob.glob( "build/lib/subgroups/**/*.py", recursive=True)
        for file in list_of_py_files:
            os.rename(file, file+"c")
    
    def run(self):
        # Directory to build.
        build_directory = self.build_lib ### <===============================================================================
        # Make a backup of the original directory (the directory with the .py files).
        shutil.copytree("subgroups", "subgroups_original")
        # Compile all the .py files (generating .pyc files).
        # IMPORTANT: the extension will be still .py and the original file will be overwritten.
        custom_build_py._compile_all()
        # Run the "build_py" command.
        self.compile = 0 # Force to no-compile option, no matter the specified by the user.
        super().run()
        # Delete the directory with the .pyc files.
        shutil.rmtree("subgroups")
        # Restore the original directory.
        shutil.move("subgroups_original", "subgroups")
        # Delete "tests" subdirectory located in the build directory.
        shutil.rmtree("build/lib/subgroups/tests")
        # Rename all generated .py files (which are actually the bytecodes) to .pyc.
        # IMPORTANT: the generated files are in "build" directory.
        custom_build_py._rename_all_py_files_to_pyc()
        # Add "tests" subdirectory to the build (because we want to include the source code of the test files).
        shutil.copytree("subgroups/tests", "build/lib/subgroups/tests")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Entry point of the python script.
if __name__ == "__main__":
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
        cmdclass = {"build_py" : custom_build_py},
    )
