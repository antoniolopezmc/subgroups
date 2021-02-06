import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="subgroups",
    version="0.0.1",
    author="Antonio López Martínez-Carrasco",
    author_email="antoniolopezmc1995@gmail.com",
    description="subgroups is a python library which contains a collection of subgroup discovery algorithms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antoniolopezmc/subgroups",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas>=1.1.3',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
)