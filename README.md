# subgroups

**subgroups** is a Python library that provides a collection of subgroup discovery algorithms and other data analysis utilities.

## Installation

The source code is currently hosted on: https://github.com/antoniolopezmc/subgroups

To install the 'subgroups' library from pip, it is necessary to execute:

```sh
pip install subgroups
```

## Testing

After installing the library, a collection of tests can be launched by executing:

```python
import subgroups.tests as st
st.run_all_tests()
```

## Generate the library documentation manually

To manually generate the library documentation, it is necessary to execute:

```sh
# 1. Clone the repository.
git clone https://github.com/antoniolopezmc/subgroups.git
# 2. Go to the 'docs' subfolder.
cd subgroups/docs
# 3. Generate the documentation.
make build
```

The generated documentation will be located in the *build* subfolder.
