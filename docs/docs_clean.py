import shutil, os

def docs_clean():
    # Delete build subdirectory.
    if os.path.isdir("build"):
        shutil.rmtree("build")
    # Delete source/rst_files subdirectory.
    if os.path.isdir("source/rst_files"):
        shutil.rmtree("source/rst_files")

# Entry point of the python script.
if __name__ == "__main__":
    docs_clean()
