.PHONY: uninstall build clean clean_pycache upload install_prod install_dev

clean:
	python setup.py clean

uninstall: clean
	python -m pip uninstall subgroups

clean_pycache: clean
	python setup.py clean_pycache

upload_to_pypi: clean build
	python -m pip install --upgrade twine
	python -m twine upload --repository pypi dist/*.whl

build: clean
	python -m pip install --upgrade build
	python -m build

install_prod: clean
	python -m pip install ./

install_dev: clean
	python -m pip install -e ./
