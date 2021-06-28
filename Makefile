.PHONY: build clean remove_all_pycache_directories docs_build docs_clean

build: clean
	python -m pip install --upgrade build
	python -m build

clean:
	python setup.py clean

remove_all_pycache_directories:
	python setup.py remove_all_pycache_directories

docs_build: docs_clean
	python -m pip install --upgrade sphinx
	python -m pip install --upgrade sphinx-rtd-theme
	sphinx-apidoc -f -o docs/source/rst_files subgroups --no-toc
	make html --directory=docs
	make latex --directory=docs

docs_clean:
	make clean --directory=docs
