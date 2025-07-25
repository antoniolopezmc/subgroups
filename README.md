<p align="center"><img alt="subgroups logo" src="https://github.com/antoniolopezmc/subgroups/blob/master/docs/source/images/logo_small.png?raw=true"></p>

-----------------

# subgroups - A Python library for Subgroup Discovery

|               |   |
|---------------|---|
| **Tests** | [![Azure Pipelines - Tests](https://dev.azure.com/conda-forge/feedstock-builds/_apis/build/status/subgroups-feedstock?branchName=main)](https://dev.azure.com/conda-forge/feedstock-builds/_build/latest?definitionId=21954&branchName=main) |
| **Package** | [![PyPI - Version](https://img.shields.io/pypi/v/subgroups?label=PyPI)](https://pypi.org/project/subgroups/) [![Conda Version](https://img.shields.io/conda/vn/conda-forge/subgroups?label=Anaconda.org%20%7C%20conda-forge)](https://anaconda.org/conda-forge/subgroups)|
| **Metadata** | [![GitHub](https://img.shields.io/badge/GitHub-Latest%20development-blue?style=flat)](https://github.com/antoniolopezmc/subgroups) [![Author's webpage](https://img.shields.io/badge/Author's%20webpage-orange?style=flat)](https://webs.um.es/antoniolopezmc/) [![Python Version](https://img.shields.io/pypi/pyversions/subgroups)](https://www.python.org/) [![License](https://img.shields.io/pypi/l/subgroups?color=green)](https://github.com/antoniolopezmc/subgroups/blob/master/LICENSE) ![Total Downloads](https://img.shields.io/pepy/dt/subgroups) [![Documentation](https://img.shields.io/badge/Documentation-green?style=flat)](https://www.um.es/subgroups/)|

## What is it?

`subgroups` is a public, accessible and open-source python library created to work with the Subgroup Discovery (SD) technique. This library implements the necessary components related to the SD technique and contains a collection of SD algorithms and other data analysis utilities.

## Quick install

The easiest way to obtain this library is from either [PyPI](https://pypi.org/) (the Python Package Index) or [Conda](https://docs.conda.io/).

### PyPI

For that, you can [view and download the package from its PyPI page](https://pypi.org/project/subgroups/) or directly install it by executing:

```shell
pip install subgroups
```

### Conda

For that, you can [view and download the package from its Anaconda.org page (conda-forge channel)](https://anaconda.org/conda-forge/subgroups) or directly install it by executing:

```shell
conda install -c conda-forge subgroups
```

## Testing

After installing the library, a collection of tests can be launched by executing:

```python
import subgroups.tests as st
st.run_all_tests()
```

These tests verify that the library is correctly installed and that all components, algorithms and features are properly working.

## Installing from source

The source code (latest development) is currently hosted on: https://github.com/antoniolopezmc/subgroups

Therefore, you need first to clone the repository:

```shell
git clone https://github.com/antoniolopezmc/subgroups.git
cd subgroups
```

After that, the library can be installed in *production mode* or in *develop mode*.

### Production mode

```shell
make install_prod
```

or

```shell
python -m pip install ./
```

or

```shell
pip install ./
```

This mode installs the library as normal, copying it to the standard Python site-packages directory.

### Develop mode

```shell
make install_dev
```

or

```shell
python -m pip install -e ./
```

or

```shell
pip install -e ./
```

This mode installs the library in editable mode, creating a link in the standard Python site-packages directory to the downloaded project directory (the current directory). See the [pip_install documentation](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e) for further details.

## Example of use of the algorithms

An example of use of each algorithm implemented in `subgroups` python library can be found in the `examples/algorithms` folder:

- [SDMap](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/SDMap.ipynb)
- [SDMap*](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/SDMapStar.ipynb)
- [VLSD](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/VLSD.ipynb)
- [BSD-CBSD-CPBSD](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/BSD-CBSD-CPBSD.ipynb)
- [QFinder](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/QFinder.ipynb)
- [IDSD](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/IDSD.ipynb)
- [GMSL](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/GMSL.ipynb)
- [DSLM](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/DSLM.ipynb)
- [SDIGA](https://github.com/antoniolopezmc/subgroups/blob/master/examples/algorithms/SDIGA.ipynb)

## Documentation

The official documentation is hosted on https://www.um.es/subgroups/

Additionally, the source code of the project contains a folder called `docs`, which includes the documentation of the library. This documentation can be also manually generated by executing:

```shell
cd docs
make build
```

or

```shell
cd docs
python clean.py source/project_files build
python -m pip install sphinx==8.1.3
python -m pip install sphinx-rtd-theme==3.0.2
python -m pip install sphinx-autodoc-typehints==2.5.0
sphinx-apidoc -f -T -M -o source/project_files ../src/subgroups
sphinx-build -M html source build
```

The generated documentation will be located in the `build` subfolder.

## Citation

If you use `subgroups` library in a scientific publication, please cite the following paper:

- BibTeX format:

```
@article{LOPEZMARTINEZCARRASCO2024101895,
title = {Subgroups: A Python library for Subgroup Discovery},
journal = {SoftwareX},
volume = {28},
pages = {101895},
year = {2024},
issn = {2352-7110},
doi = {https://doi.org/10.1016/j.softx.2024.101895},
url = {https://www.sciencedirect.com/science/article/pii/S2352711024002656},
author = {Antonio Lopez-Martinez-Carrasco and Jose M. Juarez and Manuel Campos and Francisco Mora-Caselles},
keywords = {Machine learning, Data mining, Subgroup Discovery, Python}
}
```

- RIS format:

```
TY  - JOUR
T1  - Subgroups: A Python library for Subgroup Discovery
AU  - Lopez-Martinez-Carrasco, Antonio
AU  - Juarez, Jose M.
AU  - Campos, Manuel
AU  - Mora-Caselles, Francisco
JO  - SoftwareX
VL  - 28
SP  - 101895
PY  - 2024
DA  - 2024/12/01/
SN  - 2352-7110
DO  - https://doi.org/10.1016/j.softx.2024.101895
UR  - https://www.sciencedirect.com/science/article/pii/S2352711024002656
KW  - Machine learning
KW  - Data mining
KW  - Subgroup Discovery
KW  - Python
ER  - 
```

- Plain text:

```
Antonio Lopez-Martinez-Carrasco, Jose M. Juarez, Manuel Campos, Francisco Mora-Caselles,
Subgroups: A Python library for Subgroup Discovery,
SoftwareX,
Volume 28,
2024,
101895,
ISSN 2352-7110,
https://doi.org/10.1016/j.softx.2024.101895.
(https://www.sciencedirect.com/science/article/pii/S2352711024002656)
Keywords: Machine learning; Data mining; Subgroup Discovery; Python
```
