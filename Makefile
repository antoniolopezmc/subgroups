.PHONY: clean_pycache clean install_prod install_dev uninstall build_for_pypi upload_to_pypi build

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

build_for_pypi: clean
	python -m pip install --upgrade build
	python -m build

upload_to_pypi: build_for_pypi
	python -m pip install --upgrade twine
	python -m twine upload --repository pypi dist/*.whl

build: build_for_pypi
