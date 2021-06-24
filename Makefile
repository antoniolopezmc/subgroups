.PHONY: build clean

build: clean
	python -m pip install --upgrade build
	python -m build
	python make.py clean_all_except_whl

clean:
	python make.py clean_all
