#!/bin/bash
# Convert markdown documentation to PDF

set -e

echo "=== Documentation to PDF Converter ==="
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "⚠️  Pandoc not installed!"
    echo ""
    echo "Install with:"
    echo "  sudo apt-get install pandoc texlive-xetex"
    echo ""
    echo "Or view the markdown files directly:"
    echo "  - COMPLETE_BUILD_GUIDE.md (main guide)"
    echo "  - README.md"
    echo "  - QUICKSTART.md"
    echo "  - walkthrough.md (in .gemini directory)"
    exit 1
fi

echo "Converting documentation to PDF..."
echo ""

# Convert main build guide
if [ -f "COMPLETE_BUILD_GUIDE.md" ]; then
    echo "1. Converting COMPLETE_BUILD_GUIDE.md..."
    pandoc COMPLETE_BUILD_GUIDE.md \
        -o COMPLETE_BUILD_GUIDE.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=1in \
        --toc \
        --toc-depth=3
    echo "   ✓ Created COMPLETE_BUILD_GUIDE.pdf"
fi

# Convert README
if [ -f "README.md" ]; then
    echo "2. Converting README.md..."
    pandoc README.md \
        -o README.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=1in
    echo "   ✓ Created README.pdf"
fi

# Convert QUICKSTART
if [ -f "QUICKSTART.md" ]; then
    echo "3. Converting QUICKSTART.md..."
    pandoc QUICKSTART.md \
        -o QUICKSTART.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=1in \
        --toc
    echo "   ✓ Created QUICKSTART.pdf"
fi

echo ""
echo "=== PDF Generation Complete ==="
echo ""
echo "Generated files:"
ls -lh *.pdf 2>/dev/null || echo "  (run script to generate PDFs)"
echo ""
echo "📖 To view:"
echo "  evince COMPLETE_BUILD_GUIDE.pdf"
echo "  # or your favorite PDF viewer"
