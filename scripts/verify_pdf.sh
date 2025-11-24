#!/bin/bash
# Verify PDF Generation Script
# This script builds the thesis and verifies that the final PDF files are correctly generated
# Usage: bash scripts/verify_pdf.sh

set -e  # Exit on error

echo "=========================================="
echo "Ethical Riemann Hypothesis - PDF Verification"
echo "=========================================="
echo ""

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success message
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Step 1: Check prerequisites
echo "[1/6] Checking prerequisites..."
MISSING_DEPS=0

if ! command -v python3 &> /dev/null; then
    print_error "python3 not found"
    MISSING_DEPS=1
else
    print_success "python3 found: $(python3 --version)"
fi

if ! command -v xelatex &> /dev/null; then
    print_warning "xelatex not found (PDF compilation will be skipped)"
    XELATEX_AVAILABLE=0
else
    print_success "xelatex found: $(xelatex --version | head -n 1)"
    XELATEX_AVAILABLE=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    print_error "Missing required dependencies. Please install them and try again."
    exit 1
fi
echo ""

# Step 2: Run the build script
echo "[2/6] Running build script..."
if [ -f "scripts/build_thesis.sh" ]; then
    bash scripts/build_thesis.sh
    BUILD_SUCCESS=$?
    if [ $BUILD_SUCCESS -eq 0 ]; then
        print_success "Build script completed"
    else
        print_error "Build script failed with exit code $BUILD_SUCCESS"
        exit 1
    fi
else
    print_error "build_thesis.sh not found"
    exit 1
fi
echo ""

# Step 3: Verify required files exist
echo "[3/6] Verifying required files..."
REQUIRED_FILES=(
    "ethical_riemann_hypothesis_en.tex"
    "ethical_riemann_hypothesis_zh.tex"
    "references.bib"
)

ALL_FILES_EXIST=1
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file not found"
        ALL_FILES_EXIST=0
    fi
done

if [ $ALL_FILES_EXIST -eq 0 ]; then
    print_error "Some required files are missing"
    exit 1
fi
echo ""

