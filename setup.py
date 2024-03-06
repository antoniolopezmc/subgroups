from setuptools import setup, Command
from distutils.command.clean import clean
import shutil
import glob
import os

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
            "clean_pycache" : clean_pycache,
            "clean" : custom_clean_command
        },
    )
