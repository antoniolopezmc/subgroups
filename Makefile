.PHONY: clean_pycache clean install_prod install_dev uninstall build upload_to_pypi

clean_pycache:
	python setup.py clean_pycache

clean: clean_pycache
	python setup.py clean

install_prod: clean
	python -m pip install ./

install_dev: clean
	python -m pip install -e ./

uninstall:
	python -m pip uninstall subgroups

build: clean
	python -m pip install --upgrade build
	python -m build

upload_to_pypi: build
	python -m pip install --upgrade twine
	python -m twine upload --repository pypi dist/*
