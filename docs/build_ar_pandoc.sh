#!/bin/bash
# Build Arabic PDF using Pandoc (better RTL support)

cd "$(dirname "$0")"

OUTPUT="_build/pandoc-ar/HFF_Documentation_AR.pdf"
mkdir -p _build/pandoc-ar

# Combine all Arabic tutorials into one markdown file
echo "Combining Arabic tutorials..."
cat > _build/pandoc-ar/combined.md << 'HEADER'
---
title: "وثائق HFF Survey Plugin"
subtitle: "دليل المستخدم الشامل"
author: "Enzo Cocca - مؤسسة هونور فروست"
date: "يناير 2026"
lang: ar
dir: rtl
mainfont: "Arial Unicode MS"
sansfont: "Arial Unicode MS"
monofont: "Arial Unicode MS"
fontsize: 12pt
geometry: margin=2.5cm
toc: true
toc-depth: 2
header-includes:
  - \usepackage{fontspec}
  - \defaultfontfeatures{Ligatures=TeX}
  - \setmainfont[Script=Arabic]{Arial Unicode MS}
  - \setsansfont{Arial Unicode MS}
  - \setmonofont{Arial Unicode MS}
---

HEADER

# Add each tutorial
for f in tutorials/ar-lb/*.md; do
    echo "" >> _build/pandoc-ar/combined.md
    echo "\\newpage" >> _build/pandoc-ar/combined.md
    echo "" >> _build/pandoc-ar/combined.md
    cat "$f" >> _build/pandoc-ar/combined.md
done

echo "Building PDF with Pandoc..."
pandoc _build/pandoc-ar/combined.md \
    -o "$OUTPUT" \
    --pdf-engine=xelatex \
    --variable fontsize=12pt \
    --variable geometry:margin=2.5cm \
    --toc \
    --toc-depth=2 \
    -V dir=rtl \
    -V lang=ar

if [ -f "$OUTPUT" ]; then
    echo "✓ Arabic PDF created: $OUTPUT"
    open "$OUTPUT"
else
    echo "✗ Failed to create PDF"
fi
