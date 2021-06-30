.PHONY: build clean help

build: clean
	python -m pip install --upgrade sphinx
	python -m pip install --upgrade sphinx-rtd-theme
	sphinx-apidoc -f -o source/project_files ../subgroups --no-toc
	python make.py html
	python make.py latex

clean:
	python make.py clean

help:
	python make.py
