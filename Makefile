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
	python -m pip install build==1.2.2.post1
	python -m build

upload_to_pypi: build
	python -m pip install twine==6.0.1
	python -m twine upload --repository pypi dist/*
