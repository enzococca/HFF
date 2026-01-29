# HFF Documentation Build System

This directory contains the documentation source files for the HFF Survey Plugin.

## Prerequisites

### Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements-docs.txt
```

### LaTeX (for PDF generation)

PDF generation requires XeLaTeX with Arabic font support.

#### macOS
```bash
brew install --cask mactex
```

#### Ubuntu/Debian
```bash
sudo apt-get install texlive-xetex texlive-fonts-extra texlive-lang-arabic latexmk
```

#### Windows
Install MiKTeX from https://miktex.org/

### Arabic Fonts

For proper Arabic PDF rendering, install the Amiri font:
- Download from https://www.amirifont.org/
- Or install via package manager:
  - macOS: Included in MacTeX
  - Ubuntu: `sudo apt-get install fonts-hosny-amiri`

## Building Documentation

### Check Tools

Verify all required tools are installed:

```bash
make check-tools
```

### Build HTML (English)

```bash
make html
```

Output: `_build/html/`

### Build HTML (Arabic)

```bash
make html-ar
```

Output: `_build/html-ar/`

### Build PDF (English)

```bash
make pdf
```

Output: `_build/latex/HFF_Documentation_EN.pdf`

### Build PDF (Arabic)

```bash
make pdf-ar
```

Output: `_build/latex-ar/HFF_Documentation_AR.pdf`

### Build Both PDFs

```bash
make pdf-all
```

### Build Everything

```bash
make all
```

### Clean Build

```bash
make clean
```

## Directory Structure

```
docs/
├── _build/              # Generated output (gitignored)
├── _static/             # Static files (CSS, images)
├── _templates/          # Custom templates
├── tutorials/
│   ├── en/              # English tutorials
│   └── ar-lb/           # Arabic Lebanese tutorials
├── conf.py              # Sphinx configuration (English)
├── conf_ar.py           # Sphinx configuration (Arabic)
├── index.md             # English index
├── index_ar.md          # Arabic index
├── Makefile             # Build commands
├── requirements-docs.txt # Python dependencies
└── README.md            # This file
```

## Adding New Tutorials

1. Create the tutorial in `tutorials/en/` (English) or `tutorials/ar-lb/` (Arabic)
2. Use the established format (see existing tutorials)
3. Add the tutorial to `index.md` or `index_ar.md` toctree
4. Rebuild documentation

## Tutorial Format

Tutorials use Markdown with MyST extensions:

- Table of Contents at the top
- Horizontal dividers between sections
- Image placeholders: `![Alt](images/XX_name/01_image.png)`
- Figure captions: `*Figure N: Description*`
- Video placeholders: `> **Video Tutorial**: Description`
- Tables for fields, buttons, parameters
- Troubleshooting section at end
- Technical Notes section at end
- Version and date footer

## Troubleshooting

### LaTeX Error: Font not found

Install the Amiri font for Arabic support.

### Missing myst-parser

```bash
pip install myst-parser
```

### XeLaTeX not found

Ensure TeXLive (or MacTeX/MiKTeX) is installed and in PATH.

### Build fails on Arabic

- Check that polyglossia package is installed
- Verify Amiri font is available
- Use `xelatex` engine (not pdflatex)

### Arabic PDF has character rendering issues

For proper RTL (right-to-left) Arabic rendering, install the bidi LaTeX package:

```bash
sudo tlmgr install bidi
```

Without this package, the Arabic PDF will be generated but text will be left-to-right.

### Missing images in PDF

The tutorials include placeholder references to screenshots. Create actual screenshots
in the `tutorials/en/images/` and `tutorials/ar-lb/images/` directories to replace
the placeholder images.

## License

Documentation is released under the same license as the HFF plugin (GPLv3).

---

*HFF Survey Plugin Documentation System*
*Version 4.1.x - January 2026*
