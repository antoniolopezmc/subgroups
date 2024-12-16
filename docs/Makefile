.PHONY: clean build_pre build_html build_man build_text build_xml build build_all

SOURCEDIR = source
BUILDDIR = build

clean:
	python clean.py $(SOURCEDIR)/project_files $(BUILDDIR)

build_pre: clean
	python -m pip install sphinx==8.1.3
	python -m pip install sphinx-rtd-theme==3.0.2
	python -m pip install sphinx-autodoc-typehints==2.5.0
	sphinx-apidoc -f -T -M -o $(SOURCEDIR)/project_files ../src/subgroups

build_html: build_pre
	sphinx-build -M html $(SOURCEDIR) $(BUILDDIR)

build_man: build_pre
	sphinx-build -M man $(SOURCEDIR) $(BUILDDIR)

build_text: build_pre
	sphinx-build -M text $(SOURCEDIR) $(BUILDDIR)

build_xml: build_pre
	sphinx-build -M xml $(SOURCEDIR) $(BUILDDIR)

build: build_html

build_all: build_html build_man build_text build_xml