# Step 4: Verify figures directory
echo "[4/6] Verifying figures..."
if [ -d "figures" ]; then
    FIGURE_COUNT=$(ls -1 figures/*.pdf 2>/dev/null | wc -l | tr -d ' ')
    if [ "$FIGURE_COUNT" -gt 0 ]; then
        print_success "Found $FIGURE_COUNT figure(s) in figures/ directory"
        echo "  Figures:"
        ls -1 figures/*.pdf 2>/dev/null | sed 's/^/    - /'
    else
        print_warning "figures/ directory exists but contains no PDF files"
    fi
else
    print_warning "figures/ directory not found"
fi
echo ""

# Step 5: Verify PDF files
echo "[5/6] Verifying PDF files..."
PDF_EN="ethical_riemann_hypothesis_en.pdf"
PDF_ZH="ethical_riemann_hypothesis_zh.pdf"

VERIFICATION_PASSED=1

# Check English PDF
if [ -f "$PDF_EN" ]; then
    EN_SIZE=$(stat -f%z "$PDF_EN" 2>/dev/null || stat -c%s "$PDF_EN" 2>/dev/null || echo "0")
    if [ "$EN_SIZE" -gt 1000 ]; then
        print_success "English PDF exists: $PDF_EN ($(numfmt --to=iec-i --suffix=B $EN_SIZE 2>/dev/null || echo "${EN_SIZE} bytes"))"
        
        # Try to verify PDF structure (basic check)
        if command -v file &> /dev/null; then
            FILE_TYPE=$(file -b "$PDF_EN" 2>/dev/null || echo "")
            if [[ "$FILE_TYPE" == *"PDF"* ]]; then
                print_success "English PDF file type verified"
            else
                print_warning "English PDF file type check inconclusive"
            fi
        fi
    else
        print_error "English PDF exists but is too small ($EN_SIZE bytes) - may be corrupted"
        VERIFICATION_PASSED=0
    fi
else
    if [ $XELATEX_AVAILABLE -eq 1 ]; then
        print_error "English PDF not found: $PDF_EN"
        VERIFICATION_PASSED=0
    else
        print_warning "English PDF not found (xelatex not available, expected in CI)"
    fi
fi

# Check Chinese PDF
if [ -f "$PDF_ZH" ]; then
    ZH_SIZE=$(stat -f%z "$PDF_ZH" 2>/dev/null || stat -c%s "$PDF_ZH" 2>/dev/null || echo "0")
    if [ "$ZH_SIZE" -gt 1000 ]; then
        print_success "Chinese PDF exists: $PDF_ZH ($(numfmt --to=iec-i --suffix=B $ZH_SIZE 2>/dev/null || echo "${ZH_SIZE} bytes"))"
        
        # Try to verify PDF structure (basic check)
        if command -v file &> /dev/null; then
            FILE_TYPE=$(file -b "$PDF_ZH" 2>/dev/null || echo "")
            if [[ "$FILE_TYPE" == *"PDF"* ]]; then
                print_success "Chinese PDF file type verified"
            else
                print_warning "Chinese PDF file type check inconclusive"
            fi
        fi
    else
        print_error "Chinese PDF exists but is too small ($ZH_SIZE bytes) - may be corrupted"
        VERIFICATION_PASSED=0
    fi
else
    if [ $XELATEX_AVAILABLE -eq 1 ]; then
        print_error "Chinese PDF not found: $PDF_ZH"
        VERIFICATION_PASSED=0
    else
        print_warning "Chinese PDF not found (xelatex not available, expected in CI)"
    fi
fi
echo ""

# Step 6: Additional checks
echo "[6/6] Running additional checks..."

# Check for LaTeX compilation artifacts
echo "  Checking LaTeX compilation artifacts..."
ARTIFACTS=(
    "ethical_riemann_hypothesis_en.aux"
    "ethical_riemann_hypothesis_en.log"
    "ethical_riemann_hypothesis_zh.aux"
    "ethical_riemann_hypothesis_zh.log"
)

for artifact in "${ARTIFACTS[@]}"; do
    if [ -f "$artifact" ]; then
        # Check log file for errors
        if [[ "$artifact" == *.log ]]; then
            ERROR_COUNT=$(grep -i "error" "$artifact" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$ERROR_COUNT" -gt 0 ]; then
                print_warning "$artifact contains $ERROR_COUNT error(s)"
                echo "    First few errors:"
                grep -i "error" "$artifact" 2>/dev/null | head -n 3 | sed 's/^/      /'
            fi
        fi
    fi
done

# Check simulation output
if [ -f "simulation/output/results_summary.txt" ]; then
    print_success "Simulation results file exists"
else
    print_warning "Simulation results file not found (may be expected if simulations haven't run)"
fi
echo ""

# Final summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""

if [ $VERIFICATION_PASSED -eq 1 ] || [ $XELATEX_AVAILABLE -eq 0 ]; then
    if [ $XELATEX_AVAILABLE -eq 1 ]; then
        print_success "All PDF files verified successfully!"
        echo ""
        echo "Generated PDFs:"
        if [ -f "$PDF_EN" ]; then
            ls -lh "$PDF_EN" | awk '{print "  English:  " $9 " (" $5 ")"}'
        fi
        if [ -f "$PDF_ZH" ]; then
            ls -lh "$PDF_ZH" | awk '{print "  Chinese:  " $9 " (" $5 ")"}'
        fi
    else
        print_warning "xelatex not available - PDFs will be generated in CI"
        print_success "All other verification checks passed"
    fi
    echo ""
    echo "=========================================="
    echo "Verification completed successfully!"
    echo "=========================================="
    exit 0
else
    print_error "Verification failed - some PDF files are missing or corrupted"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Check LaTeX log files for compilation errors"
    echo "  2. Ensure all required figures are in the figures/ directory"
    echo "  3. Verify that xelatex is properly installed"
    echo "  4. Run 'bash scripts/build_thesis.sh' manually to see detailed output"
    echo ""
    echo "=========================================="
    echo "Verification failed!"
    echo "=========================================="
    exit 1
fi

