.PHONY: clean build extended_build

clean:
	python make.py clean

build: clean
	python -m pip install --upgrade sphinx
	python -m pip install --upgrade sphinx-rtd-theme
	python -m pip install --upgrade sphinx-autodoc-typehints
	sphinx-apidoc -f -o source/project_files ../src/subgroups --no-toc
	python make.py html
	python make.py latex
	cd build && cd latex && pdflatex -synctex=1 -interaction=nonstopmode subgroups.tex && cd .. && cd ..

extended_build: build
	python make.py man
	python make.py text
	python make.py xml
