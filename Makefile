.PHONY: build clean clean_pycache upload

build: clean
	python -m pip install --upgrade build
	python -m build

clean:
	python setup.py clean

clean_pycache:
	python setup.py clean_pycache

upload: clean build
	python -m pip install --upgrade twine
	python -m twine upload --repository pypi dist/*.whl
