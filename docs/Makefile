# Makefile for Sphinx documentation
# HFF Survey Plugin

# You can set these variables from the command line
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Default target
.PHONY: help
help:
	@echo "HFF Documentation Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  html       Build HTML documentation (English)"
	@echo "  html-ar    Build HTML documentation (Arabic)"
	@echo "  pdf        Build PDF documentation (English)"
	@echo "  pdf-ar     Build PDF documentation (Arabic)"
	@echo "  pdf-all    Build both English and Arabic PDFs"
	@echo "  clean      Remove build directory"
	@echo ""

# English documentation
.PHONY: html
html:
	@echo "Building English HTML documentation..."
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo "HTML documentation built in $(BUILDDIR)/html"

.PHONY: pdf
pdf: latexpdf
	@echo "English PDF created at $(BUILDDIR)/latex/HFF_Documentation_EN.pdf"

.PHONY: latexpdf
latexpdf:
	@echo "Building English PDF documentation..."
	$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS)
	@echo "Running LaTeX..."
	cd "$(BUILDDIR)/latex" && latexmk -f -pdf -xelatex -interaction=nonstopmode HFF_Documentation_EN.tex || echo "Note: PDF built with warnings"
	@echo "English PDF documentation built"

# Arabic documentation (uses conf_ar.py)
.PHONY: html-ar
html-ar:
	@echo "Building Arabic HTML documentation..."
	$(SPHINXBUILD) -b html -c . "$(SOURCEDIR)" "$(BUILDDIR)/html-ar" -D master_doc=index_ar -D language=ar $(SPHINXOPTS)
	@echo "Arabic HTML documentation built in $(BUILDDIR)/html-ar"

.PHONY: pdf-ar
pdf-ar: latexpdf-ar
	@echo "Arabic PDF created at $(BUILDDIR)/latex-ar/HFF_Documentation_AR.pdf"

.PHONY: latexpdf-ar
latexpdf-ar:
	@echo "Building Arabic PDF documentation..."
	@echo "Note: For proper RTL support, install bidi package: sudo tlmgr install bidi"
	$(SPHINXBUILD) -b latex -c . "$(SOURCEDIR)" "$(BUILDDIR)/latex-ar" -D master_doc=index_ar $(SPHINXOPTS)
	@echo "Running XeLaTeX for Arabic..."
	cd "$(BUILDDIR)/latex-ar" && latexmk -f -pdf -xelatex -interaction=nonstopmode HFF_Documentation_AR.tex || echo "Note: Arabic PDF requires XeLaTeX and Amiri font"
	@echo "Arabic PDF documentation built"

# Build both PDFs
.PHONY: pdf-all
pdf-all: pdf pdf-ar
	@echo ""
	@echo "====================================="
	@echo "Both PDF documents have been created:"
	@echo "  English: $(BUILDDIR)/latex/HFF_Documentation_EN.pdf"
	@echo "  Arabic:  $(BUILDDIR)/latex-ar/HFF_Documentation_AR.pdf"
	@echo "====================================="

# Clean build directory
.PHONY: clean
clean:
	rm -rf $(BUILDDIR)
	@echo "Build directory cleaned"

# Install dependencies
.PHONY: install-deps
install-deps:
	pip install -r requirements-docs.txt
	@echo "Dependencies installed"

# Check for required tools
.PHONY: check-tools
check-tools:
	@echo "Checking for required tools..."
	@which sphinx-build > /dev/null || (echo "ERROR: sphinx-build not found" && exit 1)
	@which xelatex > /dev/null || (echo "ERROR: xelatex not found (install texlive-xetex)" && exit 1)
	@which latexmk > /dev/null || (echo "ERROR: latexmk not found" && exit 1)
	@echo "All required tools found"

# Build everything
.PHONY: all
all: check-tools html html-ar pdf-all
	@echo "All documentation built successfully"
