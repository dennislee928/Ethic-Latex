#!/bin/bash
# Verify document generation library versions
# Usage: ./verify-deps.sh [--install]
#
# Checks latest versions of:
# - docx (Word documents)
# - xlsx (Excel spreadsheets)
# - pdf-lib (PDF generation)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Office Document Libraries Version Check ===${NC}\n"

# Expected minimum versions
DOCX_MIN="9.5.0"
XLSX_MIN="0.18.5"
PDFLIB_MIN="1.17.1"

check_version() {
  local pkg=$1
  local min=$2
  local latest

  latest=$(npm view "$pkg" version 2>/dev/null || echo "unknown")

  if [ "$latest" = "unknown" ]; then
    echo -e "${RED}✗ $pkg: Could not fetch version${NC}"
    return 1
  fi

  echo -e "${GREEN}✓ $pkg${NC}"
  echo "  Latest:  $latest"
  echo "  Minimum: $min"

  # Version comparison (simple check - assumes semver)
  if [ "$(printf '%s\n' "$min" "$latest" | sort -V | head -n1)" = "$min" ]; then
    echo -e "  Status:  ${GREEN}OK${NC}"
  else
    echo -e "  Status:  ${YELLOW}Update available${NC}"
  fi
  echo ""
}

echo -e "${YELLOW}Checking npm registry for latest versions...${NC}\n"

# Check each library
check_version "docx" "$DOCX_MIN"
check_version "xlsx" "$XLSX_MIN"
check_version "pdf-lib" "$PDFLIB_MIN"

# Optional: Check if installed in current project
if [ -f "package.json" ]; then
  echo -e "${BLUE}=== Local Installation Check ===${NC}\n"

  for pkg in docx xlsx pdf-lib; do
    installed=$(npm list "$pkg" --depth=0 2>/dev/null | grep "$pkg@" | sed 's/.*@//' || echo "not installed")
    if [ "$installed" != "not installed" ]; then
      echo -e "${GREEN}✓ $pkg@$installed installed${NC}"
    else
      echo -e "${YELLOW}○ $pkg not installed${NC}"
    fi
  done
  echo ""
fi

# Install option
if [ "$1" = "--install" ]; then
  echo -e "${BLUE}=== Installing Libraries ===${NC}\n"

  if command -v pnpm &> /dev/null; then
    echo "Using pnpm..."
    pnpm add docx xlsx pdf-lib
  elif command -v npm &> /dev/null; then
    echo "Using npm..."
    npm install docx xlsx pdf-lib
  else
    echo -e "${RED}No package manager found!${NC}"
    exit 1
  fi

  echo -e "\n${GREEN}✓ Libraries installed${NC}"
fi

echo -e "${BLUE}=== Workers Compatibility ===${NC}\n"
echo "All libraries are compatible with Cloudflare Workers:"
echo "  - docx: Pure JavaScript, no Node.js APIs"
echo "  - xlsx: Pure JavaScript (use 'xlsx' not 'xlsx-style')"
echo "  - pdf-lib: Explicitly supports Workers runtime"
echo ""
echo -e "${GREEN}Documentation:${NC}"
echo "  - docx: https://docx.js.org"
echo "  - xlsx: https://docs.sheetjs.com"
echo "  - pdf-lib: https://pdf-lib.js.org"
