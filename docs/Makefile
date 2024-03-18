.PHONY: clean build_pre build_html build_latex build_man build_text build_xml build build_all

SOURCEDIR = source
BUILDDIR = build

clean:
	python clean.py $(SOURCEDIR)/project_files $(BUILDDIR)

build_pre: clean
	python -m pip install --upgrade sphinx
	python -m pip install --upgrade sphinx-rtd-theme
	python -m pip install --upgrade sphinx-autodoc-typehints
	sphinx-apidoc -f -T -o $(SOURCEDIR)/project_files ../src/subgroups

build_html: build_pre
	sphinx-build -M html $(SOURCEDIR) $(BUILDDIR)

build_latex: build_pre
	sphinx-build -M latex $(SOURCEDIR) $(BUILDDIR)
	cd $(BUILDDIR) && cd latex && pdflatex -synctex=1 -interaction=nonstopmode subgroups.tex && cd .. && cd ..

build_man: build_pre
	sphinx-build -M man $(SOURCEDIR) $(BUILDDIR)

build_text: build_pre
	sphinx-build -M text $(SOURCEDIR) $(BUILDDIR)

build_xml: build_pre
	sphinx-build -M xml $(SOURCEDIR) $(BUILDDIR)

build: build_html build_latex
	@echo

build_all: build_html build_latex build_man build_text build_xml
	@echo
