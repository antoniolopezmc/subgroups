.PHONY: build clean remove_all_pycache_directories

build: clean
	python -m pip install --upgrade build
	python -m build

clean:
	python setup.py clean

remove_all_pycache_directories:
	python setup.py remove_all_pycache_directories
