#!/bin/bash

# Playwright Browser Installation Script
#
# Installs Playwright browser binaries for all supported browsers
# or specific browsers if provided as arguments.

set -e

echo "Playwright Browser Installation"
echo "================================"
echo ""

# Check if playwright is installed
if ! command -v npx &> /dev/null && ! command -v playwright &> /dev/null; then
    echo "Error: Playwright not found. Install it first:"
    echo "  npm install -D playwright"
    echo "  or"
    echo "  pip install playwright"
    exit 1
fi

# Default: install all browsers
BROWSERS="${@:-chromium firefox webkit}"

echo "Installing browsers: $BROWSERS"
echo ""

# Try npm-based playwright first
if command -v npx &> /dev/null; then
    npx playwright install $BROWSERS --with-deps
    echo ""
    echo "✅ Browsers installed via npx playwright"
# Try Python playwright
elif command -v playwright &> /dev/null; then
    playwright install $BROWSERS --with-deps
    echo ""
    echo "✅ Browsers installed via playwright CLI"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Browser storage location:"
echo "  Linux/Mac: ~/.cache/ms-playwright/"
echo "  Windows: %USERPROFILE%\\AppData\\Local\\ms-playwright\\"
echo ""
echo "Disk usage:"
du -sh ~/.cache/ms-playwright/ 2>/dev/null || echo "  (unable to calculate)"
